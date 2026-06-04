import json
import os
from datetime import datetime

from apify_client import ApifyClient

# Token de Apify
APIFY_TOKEN = os.getenv("APIFY_TOKEN", "REDACTED_APIFY_TOKEN")


class MassCollector:
    def __init__(self):
        self.client = ApifyClient(APIFY_TOKEN)

    def collect_from_post(self, post_url, limit=20):
        """Extrae comentarios de un post específico de Instagram."""
        print(f"--- Recolectando: {post_url} ---")

        run_input = {
            "directUrls": [post_url],
            "resultsLimit": limit,
        }

        try:
            run = self.client.actor("apify/instagram-comment-scraper").call(run_input=run_input)
            data = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                data.append(
                    {
                        "source_url": post_url,
                        "user": item.get("ownerUsername"),
                        "text": item.get("text"),
                        "date": item.get("timestamp"),
                        "likes": item.get("likesCount"),
                        "collected_at": datetime.now().isoformat(),
                    }
                )
            print(f"[OK] Extraidos {len(data)} comentarios")
            return data
        except Exception as e:
            print(f"[ERROR] {str(e)}")
            return []


# --- MISIÓN: RECOLECCIÓN MASIVA NAYARIT ---
if __name__ == "__main__":
    collector = MassCollector()
    all_data = []

    # Lista de posts públicos de figuras clave (encontrados en la auditoría)
    targets = [
        # Geraldine Ponce (Alcaldesa Tepic)
        "https://www.instagram.com/p/COHJ9TSnfT6/",  # Registro candidatura 2021
        "https://www.instagram.com/p/COEP_fonski/",  # Campaña 2021
        # Aquí agregaríamos más posts de:
        # - Andrea Navarro (cuando encontremos sus posts públicos)
        # - Héctor Santana
        # - Beatriz Estrada
        # - Gobernador Miguel Ángel Navarro
    ]

    print("=== INICIANDO RECOLECCIÓN MASIVA ===")
    print(f"Objetivos: {len(targets)} posts")
    print("Límite por post: 20 comentarios")
    print("=" * 50)

    for target in targets:
        batch = collector.collect_from_post(target, limit=20)
        all_data.extend(batch)

    # Guardar todo en un solo archivo consolidado
    output_path = "c:/Users/dcamb/Desktop/Consultoria_Inteligencia/data/raw/mision_masiva_nayarit.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)

    print("=" * 50)
    print("[COMPLETADO] MISION FINALIZADA")
    print(f"Total de comentarios recolectados: {len(all_data)}")
    print(f"Archivo guardado en: {output_path}")
    print("\nProximo paso: Ejecutar sensemaker_engine.py para analisis")
