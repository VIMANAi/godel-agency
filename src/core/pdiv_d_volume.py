"""
SAIEL System - Component D: Digital Volume Module
Calcula el índice de volumen digital normalizado (0-100) para candidatos.
Ajusta la métrica utilizando los factores de censo de población (INEGI) y aplica
un factor de penalización robusto por actividad de bots y trolls (spam y frecuencia de comentarios).

Autor: SAIEL Intelligence System
Versión: 2.1 (Decoupled SoC)
"""

import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import polars as pl

logger = logging.getLogger(__name__)


class DVolumeModule:
    """
    Módulo para el cálculo del Volumen Digital (D) ajustado por demografía y comportamiento bot
    """

    def __init__(self, demographics_path: Optional[Path] = None):
        self.demographics_path = demographics_path

        # Factores de escala de población por defecto (Censo INEGI 2020)
        # Tepic representa el 33.8% de la población total de Nayarit
        self.default_population_factors = {
            "nayarit": 1.0,  # Población estatal de referencia: 1,235,456 hab
            "tepic": 0.3388,  # 418,583 habitantes (33.88% del estado)
            "bahia_de_banderas": 0.1519,  # 187,632 habitantes (15.19% del estado)
            "santiago_ixcuintla": 0.0760,  # 93,881 habitantes (7.60% del estado)
            "compostela": 0.0627,  # 77,436 habitantes (6.27% del estado)
            "xalisco": 0.0585,  # 72,286 habitantes (5.85% del estado)
            "acaponeta": 0.0301,  # 37,232 habitantes (3.01% del estado)
        }

        self.population_factors = self.default_population_factors.copy()

        # Umbrales configurables de detección de bots
        self.bot_thresholds = {
            "max_comments_per_user": 40,  # Comentarios máximos de un mismo usuario en el lote
            "max_likes_per_post": 800,  # Más de esto en Tepic indica anomalía / granja
            "spam_duplicate_threshold": 5,  # Comentarios con texto idéntico repetidos más de N veces
        }

        # Intentar cargar factores de población desde archivo estructurado
        self._load_demographics()

    def _load_demographics(self):
        """Intenta cargar dinámicamente los datos de población desde un archivo CSV"""
        if self.demographics_path and Path(self.demographics_path).exists():
            try:
                df = pd.read_csv(self.demographics_path)
                # Debe tener las columnas: municipio, factor_poblacion
                if "municipio" in df.columns and "factor_poblacion" in df.columns:
                    loaded_factors = dict(zip(df["municipio"].str.lower(), df["factor_poblacion"], strict=False))
                    self.population_factors.update(loaded_factors)
            except Exception:
                # Silencioso: mantener los factores por defecto en caso de error
                pass

    def calculate_bot_penalty(self, df: pd.DataFrame) -> pd.Series:
        """
        Calcula una penalización estadística para cada candidato basada en el comportamiento
        de sus cuentas y comentarios en busca de bots/trolls.
        Implementado con Polars para mayor eficiencia.
        Retorna una serie con penalizaciones entre 0.0 (sin bots) y 0.8 (alta sospecha de bots).
        """
        if df.empty or "candidato" not in df.columns:
            return pd.Series(dtype=float)

        try:
            # Preparar datos limpiando tipos mixtos si hay likes
            df_clean = df.copy()
            if "likes" in df_clean.columns:
                df_clean["likes"] = pd.to_numeric(df_clean["likes"], errors="coerce").fillna(0).astype(int)
            else:
                df_clean["likes"] = 0

            # Pasar a Polars
            lf = pl.from_pandas(df_clean).lazy()

            # 1. Calcular total de records por candidato
            total_records = lf.group_by("candidato").agg(pl.len().alias("total_records"))

            # 2. Penalización por usuario (Ataque Sybil)
            if "user" in df_clean.columns:
                user_counts = lf.group_by(["candidato", "user"]).agg(pl.len().alias("user_count"))
                spam_users = user_counts.filter(pl.col("user_count") > self.bot_thresholds["max_comments_per_user"])
                spam_user_volume = spam_users.group_by("candidato").agg(
                    pl.col("user_count").sum().alias("spam_user_volume")
                )
            else:
                spam_user_volume = lf.select("candidato").unique().with_columns(pl.lit(0).alias("spam_user_volume"))

            # 3. Penalización por textos de spam idénticos
            if "text" in df_clean.columns:
                text_counts = lf.group_by(["candidato", "text"]).agg(pl.len().alias("text_count"))
                spam_texts = text_counts.filter(pl.col("text_count") > self.bot_thresholds["spam_duplicate_threshold"])
                spam_text_volume = spam_texts.group_by("candidato").agg(
                    pl.col("text_count").sum().alias("spam_text_volume")
                )
            else:
                spam_text_volume = lf.select("candidato").unique().with_columns(pl.lit(0).alias("spam_text_volume"))

            # 4. Likes anormalmente altos
            high_likes = lf.filter(pl.col("likes") > self.bot_thresholds["max_likes_per_post"])
            high_likes_volume = high_likes.group_by("candidato").agg(pl.len().alias("high_likes_count"))

            # Consolidar penalizaciones
            penalties_lf = total_records.join(spam_user_volume, on="candidato", how="left").fill_null(0)
            penalties_lf = penalties_lf.join(spam_text_volume, on="candidato", how="left").fill_null(0)
            penalties_lf = penalties_lf.join(high_likes_volume, on="candidato", how="left").fill_null(0)

            penalties_lf = penalties_lf.with_columns(
                penalty=(
                    (pl.col("spam_user_volume") / pl.col("total_records") * 0.4)
                    + (pl.col("spam_text_volume") / pl.col("total_records") * 0.3)
                    + (pl.col("high_likes_count") / pl.col("total_records") * 0.1)
                ).clip(0.0, 0.8)
            )

            penalties_df = penalties_lf.collect()

            return pd.Series(penalties_df["penalty"].to_numpy(), index=penalties_df["candidato"].to_numpy())

        except Exception as e:
            logger.exception(f"Error en el cálculo de penalizaciones por bot (Polars): {e}")
            return pd.Series({c: 0.0 for c in df["candidato"].unique()})

    def _robust_min_max_normalize(self, series: pd.Series) -> pd.Series:
        """
        Normalización min-max robusta basada en rango intercuartil (IQR) para atenuar outliers
        """
        if series.empty:
            return series

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        if iqr == 0:
            iqr = 1.0  # Evitar divisiones por cero

        # Clippear valores extremos utilizando barreras IQR
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        series_clipped = series.clip(lower_bound, upper_bound)

        min_val = series_clipped.min()
        max_val = series_clipped.max()

        if max_val == min_val:
            return pd.Series(50.0, index=series.index)

        normalized = ((series_clipped - min_val) / (max_val - min_val)) * 100.0
        return normalized

    def calculate_volume_score(self, df: pd.DataFrame, region: str = "tepic") -> pd.Series:
        """
        Calcula el volumen de menciones ajustado por demografía e impacto bot.
        Normaliza robustamente a escala de 0 a 100.
        """
        if df.empty:
            return pd.Series(dtype=float)

        # 1. Contar menciones brutas por candidato
        volume_raw = df.groupby("candidato").size().astype(float)

        # 2. Ajuste demográfico según región
        # Si analizamos una contienda local (por ejemplo, Tepic-only), todos los candidatos
        # pertenecen a la misma región, por lo que el factor de población es homogéneo (1.0).
        # Si se hace un análisis estatal/multiregional, el volumen se escala por el peso poblacional del municipio.
        pop_factor = self.population_factors.get(region.lower(), 1.0)

        # Multiplicamos el volumen bruto por el factor demográfico para representar
        # el impacto del candidato respecto al universo electoral completo de la región.
        volume_adjusted = volume_raw * pop_factor

        # 3. Calcular y aplicar penalización por bots/spam
        bot_penalties = self.calculate_bot_penalty(df)

        # Alinear series e inyectar penalizaciones
        volume_final = volume_adjusted * (1.0 - bot_penalties.reindex(volume_adjusted.index, fill_value=0.0))

        # 4. Normalización robusta
        volume_normalized = self._robust_min_max_normalize(volume_final)

        return volume_normalized.clip(0.0, 100.0)


