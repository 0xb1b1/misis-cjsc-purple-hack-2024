import json

from clickhouse_driver import Client


class ClickHouse:
    def __init__(self, client):
        self.client = client

    def preprocess_faq_df(self, faq_df, embeddings):
        faq_df["embedding"] = (embeddings).tolist()
        faq_df.to_json("faq+embeddings.json")

        file_path = "faq+embeddings.json"
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        ids = data["id"]
        topics = data["topic"]
        questions = data["question"]
        answers = data["answer"]
        embeddings = data["embedding"]

        rows_to_insert = []
        for i in range(len(ids)):
            i_str = str(i)

            row = {
                "id": ids[i_str],
                "topic": topics[i_str],
                "question": questions[i_str],
                "answer": answers[i_str],
                "embedding": embeddings[i_str],
            }
            rows_to_insert.append(row)

        return rows_to_insert

    def preprocess_documents_df(self, documents_df, embeddings):
        documents_df["date"] = pd.to_datetime(documents_df["date"], format="%d.%m.%Y")
        documents_df["id"] = [k for k in range(0, documents_df.shape[0])]
        documents_df["embedding"] = embeddings.tolist()
        # print(documents_df['embedding'])

        documents_df.to_json("documents+embeddings.json")

        file_path = "documents+embeddings.json"

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        ids = data["id"]
        texts = data["text"]
        titles = data["title"]
        topics = data["topic"]
        urls = data["url"]
        dates = list(documents_df["date"])
        embeddings = data["embedding"]

        rows_to_insert = []
        for i in range(len(ids)):
            i_str = str(i)

            row = {
                "id": ids[i_str],
                "text": texts[i_str],
                "topic": topics[i_str],
                "title": titles[i_str],
                "url": urls[i_str],
                "date": dates[i],
                "embedding": embeddings[i_str],
            }
            rows_to_insert.append(row)

        return rows_to_insert

    def add(self, df, embeddings, table: str):
        if table == "faq":
            insert_info = self.preprocess_faq_df(df, embeddings)
            self.client.execute(
                "INSERT INTO faq (id, topic, question, answer, embedding) VALUES",
                insert_info,
            )
        elif table == "documents":
            insert_info = self.preprocess_documents_df(df, embeddings)
            client.execute(
                "INSERT INTO documents (id, text, topic, title, url, date, embedding) VALUES",
                insert_info,
            )
        else:
            raise ValueError("table should be in ['faq', 'documents']")

    def _post_process_texts(self, samples):
        samples = list(map(list, samples))

        for i in range(len(samples)):
            samples[i][0] = samples[i][0].replace("\xa0", " ").strip()

        return samples

    def _click_to_pd_faq(self, click_out):
        df = pd.DataFrame(columns=["text", "cos"], data=click_out)
        return df

    def _click_to_pd_documents(self, click_out):
        df = pd.DataFrame(columns=["text", "date", "url", "cos"], data=click_out)
        return df

    def retrieve(self, embedding, table: str, order_by="score", k: int = 1):
        # print(str(embedding.tolist()))
        if table == "faq":
            request = f"""
                SELECT
                answer,
                cosineDistance(embedding, {str(embedding[0].tolist())}) AS score
                FROM {table}
                ORDER BY {order_by} ASC
                LIMIT {k}
                FORMAT Vertical
                """

        elif table == "documents":
            request = f"""
                        SELECT
                        text,
                        date,
                        url,
                        cosineDistance(embedding, {str(embedding[0].tolist())}) AS score
                        FROM {table}
                        ORDER BY {order_by} ASC
                        LIMIT {k}
                        FORMAT Vertical
                        """
        else:
            raise ValueError("table should be in ['faq', 'documents']")

        click_out = self._post_process_texts(self.client.execute(request))

        if table == "faq":
            df = self._click_to_pd_faq(click_out)

        elif table == "documents":
            df = self._click_to_pd_documents(click_out)

        return df

    def clichouse_to_df(self, clickhouse_output):
        return "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"

    def get_num_samples(self, table: str):
        request = f"""
        SELECT COUNT() FROM {table};
        """

        return self.client.execute(request)[0][0]
