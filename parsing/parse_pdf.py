import fitz  # PyMuPDF


def extract_title_and_text(pdf_path):
    with fitz.open(pdf_path) as doc:
        first_page = doc[12]

        # Извлекаем блоки с информацией о тексте, включая размер шрифта
        blocks = first_page.get_text("dict")["blocks"]

        # Фильтруем только текстовые блоки (игнорируем изображения)
        text_blocks = [b for b in blocks if b["type"] == 0]

        # Находим блок с наибольшим размером шрифта
        max_font_size = 0
        title_block = None
        for block in text_blocks:
            for line in block["lines"]:
                for span in line["spans"]:
                    if span["size"] > max_font_size:
                        max_font_size = span["size"]
                        title_block = block

        # Считаем заголовок текстом блока с наибольшим размером шрифта
        title = "\n".join(
            [
                " ".join([span["text"] for span in line["spans"]])
                for line in title_block["lines"]
            ]
        )

        # Собираем весь текст документа для примера
        full_text = "\n".join(
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

        return title, full_text


# Путь к вашему PDF файлу
pdf_path = "ar_2022.pdf"
title, text = extract_title_and_text(pdf_path)

print("Заголовок:", title)
print("Текст:", text)
