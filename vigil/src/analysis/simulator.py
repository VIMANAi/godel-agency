"""Módulo de simulación estratégica "What-If" para Vigil.

Permite simular cambios en el posicionamiento electoral (PDIV)
al reponderar la mezcla de temas de comunicación o simular giros de opinión pública.
"""

import logging
from typing import Dict

import numpy as np
import polars as pl

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class WhatIfSimulator:
    """Simulador de escenarios estratégicos para re-calcular PDIV y sentimiento."""

    def __init__(self, weights: Dict[str, float] = None) -> None:
        self.weights = weights or {
            "sentiment": 0.40,
            "volume": 0.30,
            "engagement": 0.20,
            "growth": 0.10,
        }

    def calcular_scores_base(self, df_gold: pl.DataFrame) -> pl.DataFrame:
        """Calcula los scores base de sentimiento, volumen, engagement y crecimiento para cada candidato."""
        if df_gold.height == 0:
            return pl.DataFrame()

        # Asegurar columna de sentimiento numérico
        df_gold = self._asegurar_sentimiento_numerico(df_gold)

        # 1. Sentimiento promedio por candidato normalizado a escala 0-100 (50 = neutral)
        df_sentiment = (
            df_gold.group_by("candidato")
            .agg(pl.col("sentimiento_num").mean().alias("sentimiento_promedio"))
            .with_columns(((pl.col("sentimiento_promedio") + 1) / 2 * 100).clip(0, 100).alias("sentimiento_score"))
        )

        # 2. Volumen por candidato
        df_volume = df_gold.group_by("candidato").agg(pl.count().alias("volumen_menciones"))
        # Normalización min-max robusta de volumen
        max_vol = df_volume["volumen_menciones"].max()
        min_vol = df_volume["volumen_menciones"].min()
        rango_vol = max_vol - min_vol if max_vol != min_vol else 1
        df_volume = df_volume.with_columns(
            ((pl.col("volumen_menciones") - min_vol) / rango_vol * 100).alias("volumen_score")
        )

        # 3. Engagement por candidato
        df_engagement = df_gold.group_by("candidato").agg(pl.col("reacciones_totales").sum().alias("engagement_total"))
        # Normalización logarítmica robusta
        df_engagement = df_engagement.with_columns(
            pl.col("engagement_total").fill_null(0).cast(pl.Float64).log1p().alias("engagement_log")
        )
        max_eng = df_engagement["engagement_log"].max()
        min_eng = df_engagement["engagement_log"].min()
        rango_eng = max_eng - min_eng if max_eng != min_eng else 1
        df_engagement = df_engagement.with_columns(
            ((pl.col("engagement_log") - min_eng) / rango_eng * 100).alias("engagement_score")
        )

        # 4. Unir scores y calcular PDIV base
        df_scores = (
            df_sentiment.join(df_volume, on="candidato", how="left")
            .join(df_engagement, on="candidato", how="left")
            .with_columns(
                # Crecimiento simplificado (score fijo de 50 para el MVP base si no hay series de tiempo)
                pl.lit(50.0).alias("crecimiento_score")
            )
            .with_columns(
                (
                    pl.col("sentimiento_score") * self.weights["sentiment"]
                    + pl.col("volumen_score") * self.weights["volume"]
                    + pl.col("engagement_score") * self.weights["engagement"]
                    + pl.col("crecimiento_score") * self.weights["growth"]
                ).alias("pdiv_score")
            )
            .sort("pdiv_score", descending=True)
        )

        return df_scores

    def simular_cambio_temas(
        self, df_gold: pl.DataFrame, candidato_target: str, ajustes_temas: Dict[str, float]
    ) -> pl.DataFrame:
        """Simula cómo cambia el PDIV si el candidato objetivo modifica su agenda de comunicación.

        Args:
            df_gold: DataFrame de entrada con datos enriquecidos.
            candidato_target: Candidato sobre el cual aplicar la simulación.
            ajustes_temas: Diccionario de ajustes por tópico (ej: {"seguridad": 0.30, "obras": -0.20}).
                           Un valor positivo (0.30) representa un incremento del 30% en posts de ese tema.

        Returns:
            DataFrame con columnas comparativas (baseline vs simulado).
        """
        if df_gold.height == 0:
            return pl.DataFrame()

        # Calcular línea base
        df_base = self.calcular_scores_base(df_gold)
        if df_base.height == 0:
            return pl.DataFrame()

        # Asegurar sentimiento numérico
        df_sim = self._asegurar_sentimiento_numerico(df_gold)

        # 1. Asignar factores de peso por publicación
        # Por defecto cada publicación pesa 1.0. Si contiene el tema target, modificamos el peso.
        pesos_post = np.ones(df_sim.height)

        # Buscar palabras clave en la columna texto_publicacion o keywords_extracted
        for index, row in enumerate(df_sim.iter_rows(named=True)):
            if row["candidato"] != candidato_target:
                continue

            texto = row.get("texto_publicacion", "").lower()
            keywords = row.get("keywords_extracted", [])
            if keywords is None:
                keywords = []

            for tema, factor in ajustes_temas.items():
                tema_lc = tema.lower()
                # Verificar si el tema está en el texto o en las keywords
                if tema_lc in texto or any(tema_lc in str(kw).lower() for kw in keywords):
                    # Aplicar factor multiplicador (ej. +30% es 1.30, -20% es 0.80)
                    pesos_post[index] *= 1.0 + factor

        df_sim = df_sim.with_columns(pl.Series("peso_simulado", pesos_post))

        # 2. Recalcular métricas ponderadas por peso_simulado
        # A. Sentimiento simulado
        df_sentiment_sim = (
            df_sim.group_by("candidato")
            .agg(
                (pl.col("sentimiento_num") * pl.col("peso_simulado")).sum().alias("sentimiento_num_sum"),
                pl.col("peso_simulado").sum().alias("peso_total"),
            )
            .with_columns((pl.col("sentimiento_num_sum") / pl.col("peso_total")).alias("sentimiento_promedio_sim"))
            .with_columns(
                ((pl.col("sentimiento_promedio_sim") + 1) / 2 * 100).clip(0, 100).alias("sentimiento_score_sim")
            )
            .select(["candidato", "sentimiento_score_sim"])
        )

        # B. Volumen simulado (suma de pesos)
        df_volume_sim = df_sim.group_by("candidato").agg(pl.col("peso_simulado").sum().alias("volumen_simulado"))
        max_vol_sim = df_volume_sim["volumen_simulado"].max()
        min_vol_sim = df_volume_sim["volumen_simulado"].min()
        rango_vol_sim = max_vol_sim - min_vol_sim if max_vol_sim != min_vol_sim else 1
        df_volume_sim = df_volume_sim.with_columns(
            ((pl.col("volumen_simulado") - min_vol_sim) / rango_vol_sim * 100).alias("volumen_score_sim")
        )

        # C. Engagement simulado (ponderado)
        df_engagement_sim = (
            df_sim.group_by("candidato")
            .agg(
                (pl.col("reacciones_totales").fill_null(0).cast(pl.Float64) * pl.col("peso_simulado"))
                .sum()
                .alias("engagement_total_sim")
            )
            .with_columns(pl.col("engagement_total_sim").log1p().alias("engagement_log_sim"))
        )
        max_eng_sim = df_engagement_sim["engagement_log_sim"].max()
        min_eng_sim = df_engagement_sim["engagement_log_sim"].min()
        rango_eng_sim = max_eng_sim - min_eng_sim if max_eng_sim != min_eng_sim else 1
        df_engagement_sim = df_engagement_sim.with_columns(
            ((pl.col("engagement_log_sim") - min_eng_sim) / rango_eng_sim * 100).alias("engagement_score_sim")
        )

        # D. Combinar scores y calcular PDIV simulado
        df_simulados = (
            df_sentiment_sim.join(df_volume_sim, on="candidato", how="left")
            .join(df_engagement_sim, on="candidato", how="left")
            .with_columns(pl.lit(50.0).alias("crecimiento_score_sim"))
            .with_columns(
                (
                    pl.col("sentimiento_score_sim") * self.weights["sentiment"]
                    + pl.col("volumen_score_sim") * self.weights["volume"]
                    + pl.col("engagement_score_sim") * self.weights["engagement"]
                    + pl.col("crecimiento_score_sim") * self.weights["growth"]
                ).alias("pdiv_score_sim")
            )
        )

        # 3. Cruzar línea base con datos simulados para retornar comparación
        df_comparativo = (
            df_base.select(["candidato", "pdiv_score", "sentimiento_score", "volumen_score"])
            .join(
                df_simulados.select(["candidato", "pdiv_score_sim", "sentimiento_score_sim", "volumen_score_sim"]),
                on="candidato",
                how="inner",
            )
            .with_columns(
                (pl.col("pdiv_score_sim") - pl.col("pdiv_score")).round(2).alias("dif_pdiv"),
                (pl.col("sentimiento_score_sim") - pl.col("sentimiento_score")).round(2).alias("dif_sentimiento"),
            )
            .sort("pdiv_score_sim", descending=True)
        )

        return df_comparativo

    def _asegurar_sentimiento_numerico(self, df: pl.DataFrame) -> pl.DataFrame:
        """Helper para asegurar que la columna de sentimiento numérico existe y está tipada."""
        if "sentimiento_num" in df.columns:
            return df

        # Si el sentimiento es cualitativo, mapearlo
        if "sentimiento" in df.columns:
            # Diccionario de mapeo cualitativo -> numérico (-1 a 1)
            sentiment_map = {
                "positive": 1.0,
                "positive_praising": 1.0,
                "neutral": 0.0,
                "informative": 0.0,
                "negative": -1.0,
                "negative_revile": -1.0,
                "troll": -0.5,
            }
            # Mapear
            return df.with_columns(
                pl.col("sentimiento").replace(sentiment_map, default=0.0).cast(pl.Float64).alias("sentimiento_num")
            )
        else:
            # Si no hay columna de sentimiento, crearla con neutros
            return df.with_columns(pl.lit(0.0).alias("sentimiento_num"))
