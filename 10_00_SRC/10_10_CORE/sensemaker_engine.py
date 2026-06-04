import glob
import json
import os

import numpy as np
import pandas as pd
from pysentimiento import create_analyzer
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans


class IndustrialSensemaker:
    def __init__(self, model_name="paraphrase-multilingual-MiniLM-L12-v2"):
        print(f"--- Iniciando Motor de Inteligencia Semántica ({model_name}) ---")
        # Cargamos el modelo de embeddings (Hugging Face)
        self.embed_model = SentenceTransformer(model_name)
        # Cargamos el analizador de sentimiento local que ya teníamos
        self.sentiment_analyzer = create_analyzer(task="sentiment", lang="es")

    def load_all_data(self, raw_path):
        """Carga todos los archivos JSON de la carpeta raw."""
        files = glob.glob(os.path.join(raw_path, "*.json"))
        all_data = []
        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                content = json.load(f)
                if isinstance(content, list):
                    all_data.extend(content)
        return pd.DataFrame(all_data)

    def discover_narratives(self, df, n_clusters=5):
        """
        Usa Clustering para descubrir temas automáticamente.
        """
        if df.empty:
            return "No hay datos para procesar."

        print(f"Procesando {len(df)} comentarios para descubrimiento de narrativas...")

        # 1. Generar Embeddings (lo que 'entiende' la IA)
        texts = df["text"].astype(str).tolist()
        embeddings = self.embed_model.encode(texts)

        # 2. Clustering (K-Means para agrupar por similitud semántica)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        df["cluster"] = kmeans.fit_predict(embeddings)

        # 3. Analizar cada Cluster (Narrativa)
        narrativas_reporte = []
        for i in range(n_clusters):
            cluster_data = df[df["cluster"] == i]

            # Obtener el sentimiento promedio del cluster
            sentimientos = [
                self.sentiment_analyzer.predict(t).probas["POS"] - self.sentiment_analyzer.predict(t).probas["NEG"]
                for t in cluster_data["text"].tolist()[:20]
            ]
            avg_sentiment = np.mean(sentimientos)

            # Identificar palabras clave o frases representativas (más cercanas al centro)
            # Por simplicidad, tomamos los 3 comentarios más cortos del cluster como 'títulos'
            ejemplos = cluster_data.sort_values(by="text", key=lambda x: x.str.len())["text"].head(3).tolist()

            narrativas_reporte.append(
                {
                    "id_narrativa": i,
                    "volumen": len(cluster_data),
                    "porcentaje": round((len(cluster_data) / len(df)) * 100, 2),
                    "sentimiento_salud": round(float(avg_sentiment), 2),
                    "ejemplos_clave": ejemplos,
                    "keywords": "Auto-detectada",  # Aquí se podría añadir un extractor de keywords extra
                }
            )

        return narrativas_reporte


# --- OPERACIÓN NAYARIT INDUSTRIAL ---
if __name__ == "__main__":
    raw_dir = "c:/Users/dcamb/Desktop/Consultoria_Inteligencia/data/raw"
    processed_dir = "c:/Users/dcamb/Desktop/Consultoria_Inteligencia/data/processed"

    sense = IndustrialSensemaker()
    df_raw = sense.load_all_data(raw_dir)

    if not df_raw.empty:
        reporte_final = sense.discover_narratives(df_raw, n_clusters=5)

        # Guardar el hallazgo
        with open(os.path.join(processed_dir, "reporte_industrial_narrativas.json"), "w", encoding="utf-8") as f:
            json.dump(reporte_final, f, indent=4, ensure_ascii=False)

        print("\n--- INFORME DE INTELIGENCIA SEMÁNTICA COMPLETADO ---")
        for n in reporte_final:
            salud = (
                "POSITIVA"
                if n["sentimiento_salud"] > 0.1
                else "CRÍTICA" if n["sentimiento_salud"] < -0.1 else "NEUTRAL"
            )
            print(f"Narrativa #{n['id_narrativa']} ({n['volumen']} menciones - {n['porcentaje']}%):")
            print(f"  Salud: {salud} ({n['sentimiento_salud']})")
            print(f"  Temas detectados: {n['ejemplos_clave'][0][:100]}...")
    else:
        print("No se encontraron datos en data/raw para analizar.")
