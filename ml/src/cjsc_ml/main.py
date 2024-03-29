import json
from datetime import datetime
from os import getenv

import redis
import requests
from cjsc_ml.clickhouse import ClickHouse
from cjsc_ml.config import Config
from cjsc_ml.models import Chat, Corrector, Retriever
from clickhouse_driver import Client
from loguru import logger
from pydantic import BaseModel
from transformers import (
    AutoModel,
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    GenerationConfig,
    M2M100ForConditionalGeneration,
    M2M100Tokenizer,
)


# Pydantic models
class Message(BaseModel):  # Same as backend
    id: int | None = None
    from_user_id: int
    to_user_id: int
    is_read: bool = False
    content: str
    created_at: datetime = datetime.now()


class MessageRequestConfig(BaseModel):
    allow_faq: bool


class MessageRequest(BaseModel):
    message: Message
    config: MessageRequestConfig


def pop_from_queue(redis_conn):
    item = redis_conn.rpop("requests")
    return item


def push_to_queue(redis_conn, item):
    redis_conn.lpush("requests", item)


def run():
    config = Config()

    generation_config = GenerationConfig.from_pretrained(config.llm)
    generation_config.num_beams = config.num_beams
    generation_config.seed = config.random_state
    generation_config.max_length = config.max_length

    embedding_model = AutoModel.from_pretrained(config.retriever)
    embedding_tokenizer = AutoTokenizer.from_pretrained(config.retriever)

    client = Client(host="CHANGEME", port=39000, password="CHANGEME")
    clickhouse = ClickHouse(client)

    document_retriever = Retriever(
        embedding_model,
        embedding_tokenizer,
        clickhouse=clickhouse,
        batch_size=16,
        mode="documents",
    )

    faq_retriever = Retriever(
        embedding_model,
        embedding_tokenizer,
        clickhouse=clickhouse,
        batch_size=16,
        mode="faq",
    )

    corrector_model = M2M100ForConditionalGeneration.from_pretrained(config.corrector)
    corrector_tokenizer = M2M100Tokenizer.from_pretrained(
        config.corrector, src_lang="ru", tgt_lang="ru"
    )

    corrector = Corrector(corrector_model, corrector_tokenizer)

    generation_tokenizer = AutoTokenizer.from_pretrained(config.llm)
    generation_model = AutoModelForSeq2SeqLM.from_pretrained(config.llm)

    chat = Chat(
        generation_model,
        generation_tokenizer,
        generation_config,
        document_retriever=document_retriever,
        faq_retriever=faq_retriever,
        corrector=corrector,
        device=config.device,
        confidence_threshold=0.8,
        k=3,
    )

    redis_conn = redis.Redis(host="localhost", port=6379, db=0)

    while True:
        res = pop_from_queue(redis_conn)

        if res:
            request = json.loads(res.decode("utf-8"))  # MessageRequest
            """
            payload: dict = {
                "message": {"id": int, "content": str},
                "config": {"allow_faq": bool}
                }
            """

            # id = request["message"]["id"]
            from_user_id = request["message"]["to_user_id"]
            to_user_id = request["message"]["from_user_id"]
            allow_faq = request["config"]["allow_faq"]
            message_content = request["message"]["content"]

            """
            payload: dict = {
                                "message": {"id": int, },
                                "response": {"content": str}
                            }
            """

            response_text = chat.answer(message_content, allow_faq=allow_faq)

            message = Message(
                from_user_id=from_user_id,
                to_user_id=to_user_id,
                message_content=response_text,
            )

            r = requests.post(
                "http://127.0.0.1:8080/msg/send",
                json=message.model_dump(exclude_unset=True),
                params={"ca_secret": getenv("CJSC_CROSS_APP_SECRET")},
            )

            logger.debug(f"Sent message to backend: {r.status_code=} {r.json()=}")


if __name__ == "__main__":
    run()
