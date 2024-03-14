import os
import random

from joblib import dump, load
from tqdm.auto import tqdm

tqdm.pandas()
import re

import numpy as np
import pandas as pd
import scipy
import sklearn
import torch
import torch.nn.functional as F
from datasets import Dataset
from torch import nn
from torch.utils.data import DataLoader
from transformers import (
    AutoModel,
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    GenerationConfig,
    M2M100ForConditionalGeneration,
    M2M100Tokenizer,
)

from cjsc_ml.clickhouse import ClickHouse


class DistilledModel(nn.Module):
    def __init__(self, model, latent_size: int = 64):
        super().__init__()
        self.model = model
        self.latent_size = latent_size

        self.latent = nn.Linear(768, self.latent_size)
        self.out = nn.Linear(self.latent_size, 768)

    def forward(self, input_ids, attention_mask, return_latent: bool = False):
        x = self.model(input_ids, attention_mask).last_hidden_state
        latent = self.latent(x)[:, 0]

        if return_latent:
            return latent

        out = self.out(latent)
        return out


class Retriever:
    def __init__(
        self,
        model: AutoModel,
        tokenizer: AutoTokenizer,
        clickhouse: ClickHouse,
        # d: int,
        # k: int,
        batch_size: int = 1,
        device: str = "cuda",
        mode: str = "documents",
    ):
        super().__init__()
        self.device = device

        self.model = model
        self.model.eval()
        self.model.to(self.device)
        self.tokenizer = tokenizer

        self.clickhouse = clickhouse

        self.batch_size = batch_size

        self.mode = mode

        # self.d = d
        # self.index = faiss.IndexFlatIP(d)

    def add(self, df, return_embeddings: bool = False):
        """
        Сюда приходит csv с новыми записями
        """

        dataset = Dataset.from_pandas(df)
        dataset = self._preprocess_dataset(dataset)
        dataset.set_format(type="torch", columns=["input_ids", "attention_mask"])
        dataloader = DataLoader(dataset, batch_size=self.batch_size, shuffle=False)

        embeddings = []

        for batch in tqdm(dataloader):
            input_ids, attention_masks = batch["input_ids"].squeeze(dim=1), batch[
                "attention_mask"
            ].squeeze(dim=1)
            input_ids, attention_masks = input_ids.to(self.device), attention_masks.to(
                self.device
            )

            with torch.no_grad():
                # print(input_ids.shape, attention_masks.shape)
                output = F.normalize(
                    self.model(
                        input_ids=input_ids,
                        attention_mask=attention_masks,
                        # return_latent=True
                    ).pooler_output
                )

            embeddings.append(output.cpu())

        embeddings = torch.cat(embeddings, dim=0).to(torch.float32).numpy()

        # self.index.add(embeddings)
        torch.cuda.empty_cache()

        self.clickhouse.add(df, embeddings, table=self.mode)

        if return_embeddings:
            return embeddings

    def get_indexer_size(self) -> int:
        return self.index.ntotal

    # def save_index(self, path: str = "/data/index.bin"):
    #     faiss.write_index(self.index, path)

    # def load_index(self, path: str = "/data/index.bin"):
    #     self.index = faiss.read_index(path)

    def _preprocess_dataset(self, dataset):
        if self.mode == "documents":
            dataset = dataset.map(
                lambda sample: self.tokenizer(
                    f"{sample['topic']} {self.tokenizer.sep_token} {sample['title']} {self.tokenizer.sep_token} {sample['text']}",
                    truncation=True,
                    padding="max_length",
                    max_length=512,
                ),
                batched=False,
                batch_size=self.batch_size,
            )

        elif self.mode == "faq":
            dataset = dataset.map(
                lambda sample: self.tokenizer(
                    f"{sample['question']}",
                    truncation=True,
                    padding="max_length",
                    max_length=512,
                ),
                batched=False,
                batch_size=self.batch_size,
            )
        else:
            dataset = dataset.map(
                lambda sample: self.tokenizer(
                    f"{sample['sentence']}",
                    truncation=True,
                    padding="max_length",
                    max_length=512,
                ),
                batched=False,
                batch_size=self.batch_size,
            )

        return dataset

    def _get_embedding(self, sample):
        input_ids = sample["input_ids"]
        if len(input_ids.shape) < 2:
            input_ids.unsqueeze(dim=0)

        attention_mask = sample["attention_mask"]
        if len(attention_mask.shape) < 2:
            input_ids.unsqueeze(dim=0)

        with torch.no_grad():
            return (
                F.normalize(
                    self.model(
                        input_ids.to(self.device),
                        attention_mask.to(self.device),
                        # return_latent=True
                    ).pooler_output
                )
                .to(torch.float32)
                .cpu()
                .numpy()
            )

    def query(self, text, k):
        sample = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=512,
            return_tensors="pt",
        )
        embedding = self._get_embedding(sample)

        torch.cuda.empty_cache()

        return self.clickhouse.retrieve(embedding, table=self.mode, k=k)

    def __len__(self):
        return self.clickhouse.get_num_samples(self.mode)


