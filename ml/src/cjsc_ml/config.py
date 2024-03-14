from dataclasses import dataclass


@dataclass
class Config:
    # Model
    # retriever = "deepvk/deberta-v1-distill"
    retriever = "Tochka-AI/ruRoPEBert-e5-base-2k"
    llm = "Den4ikAI/FRED-T5-LARGE_text_qa"
    corrector = "ai-forever/RuM2M100-418M"
    num_beams = 3
    max_length = 128

    device = "cuda"
    random_state = 42
