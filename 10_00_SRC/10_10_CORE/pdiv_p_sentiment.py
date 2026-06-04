"""
SAIEL System - Component P: Polarity & Sentiment Module
Calcula el índice de sentimiento normalizado (0-100) para candidatos.
Soporta un pipeline dual: Bunker Ligero (Lexicon Español) y Cloud/ML (API OpenRouter/Ollama).

Autor: SAIEL Intelligence System
Versión: 2.1 (Decoupled SoC)
"""

import json
import re
from typing import Optional

import numpy as np
import pandas as pd
import requests


class PSentimentModule:
    """
    Módulo para cálculo y análisis del Sentimiento / Polaridad (P) de comentarios
    """

    def __init__(self, use_api: bool = False, api_url: Optional[str] = None, api_key: Optional[str] = None):
        self.use_api = use_api
        self.api_url = api_url
        self.api_key = api_key

        # Diccionario léxico básico en español para el fallback local (Bunker Ligero)
        # Valence scores de -1.0 a +1.0
        self.spanish_lexicon = {
            # Positivos
            "bueno": 0.6,
            "buena": 0.6,
            "excelente": 0.9,
            "mejor": 0.7,
            "lider": 0.8,
            "apoyo": 0.8,
            "apoyar": 0.7,
            "ganar": 0.8,
            "ganador": 0.8,
            "triunfo": 0.8,
            "honesto": 0.8,
            "honesta": 0.8,
            "transparente": 0.8,
            "cumple": 0.6,
            "propuesta": 0.5,
            "propuestas": 0.5,
            "trabajador": 0.7,
            "trabajadora": 0.7,
            "gracias": 0.5,
            "inteligente": 0.7,
            "capaz": 0.7,
            "esperanza": 0.8,
            "seguro": 0.6,
            "segura": 0.6,
            "adelante": 0.6,
            "voto": 0.5,
            "votar": 0.5,
            # Negativos
            "malo": -0.6,
            "mala": -0.6,
            "peor": -0.8,
            "corrupto": -0.9,
            "corrupta": -0.9,
            "corrupcion": -0.9,
            "mentira": -0.8,
            "mentiroso": -0.8,
            "mentirosa": -0.8,
            "robar": -0.9,
            "robo": -0.9,
            "ratero": -0.9,
            "ratera": -0.9,
            "inutil": -0.8,
            "falso": -0.7,
            "falsa": -0.7,
            "fraude": -0.9,
            "peligro": -0.7,
            "peligroso": -0.7,
            "peores": -0.8,
            "desastre": -0.8,
            "basura": -0.8,
            "violencia": -0.8,
            "inseguridad": -0.7,
            "mal": -0.5,
            "odio": -0.8,
            "rechazo": -0.6,
        }

        # Modificadores de valencia ( valence shifters )
        self.negations = {"no", "nunca", "tampoco", "jamas", "sin", "nadie", "ningun", "ninguna"}
        self.intensifiers = {"muy": 1.5, "mas": 1.3, "bastante": 1.3, "sumamente": 1.8, "totalmente": 1.8}
        self.diminishers = {"poco": 0.5, "casi": 0.6, "algo": 0.7, "menos": 0.7}

    def _clean_text(self, text: str) -> str:
        """Limpia texto de comentarios para análisis léxico"""
        if not text:
            return ""
        text = text.lower()
        # Eliminar puntuación básica pero conservar espacios y acentos sencillos
        text = re.sub(r"[^\w\sáéíóúüñ]", "", text)
        return text

    def analyze_text_lexicon(self, text: str) -> float:
        """
        Analiza el sentimiento de un texto usando el léxico local en español.
        Retorna un score flotante entre -1.0 y 1.0.
        """
        cleaned = self._clean_text(text)
        words = cleaned.split()
        if not words:
            return 0.0

        scores = []
        for i, word in enumerate(words):
            if word in self.spanish_lexicon:
                valence = self.spanish_lexicon[word]

                # Revisar contexto previo ( Valence Shifters )
                multiplier = 1.0
                negated = False

                # Mirar hasta 2 palabras hacia atrás
                start = max(0, i - 2)
                for j in range(start, i):
                    prev_word = words[j]
                    if prev_word in self.negations:
                        negated = not negated
                    elif prev_word in self.intensifiers:
                        multiplier *= self.intensifiers[prev_word]
                    elif prev_word in self.diminishers:
                        multiplier *= self.diminishers[prev_word]

                final_score = valence * multiplier
                if negated:
                    final_score *= -1.0

                scores.append(final_score)

        if not scores:
            return 0.0

        # Retornar promedio recortado al rango [-1.0, 1.0]
        return float(np.clip(np.mean(scores), -1.0, 1.0))

    def analyze_text_api(self, text: str) -> float:
        """
        Analiza sentimiento llamando a un endpoint LLM (Ollama o OpenRouter).
        Retorna score entre -1.0 y 1.0.
        """
        if not self.api_url or not self.api_key:
            return self.analyze_text_lexicon(text)

        prompt = (
            "Eres un analista político de Nayarit. Clasifica el sentimiento del siguiente comentario sobre "
            "un candidato a la presidencia municipal. Responde ÚNICAMENTE con un número decimal entre -1.0 "
            "(extremadamente negativo/corrupto) y 1.0 (extremadamente positivo/apoyo total), donde 0.0 es neutral.\n\n"
            f'Comentario: "{text}"\n'
            "Score decimal:"
        )

        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}

        # Adaptador dinámico de payload para OpenRouter o API Ollama
        payload = {
            "model": "google/gemma-2-9b-it:free" if "openrouter" in self.api_url.lower() else "gemma-2-9b",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
            "max_tokens": 5,
        }

        try:
            response = requests.post(self.api_url, headers=headers, data=json.dumps(payload), timeout=8)
            if response.status_code == 200:
                res_data = response.json()
                content = res_data["choices"][0]["message"]["content"].strip()
                # Extraer número flotante usando regex
                match = re.search(r"[-+]?\d*\.\d+|\d+", content)
                if match:
                    val = float(match.group())
                    return float(np.clip(val, -1.0, 1.0))
            return self.analyze_text_lexicon(text)
        except Exception:
            # Fallback inmediato en caso de falla de red o API
            return self.analyze_text_lexicon(text)

    def calculate_sentiment_score(self, df: pd.DataFrame) -> pd.Series:
        """
        Calcula el sentimiento promedio por candidato a partir de un DataFrame de comentarios.
        Retorna una serie de Pandas mapeada a la escala de 0 a 100 (donde 50 es neutralidad absoluta).
        """
        if df.empty:
            return pd.Series(dtype=float)

        # Si ya cuenta con puntajes numéricos de sentimiento de antemano
        if "sentimiento_num" in df.columns:
            df["score_p"] = df["sentimiento_num"]
        else:
            # Si el sentimiento es categórico, mapearlo
            if "sentimiento" in df.columns and df["sentimiento"].dtype == "object":
                sentiment_map = {"positivo": 1.0, "negativo": -1.0, "neutro": 0.0, "ironico": -0.5}
                df["score_p"] = df["sentimiento"].map(sentiment_map).fillna(0.0)
            else:
                # Ejecutar análisis según configuración (Lexicon vs API)
                if self.use_api:
                    df["score_p"] = df["text"].apply(self.analyze_text_api)
                else:
                    df["score_p"] = df["text"].apply(self.analyze_text_lexicon)

        # Agrupar por candidato y calcular el promedio
        candidatos_sentiment = df.groupby("candidato")["score_p"].mean().fillna(0.0)

        # Normalización matemática a la escala 0-100 (donde -1.0 -> 0, 0.0 -> 50, 1.0 -> 100)
        sentiment_normalized = ((candidatos_sentiment + 1.0) / 2.0) * 100.0

        return sentiment_normalized.clip(0.0, 100.0)


if __name__ == "__main__":
    # Test rápido de validación léxica
    module = PSentimentModule()
    test_comments = [
        "Geraldine Ponce es excelente candidata, ha hecho propuestas muy buenas por Tepic",
        "No confío en ese corrupto, es lo peor y va a robar mucho",
        "Hoy el candidato dio una plática en la plaza de armas de Tepic.",
        "No es una mala opción, aunque le falta más propuesta.",
    ]

    print("--- Validación Léxica en Español ---")
    for comment in test_comments:
        score = module.analyze_text_lexicon(comment)
        mapped = ((score + 1) / 2) * 100
        print(f"Comentario: {comment[:50]}...")
        print(f" -> Score Valencia [-1 a 1]: {score:.2f} | Mapeado [0 a 100]: {mapped:.2f}\n")
