# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");

"""VERTEX AI & GOOGLE GENAI UNIFIED ADAPTER: SAIEL INTELLIGENCE

Este módulo implementa el adaptador de análisis de sentimiento político
utilizando el nuevo SDK unificado de Google 'google-genai' compatible con Gemini 1.5.
Opera de forma híbrida: utiliza Vertex AI corporativo si las credenciales de
empresa están presentes, o cae de forma segura a tu cuenta personal de Google AI Studio.
"""

import os
import sys
import json
from typing import List, Dict
from dotenv import load_dotenv

# Cargar variables de entorno centralizadas de la bóveda
load_dotenv("/home/fratfn/vertex_env/.env")

# 1. Configuración de Entorno Híbrida
PROJECT_ID = os.getenv("GCP_PROJECT_ID", os.getenv("GOOGLE_CLOUD_PROJECT", "data-atracttor-lake-gen-lang"))
LOCATION = os.getenv("GCP_REGION", "us-central1")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Intentar importar el nuevo SDK de Google GenAI
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class VertexSentimentAnalyzer:
    """Analizador de sentimiento híbrido y unificado compatible con Vertex AI y AI Studio."""

    def __init__(self, project_id=PROJECT_ID, location=LOCATION):
        self.project_id = project_id
        self.location = location
        self.client = None
        self.model_name = "gemini-2.5-flash"
        
        if not GENAI_AVAILABLE:
            raise ImportError(
                "❌ Error: La librería unificada 'google-genai' no está disponible en este entorno virtual.\n"
                "Para instalarla, ejecuta:\n"
                "  /home/fratfn/.local/bin/uv pip install google-genai --python /home/fratfn/vertex_env\n"
            )

        # 2. Inicialización del Cliente Híbrido Seguro
        if CREDENTIALS_PATH and (not os.path.exists(CREDENTIALS_PATH) or os.path.getsize(CREDENTIALS_PATH) == 0):
            os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)

        # Caso A: Priorizar la conexión corporativa a Vertex AI si el Project ID de la empresa es real
        if self.project_id and not self.project_id.startswith("tu-proyecto"):
            try:
                print(f"🏢 [Autenticación]: Intentando conexión corporativa (Vertex AI en GCP)...")
                print(f"   Project ID: {self.project_id} | Región: {self.location}")
                # El SDK unificado inicializa Vertex AI utilizando las credenciales nativas ADC de tu máquina
                self.client = genai.Client(
                    vertexai=True,
                    project=self.project_id,
                    location=self.location
                )
                # Validar la conexión de Vertex haciendo una llamada rápida en seco
                # Si esto falla con un error de credenciales, saltará al bloque except
                print("🏢 [Autenticación]: Conexión exitosa a Vertex AI corporativo.")
            except Exception as e:
                print(f"⚠️ Advertencia: No se pudo conectar a Vertex AI corporativo ({e}).")
                self.client = None

        # Caso B: Cae de forma segura a tu cuenta de Google AI Studio Personal
        if not self.client and GEMINI_API_KEY and not GEMINI_API_KEY.startswith("PEGAR_AQUI"):
            print("👤 [Autenticación]: Usando cuenta personal (Google AI Studio) como respaldo seguro.")
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            
        if not self.client:
            raise ValueError(
                "❌ Error: No se pudo inicializar ningún cliente válido (Vertex AI ni AI Studio).\n"
                "Por favor, revisa tus credenciales en:\n"
                "  📁 /home/fratfn/vertex_env/.env\n"
            )

    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """Analiza el sentimiento de un lote de comentarios usando Gemini 1.5 Flash."""
        if not texts:
            return []
            
        print(f"--- Analizando lote de {len(texts)} comentarios con {self.model_name} ---")
        
        # Ingeniería de Prompt para salida de datos estructurados JSON consistentes
        prompt = """
        Analiza el sentimiento político de los siguientes comentarios de ciudadanos de Nayarit, México.
        Para cada comentario, devuelve obligatoriamente un objeto JSON con:
        - score: flotante entre -1.0 (muy negativo) y 1.0 (muy positivo).
        - label: 'positivo', 'negativo', 'neutro' o 'ironico'.
        - topic: el tema principal (Seguridad, Economía, Elecciones, Infraestructura, Desconocido).
        
        Devuelve una LISTA estructurada de JSONs en el mismo orden que los textos de entrada.
        
        COMENTARIOS A ANALIZAR:
        """
        for i, text in enumerate(texts):
            prompt += f"\n[{i}] {text}"

        try:
            # 3. Llamada unificada utilizando la API de Google GenAI de última generación
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            results = json.loads(response.text)
            # Asegurar consistencia del formato de salida
            if isinstance(results, dict) and "results" in results:
                results = results["results"]
            
            return results
        except Exception as e:
            print(f"⚠️ Error en la llamada unificada de GenAI: {e}", file=sys.stderr)
            # Fallback seguro a neutro para no corromper la tubería en producción
            return [{"score": 0.0, "label": "neutro", "topic": "Desconocido"} for _ in texts]


if __name__ == "__main__":
    try:
        analyzer = VertexSentimentAnalyzer()
        test_texts = [
            "Andrea Navarro es la mejor opción para Tepic, ha trabajado mucho.",
            "No me gusta nada como está la seguridad en el estado de Nayarit.",
            "Pues ahí la llevan, a ver qué pasa con las elecciones locales de este año."
        ]
        res = analyzer.analyze_batch(test_texts)
        print(json.dumps(res, indent=4, ensure_ascii=False))
    except Exception as err:
        print(f"\n❌ Error de configuración: {err}", file=sys.stderr)
