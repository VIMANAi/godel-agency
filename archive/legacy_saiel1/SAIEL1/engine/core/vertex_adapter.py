"""
VERTEX AI ADAPTER: SAIEL INTELLIGENCE
Módulo para análisis de sentimiento político usando Gemini 1.5 Flash.
"""

import os
import json
import time
from typing import List, Dict
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting, Part

# Configuración (Ajustar según proyecto real)
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "data-atracttor-lake-gen-lang")
LOCATION = "us-central1"


class VertexSentimentAnalyzer:
    def __init__(self, project_id=PROJECT_ID, location=LOCATION):
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel("gemini-1.5-flash-001")

    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """
        Analiza el sentimiento de un lote de textos.
        """
        if not texts:
            return []

        print(f"--- Analizando lote de {len(texts)} comentarios con Vertex AI ---")

        # Prompt de Ingeniería para consistencia
        prompt = """
        Analiza el sentimiento político de los siguientes comentarios de ciudadanos de Nayarit, México.
        Para cada comentario, devuelve un objeto JSON con:
        - score: flotante entre -1.0 (muy negativo) y 1.0 (muy positivo).
        - label: 'positivo', 'negativo', 'neutro' o 'ironico'.
        - topic: el tema principal (Seguridad, Economía, etc.)

        Devuelve una LISTA de JSONs en el mismo orden que los textos.

        COMENTARIOS:
        """
        for i, text in enumerate(texts):
            prompt += f"\n[{i}] {text}"

        try:
            response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})

            results = json.loads(response.text)
            # Asegurar que sea una lista
            if isinstance(results, dict) and "results" in results:
                results = results["results"]

            return results
        except Exception as e:
            print(f"Error en Vertex AI: {e}")
            # Fallback a neutro en caso de error
            return [{"score": 0.0, "label": "neutro", "topic": "Desconocido"} for _ in texts]


if __name__ == "__main__":
    analyzer = VertexSentimentAnalyzer()
    test_texts = [
        "Andrea Navarro es la mejor opción para Tepic, ha trabajado mucho.",
        "No me gusta nada como está la seguridad en el estado.",
        "Pues ahí la llevan, a ver qué pasa con las elecciones.",
    ]
    res = analyzer.analyze_batch(test_texts)
    print(json.dumps(res, indent=4))
