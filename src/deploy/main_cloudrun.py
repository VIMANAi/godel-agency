"""
SAIEL CLOUD RUN ORCHESTRATOR
Orquestador de extracción de Apify con persistencia en Google Cloud Storage.
"""

import os
import json
from datetime import datetime
from apify_client import ApifyClient
from google.cloud import storage
import functions_framework

# Configuración desde Variables de Entorno
APIFY_TOKEN = os.getenv("APIFY_TOKEN")
GCS_BUCKET = os.getenv("GCS_BUCKET")

@functions_framework.http
def orchestrate_extraction(request):
    """
    Punto de entrada HTTP para Cloud Run.
    Espera un JSON con: { "target": "...", "platform": "...", "limit": 50 }
    """
    request_json = request.get_json(silent=True)
    
    if not request_json or 'target' not in request_json:
        return json.dumps({"error": "Falta parámetro 'target'"}), 400, {'Content-Type': 'application/json'}

    target = request_json['target']
    platform = request_json.get('platform', 'instagram')
    limit = request_json.get('limit', 20)

    try:
        # 1. Ejecutar Extracción en Apify
        client = ApifyClient(APIFY_TOKEN)
        actor_id = "apify/instagram-comment-scraper"
        
        # Lógica de URL simplificada
        profile_url = f"https://www.instagram.com/{target}/" if not target.startswith("http") else target
        
        run_input = {
            "directUrls": [profile_url],
            "resultsLimit": limit,
        }

        print(f"Lanzando actor Apify para: {target}")
        run = client.actor(actor_id).call(run_input=run_input)
        
        # 2. Recolectar Items
        data = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            data.append({
                "source": platform,
                "target": target,
                "text": item.get("text"),
                "date": item.get("timestamp"),
                "likes": item.get("likesCount", 0),
                "collected_at": datetime.now().isoformat()
            })

        # 3. Persistir en GCS
        if GCS_BUCKET:
            storage_client = storage.Client()
            bucket = storage_client.bucket(GCS_BUCKET)
            filename = f"raw/{platform}/{target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            blob = bucket.blob(filename)
            blob.upload_from_string(json.dumps(data, indent=4, ensure_ascii=False), content_type='application/json')
            storage_msg = f"Guardado en gs://{GCS_BUCKET}/{filename}"
        else:
            storage_msg = "GCS_BUCKET no configurado. Datos no persistidos."

        return json.dumps({
            "status": "success",
            "items_collected": len(data),
            "storage": storage_msg
        }), 200, {'Content-Type': 'application/json'}

    except Exception as e:
        print(f"Error en pipeline: {str(e)}")
        return json.dumps({"error": str(e)}), 500, {'Content-Type': 'application/json'}
