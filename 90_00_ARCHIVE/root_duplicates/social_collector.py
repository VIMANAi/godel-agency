import json
import os
from datetime import datetime

from apify_client import ApifyClient

# CONFIGURACIÓN MAESTRA
# Token de Apify proporcionado por el usuario
APIFY_TOKEN = os.getenv("APIFY_TOKEN", "REDACTED_APIFY_TOKEN")


class ApifyCollector:
    def __init__(self):
        if not APIFY_TOKEN or "TU_TOKEN" in APIFY_TOKEN:
            raise ValueError("Error: Debes configurar tu APIFY_TOKEN.")
        self.client = ApifyClient(APIFY_TOKEN)

    def collect_social_data(self, target, platform="instagram", limit=20):
        print(f"--- Operación Apify: Iniciando recolección para '{target}' en {platform} ---")

        # Usamos el actor de scraping de comentarios de Instagram
        actor_id = "apify/instagram-comment-scraper"

        # Construimos la URL correctamente según si es perfil o post
        if target.startswith("http"):
            profile_url = target
        elif len(target) > 15:  # Probable handle
            profile_url = f"https://www.instagram.com/{target}/"
        else:  # Probable post ID si es corto y alfanumérico
            profile_url = f"https://www.instagram.com/p/{target}/"

        run_input = {
            "directUrls": [profile_url],
            "resultsLimit": limit,
        }

        try:
            # Llamada síncrona al actor
            run = self.client.actor(actor_id).call(run_input=run_input)
            print(f"Llamada al Actor exitosa para {target}. Dataset: {run['defaultDatasetId']}")

            data = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                data.append(
                    {
                        "source": platform,
                        "target": target,
                        "user": item.get("ownerUsername"),
                        "text": item.get("text"),
                        "date": item.get("timestamp"),
                        "likes": item.get("likesCount"),
                        "collected_at": datetime.now().isoformat(),
                    }
                )

            self._save_to_raw(data, f"raw_{platform}_{target.replace(' ', '_')}.json")
            return data

        except Exception as e:
            print(f"Error en {target}: {str(e)}")
            return []

    def _save_to_raw(self, data, filename):
        save_path = f"c:/Users/dcamb/Desktop/Consultoria_Inteligencia/data/raw/{filename}"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Datos guardados en: {save_path}")


# --- EJECUCIÓN DE MISIONES AUTOMÁTICAS ---
if __name__ == "__main__":
    collector = ApifyCollector()
    print("Iniciando Misión de Prueba (Social Collector)...")
    # Usamos un post real de Geraldine Ponce para validar que el robot conecta y extrae
    test_post = "https://www.instagram.com/p/COHJ9TSnfT6/"
    collector.collect_social_data(test_post.split("/")[-2], platform="instagram", limit=5)
