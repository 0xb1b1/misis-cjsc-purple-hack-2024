Классы:

clickhouse.py

Класс дистиллированной модели: является оберткой над другими моделями для того чтоб проводить дистилляцию модели и одновременно сжимать ее аутпут до latent_size'a
```
DistilledModel(
    model, 
    latent_size: int = 64
)
```


models.py

Класс Retriever осуществляет получения эмбеддинга от запросов юзера а так же эмбеддингов из предоставледдынх датасетов. Также записыывает датасеты в ClickHouse и достает самые похожие семплы из ClickHouse
```
Retriever(
	model: AutoModel,
    tokenizer: AutoTokenizer,
    clickhouse: ClickHouse,
    batch_size: int = 1,
    device: str = "cuda",
    mode: str = "documents",
)

Retriever.add

Retriever._preprocess_dataset # 

Retriever._get_embedding Извлекает эмбеддинг из текста

Retriever.query Ищет ближайший вектор в ClickHouse

Retriever.__len__ возвращает размер датасета по которому делает поиск
```

Классс для исправления ошибок пользователей
```
Corrector(
    model, 
    tokenizer
)
```

Класс Chat является основным классом который:
1. Принимает запросы юзеров
2. Правит ошибки и опечатки
3. Ищет ответ в FAQ
4. Если не находит, то генерирует ответ при помощи LLM

```
Chat(
    model,
    tokenizer,
    generation_config,
    document_retriever,
    faq_retriever,
    corrector,
    k: int = 3,
    confidence_threshold: float = 0.9,
    device: str = "cuda",
)

generate - генерация ответа LLM
```




Ноутбуки:

distillation.ipynb - Код с дистилляцией модели ретривера

retriever.ipynb - Полный пайплайн RAG в Ноутбуке