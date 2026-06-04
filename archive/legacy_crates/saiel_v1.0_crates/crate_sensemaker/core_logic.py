"""
CRATE LOGIC: saiel.sensemaker
Adaptación Industrial de sensemaking-tools para Inteligencia Política.
"""

from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from pysentimiento import create_analyzer


class SensemakerCrate:
    def __init__(self, model="paraphrase-multilingual-MiniLM-L12-v2"):
        self.embedder = SentenceTransformer(model)
        self.analyzer = create_analyzer(task="sentiment", lang="es")

    def process_data(self, df):
        # 1. Embeddings
        embeddings = self.embedder.encode(df["text"].tolist())
        # 2. Clusters (Narrativas)
        kmeans = KMeans(n_clusters=5, n_init=10)
        df["cluster"] = kmeans.fit_predict(embeddings)
        return df

    def get_crate_metadata(self):
        return {
            "crate_id": "saiel.sensemaker",
            "logic_heritage": "sensemaking-tools",
            "adaptation_level": "65%",
            "components": ["SBERT", "KMeans", "PySentimiento"],
        }
