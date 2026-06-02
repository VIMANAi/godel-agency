# GUÍA DE INGESTIÓN Y CONSULTAS PARA RAG / NOTEBOOKLM
**Proyecto:** SAIEL — Sistema de Análisis de Inteligencia Electoral Local  
**Ubicación Temporal:** Mayo 2026  
**Fecha de Emisión:** 2026-05-30  
**Propósito:** Cuestionario de cruce analítico e hipótesis de investigación para NotebookLM  

---

## 🧭 1. ESTRATEGIA DE INGESTIÓN EN EL CUADERNO (NOTEBOOKLM)

Para lograr un análisis de RAG de altísima calidad en tu cuaderno de **NotebookLM**, te recomendamos subir como fuentes de información los siguientes documentos en este orden:

1.  📁 **Este Documento:** `GUIA_NOTEBOOKLM_SAIEL.md` (Para dotar al modelo RAG de las preguntas y los enfoques de estudio).
2.  📁 **El Manifiesto de Auditoría:** `reports/INFORME_TECNICO_SAIEL_RAG.md` (Que provee el mapa de algoritmos, el Treemap de archivos, la auditoría en vivo de Apify de febrero de 2026 y la data cruda real).
3.  📁 **La Metodología PDIV:** `docs/research/PDIV_TECHNICAL_DOCS.md` (Que detalla el diseño matemático original).
4.  📁 **Tu Literatura Especializada (External Papers):** Sube el PDF de precampañas en México en Facebook (`docs/research/FacebookPagesandMexicanPrecampaigns _ Dmi _ Foswiki.pdf`) y cualquier otro paper de ciencia política sobre predicciones electorales.

---

## ❓ 2. CUESTIONARIO DE CRUCE ANALÍTICO (9 PREGUNTAS CLAVE)

Una vez estructurado tu cuaderno de NotebookLM con las fuentes anteriores, te recomendamos correr las siguientes preguntas para generar notas de estudio y resúmenes analíticos profundos:

### Bloque A: Detección de Bots y Astroturfing
> **Pregunta 1:**
> *¿De qué manera el algoritmo de penalización de bots de la capa D (`pdiv_d_volume.py`) de SAIEL mitiga los picos artificiales de interacción y el astroturfing en Tepic, Nayarit? Analiza si la ponderación de las variables (usuarios sospechosos, spam duplicado y likes atípicos) es metodológicamente coherente para evitar sesgos en el volumen digital de la contienda.*

> **Pregunta 2:**
> *Al comparar el paper de precampañas electorales mexicanas en Facebook (PDF) con el manifiesto técnico de SAIEL, ¿qué tan representativos son los coeficientes de canal de SAIEL (Instagram 1.0, Facebook 0.9, TikTok 0.8)? ¿Tiene sustento metodológico ponderar a Facebook con 0.9 considerando su penetración histórica en el padrón electoral general de Nayarit?*

---

### Bloque B: Robustez Estadística y Outliers
> **Pregunta 3:**
> *¿Por qué el uso conjunto de la transformación logarítmica (`np.log1p`) y el clippeo basado en el rango intercuartil (IQR) en los componentes D e I de SAIEL es una decisión de ingeniería estadística correcta para manejar la viralidad atípica en redes sociales? Explica el impacto matemático de no usar estas normalizaciones robustas.*

> **Pregunta 4:**
> *¿Cómo evalúa la función `validate_correlation` de `pdiv_calculator.py` la precisión del PDIV frente a encuestas reales? ¿Qué limitaciones matemáticas enfrentaría una simple correlación lineal de Pearson si los datos de encuestas no se calibran o si la muestra de candidatos es inferior a 5?*

---

### Bloque C: Simulación Probabilística de Voto
> **Pregunta 5:**
> *Explica el funcionamiento y fundamento matemático del Simulador de Monte Carlo electoral implementado en la capa V (`pdiv_v_growth.py`). ¿Por qué la elección de una Distribución de Dirichlet (en lugar de distribuciones normales independientes) es el estándar dorado para modelar proporciones de votos en un sistema cerrado?*

> **Pregunta 6:**
> *¿De qué manera influye la inyección del censo demográfico de población del INEGI (`inegi_demographics.csv`) y el histórico electoral del IEEN 2021 (`ieen_historical_votes.csv`) en el cálculo del "Voto Base Estimado" ($\mu_i$) del Simulador de Monte Carlo? ¿Qué hipótesis plantea el modelo sobre el peso relativo del 'voto duro' frente al 'momentum digital'?*

---

### Bloque D: Privacidad, Compliance y Escalabilidad
> **Pregunta 7:**
> *¿Cómo garantiza la capa de ingesta de datos (`data_ingestion.py`) el cumplimiento estricto de la normativa de privacidad mexicana (LGPDPPSO) durante el procesamiento de comentarios en Tepic? Analiza el impacto del bug de compliance resuelto (cambio de `hasattr` a `in` en PII) en la seguridad de datos del proyecto.*

> **Pregunta 8:**
> *A partir de las pautas descritas en `ESTANDAR_DUAL_LOCAL_CLOUD.md`, ¿cómo interactúa el agente conversacional asíncrono con las herramientas de la base de datos local SQLite y qué cambios estructurales se requieren en los metadatos y schemas para habilitar el motor de embeddings DBSCAN en la Sesión 08?*

> **Pregunta 9:**
> *Considerando las 10 corridas exitosas de Apify de febrero de 2026 auditadas en la cuenta `engaging_jumble`, ¿cuál es la coherencia temática y temporal entre las conversaciones reales extraídas (SIAPA, baches, inundaciones, detención de Galván) y el propósito analítico de la matriz de posicionamiento del PDIV?*

---

## 📊 3. ENFOQUES Y PUNTOS A DESTACAR EN TUS NOTAS DE ESTUDIO

Cuando NotebookLM genere las respuestas a estas preguntas, te sugerimos crear notas de estudio destacando:
*   **La Resiliencia en Inferencia Local (Bunker Mode):** Cómo el léxico local en español VADER-ES resuelve la ausencia de internet, complementándose de manera híbrida con las APIs de OpenRouter para inferencia contextual profunda.
*   **La Idempotencia del Pipeline:** La división de los submódulos P, D, I, V asegura que cada paso del cálculo sea replicable e independiente de fallas en los demás.
*   **La Trazabilidad de Datos (Provenance):** Toda la data cruda analizada se vincula cronológica e inequívocamente a los datasets y corridas del 20 de febrero de 2026 de la cuenta de Apify de tu proyecto.
