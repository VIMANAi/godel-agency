# Documentación Técnica - Sistema PDIV v2.0

## Resumen Ejecutivo

El sistema PDIV (Posicionamiento Digital de Intención de Voto) ha sido completamente rediseñado para cumplir con el objetivo de correlación >0.7 frente a encuestas tradicionales. Esta versión implementa una arquitectura matemática rigurosa con normalización avanzada y ajustes poblacionales.

---

## Arquitectura Matemática

### 1. Ecuación Base PDIV

```
PDIV = (S × 0.40) + (V × 0.30) + (E × 0.20) + (C × 0.10)

Donde:
S = Sentimiento Promedio Normalizado (0-100)
V = Volumen de Menciones Ajustado (0-100)
E = Engagement Ponderado (0-100)
C = Crecimiento Semanal (0-100)
```

### 2. Funciones de Normalización

#### 2.1 Sentimiento (S)
- **Entrada:** Categórico (positivo/negativo/neutro/irónico) o numérico (-1 a 1)
- **Proceso:** Mapeo a escala numérica + promedio por candidato
- **Salida:** `((promedio + 1) / 2) × 100`

#### 2.2 Volumen (V) - Ajuste Poblacional Crítico
```
V_ajustado = (V_raw / Factor_Población) × (1 - Penalización_Bots)

Factores_Población:
- Nayarit: 1.0 (1,181,052 hab)
- Tepic: 0.33 (338,058 hab)
- Xalisco: 0.05 (59,312 hab)
```

#### 2.3 Engagement (E) - Ponderación por Fuente
```
E_ponderado = Sum(Likes + Shares + Comments) × Coeficiente_Fuente

Coeficientes_Fuente (demographics):
- Instagram: 1.0 (jóvenes)
- Facebook: 0.8 (adultos)
- TikTok: 0.9 (mixto)
- Twitter: 0.7 (bajo impacto electoral)
- YouTube: 0.6 (bajo engagement directo)
```

#### 2.4 Crecimiento (C)
```
C = ((Menciones_Semana_Actual - Menciones_Semana_Anterior) / Menciones_Semana_Anterior + 1) / 2 × 100
```

### 3. Detección de Bots y Penalizaciones

#### 3.1 Umbrales de Detección
- **Máximos likes por post:** 1,000
- **Máximos comentarios por usuario:** 50
- **Ratio de spam:** >30% textos idénticos

#### 3.2 Fórmula de Penalización
```
Penalización_Total = min(
    (Usuarios_Sospechosos / Total_Usuarios) × 0.3 +
    (Posts_HighLikes / Total_Posts) × 0.2 +
    (Textos_Spam / Total_Textos) × 0.1,
    0.8
)
```

---

## Flujo de Datos Optimizado

```
1. RECOLECCIÓN (social_collector.py)
   - Apify API scraping
   - Estandarización de campos
   - Detección inicial de spam

2. ANÁLISIS DE SENTIMIENTO (local_sentiment.py)
   - Ollama + DeepSeek-R1:7b
   - Procesamiento batch (10 registros)
   - Clasificación: positivo/negativo/neutro/irónico

3. DESCUBRIMIENTO DE NARRATIVAS (sensemaker_engine.py)
   - Sentence Transformers embeddings
   - KMeans clustering (k=5)
   - Identificación automática de temas

4. CÁLCULO PDIV (pdiv_calculator.py)
   - Normalización robusta (IQR-based)
   - Ajustes poblacionales
   - Penalización por bots

5. PIPELINE INTEGRADO (pdiv_pipeline.py)
   - Orquestación completa
   - Validación de datos
   - Generación de reportes
```

---

## Mejoras Matemáticas Implementadas

### 1. Normalización Robusta con IQR
```python
def _robust_min_max_normalize(self, series: pd.Series) -> pd.Series:
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1

    # Detectar outliers
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    # Clippear valores atípicos
    series_clipped = series.clip(lower_bound, upper_bound)

    # Normalización estándar
    return ((series_clipped - series_clipped.min()) /
            (series_clipped.max() - series_clipped.min())) * 100
```

### 2. Transformación Logarítmica para Engagement
```python
# Maneja outliers en engagement masivo
engagement_log = np.log1p(engagement_weighted)
```

### 3. Validación Estadística
```python
def validate_correlation(self, pdiv_results: pd.DataFrame,
                        poll_data: Dict[str, float]) -> float:
    # Correlación de Pearson para validación
    correlation = np.corrcoef(pdiv_values, poll_values)[0, 1]
    return correlation if not np.isnan(correlation) else 0.0
```

---

## Problemas Resueltos vs Sistema Anterior

| Problema | Sistema Anterior | Sistema Nuevo |
|----------|------------------|---------------|
| **Normalización Incorrecta** | División simple por max | Normalización robusta IQR |
| **Sin Ajuste Poblacional** | Volumen crudo | Factores INEGI por región |
| **Sin Ponderación por Fuente** | Todos iguales | Coeficientes demographics |
| **Sin Detección de Bots** | Volumen contaminado | Penalización hasta 80% |
| **Overflow/NaN** | Sin manejo | Validación y clippering |
| **Hardcoding Rutas** | Windows-only | Multi-plataforma dinámico |
| **Sin Validación** | Sin correlación | Validación estadística |

---

## Especificaciones Técnicas

### Rendimiento
- **Procesamiento:** <5 min para 1000 comentarios
- **Memoria:** <2GB para datasets medianos
- **Precisión objetivo:** >85% sentimiento, >0.7 correlación PDIV

### Compatibilidad
- **Python:** 3.11+
- **Dependencias:** pandas, numpy, scikit-learn, sentence-transformers
- **Modelos locales:** Ollama (deepseek-r1:7b)
- **SO:** Windows/Linux (Parrot OS)

### Seguridad y Compliance
- **Procesamiento:** 100% local (on-premise)
- **Privacidad:** Anonimización automática
- **Compliance:** LGPDPPSO, GDPR, Berkeley Protocol

---

## Guía de Uso

### 1. Ejecución Pipeline Completo
```bash
cd engine/
python pdiv_pipeline.py
```

### 2. Cálculo PDIV Individual
```python
from pdiv_calculator import PDIVCalculator

calculator = PDIVCalculator()
results = calculator.calculate_pdiv(df, region='tepic')
```

### 3. Validación con Encuestas
```python
poll_data = {'Candidato A': 45.2, 'Candidato B': 38.1}
correlation = calculator.validate_correlation(results, poll_data)
```

---

## Métricas de Éxito

### KPIs Técnicos
- [ ] Precisión sentimiento >85%
- [ ] Tiempo procesamiento <5min/1000 comentarios
- [ ] Correlación PDIV vs encuestas >0.7
- [ ] Detección de bots >90%

### KPIs de Negocio
- [ ] Decisiones basadas en datos reales
- [ ] Reducción de intuición no fundamentada
- [ ] ROI >30% vs métodos tradicionales

---

## Roadmap de Implementación

### Fase 1: Validación (Semanas 1-2)
- [ ] Test con datos históricos
- [ ] Validación correlación encuestas
- [ ] Ajuste de coeficientes

### Fase 2: Producción (Semanas 3-4)
- [ ] Integración con recolección automática
- [ ] Dashboard en tiempo real
- [ ] Alertas de crisis

### Fase 3: Escalabilidad (Mes 2)
- [ ] Multi-región
- [ ] Optimización de performance
- [ ] API REST para integraciones

---

*Documento técnico generado por SAIEL Intelligence System*
*Versión: 2.0 | Fecha: 2026-04-22*
