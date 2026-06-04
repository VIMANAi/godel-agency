"""
PDIV Calculator - Posicionamiento Digital de Intención de Voto
Implementación matemática rigurosa para correlación >0.7 con encuestas

Autor: Sistema de Inteligencia Política SAIEL
Versión: 2.0 (Production-ready)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings("ignore")


class PDIVCalculator:
    """
    Calculador PDIV con normalización avanzada y ajustes poblacionales
    """

    def __init__(self):
        # Ponderaciones base (configurables)
        self.weights = {
            "sentiment": 0.40,  # Sentimiento promedio
            "volume": 0.30,  # Volumen de menciones
            "engagement": 0.20,  # Engagement/interacciones
            "growth": 0.10,  # Crecimiento semanal
        }

        # Coeficientes de fuente (ajustable por demographics)
        self.source_weights = {
            "instagram": 1.0,  # Base para jóvenes
            "facebook": 0.8,  # Menor peso para adultos
            "tiktok": 0.9,  # Intermedio
            "twitter": 0.7,  # Menor impacto electoral
            "youtube": 0.6,  # Bajo engagement directo
        }

        # Factores de escala poblacional (INEGI 2020)
        self.population_factors = {
            "nayarit": 1.0,  # Base: 1,181,052 habitantes
            "tepic": 0.33,  # 338,058 habitantes (33% del estado)
            "xalisco": 0.05,  # 59,312 habitantes
            "santiago_ixcuintla": 0.04,  # 49,487 habitantes
            "acaponeta": 0.03,  # 35,326 habitantes
        }

        # Umbrales de detección de bots
        self.bot_thresholds = {"max_likes_per_post": 1000, "max_comments_per_user": 50, "spam_ratio_threshold": 0.3}

    def calculate_sentiment_score(self, df: pd.DataFrame) -> pd.Series:
        """
        Calcula sentimiento promedio normalizado (-1 a 1)
        Aplica corrección por sesgo de distribución
        """
        # Convertir sentimiento a escala numérica si es categórico
        if df["sentimiento"].dtype == "object":
            sentiment_map = {"positivo": 1, "negativo": -1, "neutro": 0, "ironico": -0.5}
            df["sentimiento_num"] = df["sentimiento"].map(sentiment_map).fillna(0)
        else:
            df["sentimiento_num"] = pd.to_numeric(df["sentimiento"], errors="coerce").fillna(0)

        # Sentimiento promedio por candidato
        sentiment_avg = df.groupby("candidato")["sentimiento_num"].mean()

        # Normalización a escala 0-100 (donde 50 = neutro)
        sentiment_normalized = ((sentiment_avg + 1) / 2) * 100

        return sentiment_normalized

    def calculate_volume_score(self, df: pd.DataFrame, region: str = "nayarit") -> pd.Series:
        """
        Calcula volumen de menciones ajustado por población y bots
        """
        # Contar menciones por candidato
        volume_raw = df.groupby("candidato").size()

        # Aplicar factor de escala poblacional
        pop_factor = self.population_factors.get(region.lower(), 1.0)
        volume_adjusted = volume_raw / pop_factor

        # Detección y penalización de bots
        bot_penalty = self._calculate_bot_penalty(df)
        volume_final = volume_adjusted * (1 - bot_penalty)

        # Normalización min-max robusta
        volume_normalized = self._robust_min_max_normalize(volume_final)

        return volume_normalized

    def calculate_engagement_score(self, df: pd.DataFrame) -> pd.Series:
        """
        Calcula engagement ponderado por fuente
        """
        # Engagement total por candidato
        engagement_raw = df.groupby("candidato").apply(
            lambda x: (x.get("likes", 0) + x.get("shares", 0) + x.get("comments", 0)).sum()
        )

        # Aplicar ponderación por fuente
        engagement_weighted = (
            df.groupby(["candidato", "source"])
            .apply(
                lambda x: (x.get("likes", 0) + x.get("shares", 0) + x.get("comments", 0)).sum()
                * self.source_weights.get(x.name[1], 0.8)
            )
            .groupby("candidato")
            .sum()
        )

        # Normalización logarítmica (maneja outliers)
        engagement_log = np.log1p(engagement_weighted)
        engagement_normalized = self._robust_min_max_normalize(engagement_log)

        return engagement_normalized

    def calculate_growth_score(self, df: pd.DataFrame, days_back: int = 7) -> pd.Series:
        """
        Calcula crecimiento semanal comparativo
        """
        if "date" not in df.columns:
            # Si no hay fechas, retornar score neutral
            return pd.Series(50.0, index=df["candidato"].unique())

        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        cutoff_date = datetime.now() - timedelta(days=days_back)

        # Separar datos recientes vs históricos
        recent = df[df["date"] >= cutoff_date]
        historical = df[df["date"] < cutoff_date]

        # Calcular crecimiento por candidato
        growth_rates = {}
        for candidate in df["candidato"].unique():
            recent_count = len(recent[recent["candidato"] == candidate])
            historical_count = len(historical[historical["candidato"] == candidate])

            if historical_count == 0:
                growth_rate = 1.0 if recent_count > 0 else 0.0
            else:
                growth_rate = (recent_count - historical_count) / historical_count

            # Normalizar a escala 0-100
            growth_normalized = min(max((growth_rate + 1) / 2 * 100, 0), 100)
            growth_rates[candidate] = growth_normalized

        return pd.Series(growth_rates)

    def _calculate_bot_penalty(self, df: pd.DataFrame) -> float:
        """
        Calcula penalización por actividad sospechosa de bots
        """
        penalty = 0.0

        # 1. Usuarios con demasiados comentarios
        if "user" in df.columns:
            user_counts = df["user"].value_counts()
            suspicious_users = user_counts[user_counts > self.bot_thresholds["max_comments_per_user"]]
            penalty += len(suspicious_users) / len(df) * 0.3

        # 2. Likes anormalmente altos
        if "likes" in df.columns:
            high_likes = df[df["likes"] > self.bot_thresholds["max_likes_per_post"]]
            penalty += len(high_likes) / len(df) * 0.2

        # 3. Patrones de spam (textos repetitivos)
        if "text" in df.columns:
            text_counts = df["text"].value_counts()
            spam_texts = text_counts[text_counts > 5]  # Más de 5 menciones idénticas
            penalty += len(spam_texts) / len(df) * 0.1

        return min(penalty, 0.8)  # Máximo 80% de penalización

    def _robust_min_max_normalize(self, series: pd.Series) -> pd.Series:
        """
        Normalización min-max robusta que maneja outliers
        """
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        # Usar IQR para detectar outliers
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        # Clippear valores atípicos
        series_clipped = series.clip(lower_bound, upper_bound)

        # Normalización min-max estándar
        min_val = series_clipped.min()
        max_val = series_clipped.max()

        if max_val == min_val:
            return pd.Series(50.0, index=series.index)  # Score neutral

        normalized = ((series_clipped - min_val) / (max_val - min_val)) * 100
        return normalized

    def calculate_pdiv(self, df: pd.DataFrame, region: str = "nayarit") -> pd.DataFrame:
        """
        Calcula PDIV completo con todos los componentes
        """
        print(f"--- Iniciando Cálculo PDIV para región: {region} ---")

        # Validar datos mínimos
        required_columns = ["candidato", "sentimiento"]
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Columnas requeridas faltantes: {missing_cols}")

        # Calcular cada componente
        sentiment_score = self.calculate_sentiment_score(df)
        volume_score = self.calculate_volume_score(df, region)
        engagement_score = self.calculate_engagement_score(df)
        growth_score = self.calculate_growth_score(df)

        # Combinar todos los scores
        results = pd.DataFrame(
            {
                "sentimiento_score": sentiment_score,
                "volumen_score": volume_score,
                "engagement_score": engagement_score,
                "crecimiento_score": growth_score,
            }
        ).fillna(
            50.0
        )  # Valores nulos -> score neutral

        # Calcular PDIV final (ecuación lineal ponderada)
        results["pdiv_score"] = (
            results["sentimiento_score"] * self.weights["sentiment"]
            + results["volumen_score"] * self.weights["volume"]
            + results["engagement_score"] * self.weights["engagement"]
            + results["crecimiento_score"] * self.weights["growth"]
        )

        # Asegurar rango 0-100
        results["pdiv_score"] = results["pdiv_score"].clip(0, 100)

        # Agregar metadata
        results["region"] = region
        results["fecha_calculo"] = datetime.now().isoformat()
        results["total_menciones"] = df.groupby("candidato").size()

        # Ordenar por PDIV descendente
        results = results.sort_values("pdiv_score", ascending=False)

        return results

    def generate_positioning_matrix(self, pdiv_results: pd.DataFrame) -> Dict:
        """
        Genera matriz de posicionamiento estratégico
        """
        # Definir cuadrantes
        avg_sentiment = pdiv_results["sentimiento_score"].mean()
        avg_pdiv = pdiv_results["pdiv_score"].mean()

        matrix = {
            "cuadrantes": {
                "lideres": [],  # Alto PDIV, Alto Sentimiento
                "retadores": [],  # Bajo PDIV, Alto Sentimiento
                "vulnerables": [],  # Alto PDIV, Bajo Sentimiento
                "perdedores": [],  # Bajo PDIV, Bajo Sentimiento
            },
            "metricas_global": {
                "pdiv_promedio": avg_pdiv,
                "sentimiento_promedio": avg_sentiment,
                "total_candidatos": len(pdiv_results),
            },
        }

        for _, row in pdiv_results.iterrows():
            candidate = row.name
            pdiv = row["pdiv_score"]
            sentiment = row["sentimiento_score"]

            if pdiv >= avg_pdiv and sentiment >= avg_sentiment:
                matrix["cuadrantes"]["lideres"].append(candidate)
            elif pdiv < avg_pdiv and sentiment >= avg_sentiment:
                matrix["cuadrantes"]["retadores"].append(candidate)
            elif pdiv >= avg_pdiv and sentiment < avg_sentiment:
                matrix["cuadrantes"]["vulnerables"].append(candidate)
            else:
                matrix["cuadrantes"]["perdedores"].append(candidate)

        return matrix

    def validate_correlation(self, piv_results: pd.DataFrame, poll_data: Dict[str, float]) -> float:
        """
        Valida correlación con encuestas reales
        """
        # Alinear datos
        common_candidates = set(piv_results.index) & set(poll_data.keys())
        if len(common_candidates) < 2:
            print("Advertencia: Insuficientes datos para correlación")
            return 0.0

        pdiv_values = [piv_results.loc[candidate]["pdiv_score"] for candidate in common_candidates]
        poll_values = [poll_data[candidate] for candidate in common_candidates]

        # Calcular correlación de Pearson
        correlation = np.corrcoef(pdiv_values, poll_values)[0, 1]

        return correlation if not np.isnan(correlation) else 0.0


# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    # Ejemplo de uso
    calculator = PDIVCalculator()

    # Datos de ejemplo (reemplazar con datos reales)
    sample_data = pd.DataFrame(
        {
            "candidato": ["Candidato A", "Candidato B", "Candidato A", "Candidato C"],
            "sentimiento": ["positivo", "negativo", "neutro", "positivo"],
            "source": ["instagram", "facebook", "instagram", "tiktok"],
            "likes": [100, 50, 200, 80],
            "date": ["2026-01-15", "2026-01-16", "2026-01-17", "2026-01-18"],
        }
    )

    try:
        results = calculator.calculate_pdiv(sample_data, region="tepic")
        print("\n--- RESULTADOS PDIV ---")
        print(results[["pdiv_score", "sentimiento_score", "volumen_score"]].round(2))

        # Matriz de posicionamiento
        matrix = calculator.generate_positioning_matrix(results)
        print(f"\n--- MATRIZ DE POSICIONAMIENTO ---")
        for cuadrante, candidatos in matrix["cuadrantes"].items():
            print(f"{cuadrante.upper()}: {candidatos}")

    except Exception as e:
        print(f"Error: {e}")