class Corrector:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

    def __call__(self, sentence: str):
        encodings = self.tokenizer(sentence, return_tensors="pt")
        generated_tokens = self.model.generate(
            **encodings, forced_bos_token_id=self.tokenizer.get_lang_id("ru")
        )
        return self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)


class Chat:
    def __init__(
        self,
        model,
        tokenizer,
        generation_config,
        document_retriever,
        faq_retriever,
        corrector,
        k: int = 3,
        confidence_threshold: float = 0.9,
        device: str = "cuda",
    ):
        self.device = device

        self.model = model
        self.model.eval()
        self.model.to(self.device)
        self.tokenizer = tokenizer
        self.generation_config = generation_config

        self.document_retriever = document_retriever
        self.faq_retriever = faq_retriever
        self.corrector = corrector

        self.k = k
        self.confidence_threshold = confidence_threshold

    @staticmethod
    def _form_prompt(text, retrieved):
        texts = retrieved["text"].tolist()

        prompt = "<SC6>Текст: " + "\n".join(texts) + f"\nВопрос: {text}"

        return prompt

    def generate(self, prompt):
        data = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        try:
            output_ids = self.model.generate(
                **data,
                generation_config=self.generation_config,
            )[0]
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            return None

        torch.cuda.empty_cache()

        out = self.tokenizer.decode(output_ids.tolist(), skip_special_tokens=True)
        return out

    def postprocess(self, generated):
        generated = generated.strip()[len("<extra_id_0>") :].strip()
        # if "Ответ: " in generated:
        #     generated = generated.split("Ответ: ")[1]
        #     if "Вопрос: " in generated:
        #         return generated.split("Вопрос: ")[0]
        #     return generated
        # # else:
        # #     return generated
        return generated

    def filter_by_confidence(self, df):
        return df[df["cos"] >= self.confidence_threshold]

    def form_output_gen(self, generated, df):
        return (
            "LLM:\n\n"
            + f"{self.postprocess(generated)}"
            + "\n\n"
            + "На основе документов:\n"
            + "\n".join(
                [
                    f"{el[0]} {el[1]}"
                    for el in zip(df["url"].tolist(), df["date"].tolist())
                ]
            )
        )

    def form_output_faq(self, df):
        return "FAQ:\n\n" + "\n".join(
            [f"Ответ {i}\n{el.strip()}" for i, el in enumerate(df["answer"].tolist())]
        )

    def answer(self, message, allow_faq: bool = True):
        message = self.corrector(message)

        if allow_faq:
            faq_df = self.faq_retriever.query(message, k=self.k)
            faq_df = self.filter_by_confidence(faq_df)

            if faq_df.shape[0] > 0:
                return self.form_output_faq(faq_df)

        document_df = self.document_retriever.query(message, k=self.k)
        # print(document_df)
        prompt = self._form_prompt(message, document_df)
        generated = self.generate(prompt)

        return self.form_output_gen(generated, document_df)
