import re

import fitz  # PyMuPDF
import pandas as pd


def clean_title(title):
    # Удаляем числа в начале и в конце строки заголовка
    title = re.sub(r"^\d+\s+", "", title)
    title = re.sub(r"\s+\d+\s*$", "", title)
    return title.strip()


def extract_documents(pdf_path):
    with fitz.open(pdf_path) as doc:
        documents = []
        current_document = {"title": None, "text": ""}

        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            text_blocks = [b for b in blocks if b["type"] == 0]

            max_font_size = 0
            title_block = None
            for block in text_blocks:
                for line in block["lines"]:
                    for span in line["spans"]:
                        if span["size"] > max_font_size:
                            max_font_size = span["size"]
                            title_block = block

            # Извлекаем и очищаем заголовок
            title_text = ""
            if title_block:
                title_text = "\n".join(
                    [
                        " ".join([span["text"] for span in line["spans"]])
                        for line in title_block["lines"]
                    ]
                )
                title_text = clean_title(title_text)

            page_text = "\n".join(
                [
                    "\n".join(
                        [
                            " ".join([span["text"] for span in line["spans"]])
                            for line in block["lines"]
                        ]
                    )
                    for block in text_blocks
                ]
            )

            # Обрабатываем заголовки и тексты
            if title_text:
                # Если это новый документ, добавляем предыдущий в список и начинаем новый
                if current_document["title"] != title_text:
                    if current_document["title"] is not None:
                        documents.append(current_document)
                    current_document = {"title": title_text, "text": page_text}
                # Если это продолжение предыдущего документа, добавляем текст к нему
                else:
                    current_document["text"] += "\n" + page_text
            else:
                # Если заголовок не найден, добавляем текст к текущему документу
                current_document["text"] += "\n" + page_text

        # Добавляем последний документ
        if current_document["title"] or current_document["text"]:
            documents.append(current_document)

        return documents


def save_documents_to_csv(documents, csv_path):
    df = pd.DataFrame(documents)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")


# Путь к вашему PDF файлу
pdf_path = "ar_2022.pdf"
# Путь для сохранения CSV файла
csv_path = "output.csv"

documents = extract_documents(pdf_path)
save_documents_to_csv(documents, csv_path)

print(f"Данные сохранены в {csv_path}")