if __name__ == "__main__":
    # Test de validación del módulo de volumen y bots
    print("--- Validación de Detección de Bots y Volumen Ajustado ---")

    # Simulación de datos con un candidato bajo ataque de bots
    sample_df = pd.DataFrame(
        {
            "candidato": ["Candidato Limpio"] * 100 + ["Candidato Con Bots"] * 100,
            "user": ["user_" + str(i) for i in range(100)]
            + ["spammer_bot"] * 90
            + ["user_" + str(i) for i in range(10)],
            "text": ["Comentario de apoyo orgánico #" + str(i) for i in range(100)]
            + ["VOTE POR EL CANDIDATO X EL MEJOR!!!"] * 90
            + ["Comentario normal #" + str(i) for i in range(10)],
            "likes": [5] * 100 + [5] * 10 + [900] * 90,  # 90 posts con likes atípicos
        }
    )

    module = DVolumeModule()

    print("\n1. Análisis de penalizaciones por bots:")
    penalties = module.calculate_bot_penalty(sample_df)
    for cand, penalty in penalties.items():
        print(f" -> {cand}: Penalización del {penalty*100:.1f}%")

    print("\n2. Cálculo de Score de Volumen Normalizado:")
    volume_scores = module.calculate_volume_score(sample_df, region="tepic")
    for cand, score in volume_scores.items():
        print(f" -> {cand}: Score final: {score:.2f} / 100")
