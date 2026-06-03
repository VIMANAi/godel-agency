from apify_client import ApifyClient
import json
import os
from datetime import datetime
from typing import List, Dict, Any
import logging

# Token de Apify
APIFY_TOKEN = os.getenv("APIFY_TOKEN", "[REDACTED_FROM_ENV]")

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MassCollector:
    """
    Clase para la recolección masiva de comentarios desde posts de redes sociales
    usando la API de Apify.
    """
    def __init__(self) -> None:
        self.client = ApifyClient(APIFY_TOKEN)

    def collect_from_post(self, post_url: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Extrae comentarios de un post específico de Instagram.

        Args:
            post_url (str): La URL del post de Instagram del cual extraer comentarios.
            limit (int): El número máximo de comentarios a recolectar. Por defecto es 20.

        Returns:
            List[Dict[str, Any]]: Una lista de diccionarios donde cada uno representa un comentario
                                  con sus respectivos metadatos. Retorna lista vacía si hay un error.
        """
        logger.info(f"--- Recolectando: {post_url} ---")

        run_input = {
            "directUrls": [post_url],
            "resultsLimit": limit,
        }

        try:
            run = self.client.actor("apify/instagram-comment-scraper").call(run_input=run_input)
            if not run or "defaultDatasetId" not in run:
                logger.error("No se pudo obtener el datasetId de Apify.")
                return []

            data: List[Dict[str, Any]] = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                data.append({
                    "source": "instagram",
                    "source_url": post_url,
                    "candidato": "multiple",  # Para análisis agregado
                    "user": item.get("ownerUsername"),
                    "text": item.get("text"),
                    "date": item.get("timestamp"),
                    "likes": item.get("likesCount", 0),
                    "shares": item.get("sharesCount", 0),
                    "comments": item.get("commentsCount", 0),
                    "collected_at": datetime.now().isoformat()
                })
            logger.info(f"[OK] Extraidos {len(data)} comentarios")
            return data
        except Exception as e:
            logger.exception(f"[ERROR] Error al recolectar comentarios: {str(e)}")
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
    print(f"Límite por post: 20 comentarios")
    print("=" * 50)

    for target in targets:
        batch = collector.collect_from_post(target, limit=20)
        all_data.extend(batch)

    # Guardar todo en un solo archivo consolidado
    from pathlib import Path

    if os.name == "nt":  # Windows
        output_path = Path("c:/Users/dcamb/Desktop/Consultoria_Inteligencia/data/raw/mision_masiva_nayarit.json")
    else:  # Linux/Parrot
        output_path = Path.home() / "Dev/Projects/SAIEL/data/raw/mision_masiva_nayarit.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)

    print("=" * 50)
    print(f"[COMPLETADO] MISION FINALIZADA")
    print(f"Total de comentarios recolectados: {len(all_data)}")
    print(f"Archivo guardado en: {output_path}")
    print("\nProximo paso: Ejecutar sensemaker_engine.py para analisis")
