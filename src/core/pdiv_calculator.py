"""
SAIEL System - PDIV Calculator Orchestrator
Orquestador del índice PDIV (Posicionamiento Digital de Intención de Voto).
Importa y coordina los submódulos independientes P, D, I y V, combina sus puntuaciones
linealmente y genera la matriz estratégica de posicionamiento político.

Autor: SAIEL Intelligence System
Versión: 2.5 (Modular Orchestration SoC)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Importaciones robustas con triple nivel de fallback para soporte multi-entorno (Local, Notebook, Cloud)
try:
    from src.core.pdiv_p_sentiment import PSentimentModule
    from src.core.pdiv_d_volume import DVolumeModule
    from src.core.pdiv_i_engagement import IEngagementModule
    from src.core.pdiv_v_growth import VGrowthForecastingModule
except ImportError:
    try:
        from core.pdiv_p_sentiment import PSentimentModule
        from core.pdiv_d_volume import DVolumeModule
        from core.pdiv_i_engagement import IEngagementModule
        from core.pdiv_v_growth import VGrowthForecastingModule
    except ImportError:
        from pdiv_p_sentiment import PSentimentModule
        from pdiv_d_volume import DVolumeModule
        from pdiv_i_engagement import IEngagementModule
        from pdiv_v_growth import VGrowthForecastingModule

class PDIVCalculator:
    """
    Calculador PDIV modularizado y coordinado
    """
    
    def __init__(self, 
                 demographics_path: Optional[Path] = None, 
                 historical_votes_path: Optional[Path] = None,
                 use_api: bool = False,
                 api_url: Optional[str] = None,
                 api_key: Optional[str] = None):
        
        # Ponderaciones base lineales de la ecuación PDIV (Configurables)
        self.weights = {
            'sentiment': 0.40,    # S - Polaridad de la conversación
            'volume': 0.30,       # V - Presencia digital e impacto demográfico
            'engagement': 0.20,   # E - Involucramiento activo de la audiencia
            'growth': 0.10        # C - Inercia y aceleración temporal
        }
        
        # Instanciar submódulos independientes (Separation of Concerns)
        self.p_sentiment = PSentimentModule(use_api=use_api, api_url=api_url, api_key=api_key)
        self.d_volume = DVolumeModule(demographics_path=demographics_path)
        self.i_engagement = IEngagementModule()
        self.v_growth = VGrowthForecastingModule(historical_votes_path=historical_votes_path)
        
    def calculate_sentiment_score(self, df: pd.DataFrame) -> pd.Series:
        """Delega en el módulo P"""
        return self.p_sentiment.calculate_sentiment_score(df)
        
    def calculate_volume_score(self, df: pd.DataFrame, region: str = 'tepic') -> pd.Series:
        """Delega en el módulo D"""
        return self.d_volume.calculate_volume_score(df, region=region)
        
    def calculate_engagement_score(self, df: pd.DataFrame) -> pd.Series:
        """Delega en el módulo I"""
        return self.i_engagement.calculate_engagement_score(df)
        
    def calculate_growth_score(self, df: pd.DataFrame, days_back: int = 7) -> pd.Series:
        """Delega en el módulo V"""
        return self.v_growth.calculate_growth_score(df, days_back=days_back)
        
    def calculate_pdiv(self, df: pd.DataFrame, region: str = 'tepic') -> pd.DataFrame:
        """
        Calcula el índice PDIV completo orquestando las respuestas de todos los submódulos.
        Asegura un flujo de datos limpio, idempotente y robusto.
        """
        print(f"--- Iniciando Cálculo PDIV Modular [Región: {region}] ---")
        
        # Validar columnas mínimas indispensables
        required_columns = ['candidato', 'text']
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Faltan columnas obligatorias para el cálculo: {missing_cols}")
            
        # 1. Obtener puntuaciones de cada componente por separado
        sentiment_score = self.calculate_sentiment_score(df)
        volume_score = self.calculate_volume_score(df, region=region)
        engagement_score = self.calculate_engagement_score(df)
        growth_score = self.calculate_growth_score(df)
        
        # 2. Combinar en un único DataFrame consolidado
        # Rellenar con 50.0 (neutralidad) cualquier valor nulo resultante
        results = pd.DataFrame({
            'sentimiento_score': sentiment_score,
            'volumen_score': volume_score,
            'engagement_score': engagement_score,
            'crecimiento_score': growth_score
        }).fillna(50.0)
        
        # 3. Aplicar combinación lineal ponderada
        results['pdiv_score'] = (
            results['sentimiento_score'] * self.weights['sentiment'] +
            results['volumen_score'] * self.weights['volume'] +
            results['engagement_score'] * self.weights['engagement'] +
            results['crecimiento_score'] * self.weights['growth']
        )
        
        # Asegurar clippeo en rango formal [0 - 100]
        results['pdiv_score'] = results['pdiv_score'].clip(0.0, 100.0)
        
        # 4. Inyectar metadata y ordenar resultados por ranking
        results['region'] = region
        results['fecha_calculo'] = datetime.now().isoformat()
        results['total_menciones'] = df.groupby('candidato').size()
        
        # Clasificar por score descendente
        results = results.sort_values('pdiv_score', ascending=False)
        
        return results

    def generate_positioning_matrix(self, pdiv_results: pd.DataFrame) -> Dict:
        """
        Genera la matriz de posicionamiento estratégico clasificando candidatos en 4 cuadrantes.
        """
        if pdiv_results.empty:
            return {}
            
        avg_sentiment = pdiv_results['sentimiento_score'].mean()
        avg_pdiv = pdiv_results['pdiv_score'].mean()
        
        matrix = {
            'cuadrantes': {
                'lideres': [],      # Alto PDIV, Alto Sentimiento
                'retadores': [],    # Bajo PDIV, Alto Sentimiento  
                'vulnerables': [],  # Alto PDIV, Bajo Sentimiento
                'perdedores': []    # Bajo PDIV, Bajo Sentimiento
            },
            'metricas_global': {
                'pdiv_promedio': float(avg_pdiv),
                'sentimiento_promedio': float(avg_sentiment),
                'total_candidatos': len(pdiv_results)
            }
        }
        
        for candidato, row in pdiv_results.iterrows():
            pdiv = row['pdiv_score']
            sentiment = row['sentimiento_score']
            
            if pdiv >= avg_pdiv and sentiment >= avg_sentiment:
                matrix['cuadrantes']['lideres'].append(candidato)
            elif pdiv < avg_pdiv and sentiment >= avg_sentiment:
                matrix['cuadrantes']['retadores'].append(candidato)
            elif pdiv >= avg_pdiv and sentiment < avg_sentiment:
                matrix['cuadrantes']['vulnerables'].append(candidato)
            else:
                matrix['cuadrantes']['perdedores'].append(candidato)
                
        return matrix

    def validate_correlation(self, pdiv_results: pd.DataFrame, poll_data: Dict[str, float]) -> float:
        """
        Realiza la validación estadística de correlación de Pearson frente a encuestas reales.
        """
        common_candidates = set(pdiv_results.index) & set(poll_data.keys())
        if len(common_candidates) < 2:
            print("Advertencia: Insuficientes candidatos comunes para calcular correlación.")
            return 0.0
            
        pdiv_values = [pdiv_results.loc[candidate]['pdiv_score'] for candidate in common_candidates]
        poll_values = [poll_data[candidate] for candidate in common_candidates]
        
        correlation = np.corrcoef(pdiv_values, poll_values)[0, 1]
        
        return float(correlation) if not np.isnan(correlation) else 0.0

if __name__ == "__main__":
    # Test de humo de la orquestación consolidada
    print("--- Validación de la Orquestación Completa PDIV ---")
    
    sample_df = pd.DataFrame({
        'candidato': ['Candidato A', 'Candidato B', 'Candidato A', 'Candidato C'],
        'text': [
            'Me encanta el Candidato A, es excelente opción',
            'Ese candidato B es muy malo y mentiroso, no voten por él',
            'Hoy se realizó un debate electoral local de Tepic',
            'Votaré por el Candidato C, es honesto'
        ],
        'source': ['instagram', 'facebook', 'facebook', 'instagram'],
        'likes': [150, 4, 10, 80],
        'comments': [10, 2, 0, 5],
        'date': ['2026-05-20', '2026-05-21', '2026-05-22', '2026-05-23']
    })
    
    calculator = PDIVCalculator()
    results = calculator.calculate_pdiv(sample_df, region='tepic')
    
    print("\nResultados Consolidados del PDIV:")
    print(results[['pdiv_score', 'sentimiento_score', 'volumen_score', 'engagement_score', 'crecimiento_score']].round(2))
    
    matrix = calculator.generate_positioning_matrix(results)
    print("\nMatriz Estratégica de Cuadrantes:")
    for quad, cands in matrix['cuadrantes'].items():
        print(f" -> {quad.upper()}: {cands}")
