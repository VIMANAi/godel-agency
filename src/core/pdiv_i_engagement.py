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
from typing import Dict, List, Optional

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
        
        Corrección Crítica de Crash en Pandas:
        - En lugar de usar groupby().apply(lambda x: (x.get('likes') + ...)) que causaba errores
          si faltaban columnas o si se retornaban tipos incompatibles, se realiza
          una agregación vectorizada a nivel de fila y luego agrupamiento directo.
        """
        if df.empty:
            return pd.Series(dtype=float)
            
        # 1. Asegurar la presencia de columnas de interacciones y sanitizar nulos
        likes = pd.to_numeric(df['likes'], errors='coerce').fillna(0).astype(int) if 'likes' in df.columns else pd.Series(0, index=df.index)
        shares = pd.to_numeric(df['shares'], errors='coerce').fillna(0).astype(int) if 'shares' in df.columns else pd.Series(0, index=df.index)
        comments = pd.to_numeric(df['comments'], errors='coerce').fillna(0).astype(int) if 'comments' in df.columns else pd.Series(0, index=df.index)
        
        # 2. Calcular interacciones brutas (vectorizado)
        df['temp_interactions'] = likes + shares + comments
        
        # 3. Ponderar por canal (vectorizado)
        if 'source' in df.columns:
            # Mapear fuentes a sus coeficientes
            source_mapped = df['source'].str.lower().map(self.source_weights).fillna(self.source_weights['default'])
            df['temp_weighted_interactions'] = df['temp_interactions'] * source_mapped
        else:
            df['temp_weighted_interactions'] = df['temp_interactions'] * self.source_weights['default']
            
        # 4. Agrupar por candidato y sumar
        engagement_weighted = df.groupby('candidato')['temp_weighted_interactions'].sum()
        
        # 5. Transformación Logarítmica Robusta
        # Atenúa enormemente el impacto de posts virales atípicos (outliers de 100k likes)
        # permitiendo que la comparación de engagement sea equitativa para candidatos medianos.
        engagement_log = np.log1p(engagement_weighted)
        
        # 6. Normalizar a la escala 0-100 usando IQR
        engagement_normalized = self._robust_min_max_normalize(engagement_log)
        
        # Limpieza de columnas temporales para evitar efectos colaterales
        if 'temp_interactions' in df.columns:
            df.drop(columns=['temp_interactions', 'temp_weighted_interactions'], inplace=True, errors='ignore')
            
        return engagement_normalized.clip(0.0, 100.0)

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
