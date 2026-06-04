"""Agente semántico electoral para clasificación NLP con Gemini.

Responsable: SAEIL / equipo de análisis.
Módulo de clasificación semántica del discurso político.
"""

import json
import logging
import os
from typing import Any

import polars as pl
from google import genai
from google.genai import types

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

MODEL_ID: str = "gemini-2.5-flash"
API_KEY_ENV_VAR: str = "GEMINI_API_KEY"

NLP_SYSTEM_PROMPT = """
Eres un clasificador experto de discurso político electoral.
Analiza el texto proporcionado y devuelve ÚNICAMENTE un objeto JSON con:
  "sentiment": "positive" | "negative" | "neutral"
  "framing": "praising" | "revile" | "informative" | "troll" | "irrelevante"
  "keywords_extracted": [lista de entidades: candidatos, temas, zonas geográficas]
  "confidence": valor de 0.0 a 1.0

Contexto: Elecciones municipales Nayarit 2026. Tepic es la capital del estado.
"""


class AgenteSemanticoElectoral:
    """Clasificador de discurso político basado en Gemini 2.5-flash."""

    def __init__(self) -> None:
        self.api_key = os.environ.get(API_KEY_ENV_VAR)
        self.client = None
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Error al inicializar el cliente de Gemini: {e}")

        if not self.client:
            logger.warning("Gemini Client no inicializado. Modo simulación activo.")

    def clasificar_comentario(self, texto: str) -> dict[str, Any]:
        """Clasifica intención y sentimiento mediante la API de Gemini.

        Args:
            texto: Texto crudo de publicación o comentario.

        Returns:
            Dict con sentiment, framing, keywords_extracted, confidence.
        """
        if not self.client:
            return {
                "sentiment": "neutral",
                "framing": "informative",
                "keywords_extracted": ["Indeterminado"],
                "confidence": 0.0,
            }

        try:
            response = self.client.models.generate_content(
                model=MODEL_ID,
                contents=texto,
                config=types.GenerateContentConfig(
                    system_instruction=NLP_SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    temperature=0.1,
                ),
            )
            # Validar que la respuesta contiene texto
            if response.text:
                return json.loads(response.text)
            else:
                return {
                    "sentiment": "neutral",
                    "framing": "informative",
                    "keywords_extracted": [],
                    "confidence": 0.0,
                }
        except Exception as e:
            logger.error(f"Error durante inferencia: {e}")
            return {
                "error": "falla_en_inferencia",
                "sentiment": "neutral",
                "framing": "informative",
                "keywords_extracted": [],
            }

    def clasificar_dataframe(self, df: pl.DataFrame, columna_texto: str) -> pl.DataFrame:
        """Procesa y enriquece un DataFrame de Polars llamando al clasificador NLP.

        Agrega las columnas: sentimiento, framing, keywords_extracted, confidence.
        """
        if df.height == 0:
            return df

        logger.info(f"Clasificando {df.height} comentarios con Gemini API.")

        sentiments = []
        framings = []
        keywords = []
        confidences = []

        # Bucle secuencial para clasificación
        for idx, row in enumerate(df.iter_rows(named=True)):
            texto = row.get(columna_texto, "")
            if not texto:
                sentiments.append("neutral")
                framings.append("informative")
                keywords.append([])
                confidences.append(0.0)
                continue

            res = self.clasificar_comentario(str(texto))
            sentiments.append(res.get("sentiment", "neutral"))
            framings.append(res.get("framing", "informative"))
            keywords.append(res.get("keywords_extracted", res.get("keywords", [])))
            confidences.append(res.get("confidence", 0.0))

        # Inyectar columnas en Polars
        df_enriquecido = df.with_columns(
            [
                pl.Series("sentimiento", sentiments),
                pl.Series("framing", framings),
                pl.Series("keywords_extracted", keywords),
                pl.Series("confidence", confidences),
            ]
        )

        return df_enriquecido
