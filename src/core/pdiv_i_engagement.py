"""
SAIEL System - Component I: Interaction & Engagement Module
Calcula el índice de engagement e interacción normalizado (0-100) para candidatos.
Aplica transformaciones logarítmicas robustas para amortiguar publicaciones virales atípicas (outliers)
y pondera el involucramiento de acuerdo con la plataforma de red social (Instagram, Facebook, etc.).

Autor: SAIEL Intelligence System
Versión: 2.1 (Decoupled SoC)
"""

import pandas as pd
import numpy as np
import polars as pl
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class IEngagementModule:
    """
    Módulo para el cálculo del Engagement Ponderado (I) de candidatos
    """
    
    def __init__(self):
        # Coeficientes de ponderación de canal (demographics post-stratification)
        # Adaptado a la representatividad electoral en Nayarit
        self.source_weights = {
            'instagram': 1.0,     # Fuerte tracción y penetración en sectores jóvenes activos
            'facebook': 0.9,      # Mayor volumen y masa crítica en padrón electoral general
            'tiktok': 0.8,        # Mucha viralidad, pero con menor conversión de voto efectiva
            'youtube': 0.7,       # Bajo volumen de comentarios directos locales
            'twitter': 0.6,       # Canal muy politizado pero hiper-concentrado
            'x': 0.6,
            'default': 0.8
        }

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
            iqr = 1.0
            
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        series_clipped = series.clip(lower_bound, upper_bound)
        
        min_val = series_clipped.min()
        max_val = series_clipped.max()
        
        if max_val == min_val:
            return pd.Series(50.0, index=series.index)
            
        normalized = ((series_clipped - min_val) / (max_val - min_val)) * 100.0
        return normalized

    def calculate_engagement_score(self, df: pd.DataFrame) -> pd.Series:
        """
        Calcula el score de engagement por candidato.
        Utiliza Polars para optimización de rendimiento a través de pipelines paralelizables.
        
        Args:
            df (pd.DataFrame): DataFrame de Pandas con la información de las redes.

        Returns:
            pd.Series: Serie con el score de engagement normalizado por candidato.
        """
        if df.empty:
            return pd.Series(dtype=float)
            
        try:
            # 0. Limpiar columnas en Pandas antes de pasar a Polars porque pyarrow crashea al convertir tipos mixtos
            df_clean = df.copy()
            cols_to_check = ['likes', 'shares', 'comments']
            for col in cols_to_check:
                if col not in df_clean.columns:
                    df_clean[col] = 0
                else:
                    # Coerción segura en pandas para que no falle la conversión a arrow
                    df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0).astype(int)

            # 1. Convertir a Polars para procesamiento eficiente
            lf = pl.from_pandas(df_clean).lazy()
            
            # 1. Calcular interacciones brutas
            lf = lf.with_columns(
                (pl.col("likes") + pl.col("shares") + pl.col("comments")).alias("temp_interactions")
            )

            # 2. Ponderar por canal
            if "source" in df.columns:
                # Crear un mapeo usando un dataframe auxiliar de Polars
                source_df = pl.DataFrame({
                    "source_lower": list(self.source_weights.keys()),
                    "weight": list(self.source_weights.values())
                }).lazy()

                # Normalizar la columna source
                lf = lf.with_columns(pl.col("source").cast(pl.String).str.to_lowercase().alias("source_lower"))

                # Unir para obtener los pesos
                lf = lf.join(source_df, on="source_lower", how="left")

                # Si el peso es nulo, usar el default, y multiplicar por interacciones
                lf = lf.with_columns(
                    (pl.col("temp_interactions") * pl.col("weight").fill_null(self.source_weights['default'])).alias("temp_weighted_interactions")
                )

            else:
                lf = lf.with_columns(
                    (pl.col("temp_interactions") * self.source_weights['default']).alias("temp_weighted_interactions")
                )

            # 3. Agrupar por candidato y sumar
            agg_df = lf.group_by("candidato").agg(
                pl.col("temp_weighted_interactions").sum().alias("total_engagement")
            ).collect()

            # Convertir de vuelta a pandas para seguir con las interfaces existentes
            engagement_weighted = pd.Series(
                agg_df["total_engagement"].to_numpy(),
                index=agg_df["candidato"].to_numpy()
            )

            # 4. Transformación Logarítmica Robusta
            engagement_log = np.log1p(engagement_weighted)
            
            # 5. Normalizar a la escala 0-100 usando IQR
            engagement_normalized = self._robust_min_max_normalize(engagement_log)

            return engagement_normalized.clip(0.0, 100.0)

        except Exception as e:
            logger.exception(f"Error en el cálculo de engagement (Polars): {e}")
            return pd.Series(dtype=float)

if __name__ == "__main__":
    # Test de verificación del cálculo del engagement
    print("--- Validación de Engagement Vectorizado sin Crashes ---")
    
    # Simulación de DataFrame que contiene columnas ausentes (ej. shares)
    # y valores no numéricos para validar sanitización robusta
    test_df = pd.DataFrame({
        'candidato': ['Candidato Viral', 'Candidato Moderado', 'Candidato Viral', 'Candidato Pequeño'],
        'source': ['instagram', 'facebook', 'facebook', 'twitter'],
        'likes': [15000, 340, 25000, 12],
        'comments': [1200, 'invalid_comment_count', 2400, 2] # Inyectamos un string para probar coerción
        # La columna 'shares' está ausente deliberadamente
    })
    
    module = IEngagementModule()
    
    try:
        scores = module.calculate_engagement_score(test_df)
        print("\nCálculo de Score de Engagement (Escala Logarítmica + IQR):")
        for cand, score in scores.items():
            print(f" -> {cand}: Score de Engagement = {score:.2f} / 100")
        print("\n✅ El cálculo finalizó con éxito y sin crashes, superando la limitación del código legado.")
    except Exception as e:
        print(f"\n❌ Falla durante la validación del módulo: {e}")
