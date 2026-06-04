# REPORTE TÉCNICO: INTELIGENCIA ALGORÍTMICA

El sistema SAIEL integra algoritmos de vanguardia de la librería Scikit-Learn para transformar datos digitales en conocimiento político accionable.

## 1. Algoritmos en Operación

### K-Means Clustering (Sensemaker Engine)
- **Función:** Agrupamiento de comentarios en "Narrativas".
- **Mecánica:** Utiliza embeddings vectoriales de 768 dimensiones para agrupar opiniones ciudadanas con temáticas similares.
- **Uso:** Descubrimiento automático de las 5-10 preocupaciones principales de la población.

### Score PDIV (Posicionamiento Digital de Intención de Voto)
- **Fórmula:** `(S*0.4) + (V*0.3) + (E*0.2) + (C*0.1)`
- **Componentes:** Sentimiento (S), Volumen (V), Engagement (E) y Crecimiento (C).
- **Normalización:** Aplicación de `RobustScaler` (IQR) para eliminar el impacto de valores atípicos y manipulación coordinada.

## 2. Oportunidades de Expansión (Roadmap)

### Isolation Forest (Detección de Anomalías)
- **Aplicación:** Identificar ataques de "Guerra Sucia" o picos inusuales de actividad coordinada por bots.
- **Rigor:** Clasifica cada comentario como "orgánico" o "anómalo" basado en la densidad de la distribución.

### Ridge Regression (Optimización Dinámica)
- **Aplicación:** Calibración de los pesos de la fórmula PDIV.
- **Mecánica:** Entrena con datos históricos de elecciones reales para ajustar los coeficientes (0.4, 0.3, etc.) y maximizar la precisión predictiva.

### LDA - Latent Dirichlet Allocation (Tópicos)
- **Aplicación:** Identificación de palabras clave y temas subyacentes dentro de los clusters de K-Means.
- **Uso:** Ver de qué están hablando exactamente los ciudadanos sin intervención humana.

---
*Algoritmos validados mediante el Grafo de Grafos.*
