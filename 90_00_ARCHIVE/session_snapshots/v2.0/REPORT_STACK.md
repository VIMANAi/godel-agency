# REPORTE TÉCNICO: STACK TECNOLÓGICO v2.0

El ecosistema SAIEL se basa en una arquitectura de micro-componentes desacoplados, utilizando el estándar industrial de Google Cloud y Python.

## 1. Infraestructura (Google Cloud Platform)
- **Compute:** Cloud Run (Docker containers) para la ejecución serverless de extractores y pipelines.
- **Data Lake:** Cloud Storage (GCS) para el almacenamiento de archivos JSON crudos.
- **Data Warehouse:** BigQuery para el análisis de resultados PDIV a gran escala.
- **AI Engine:** Vertex AI para el procesamiento de lenguaje natural (NLP) con modelos Gemini de baja latencia.

## 2. Backend & Analytics (Python Stack)
- **Data Handling:** `Pandas` y `NumPy` para la manipulación matricial de scores.
- **Validation:** `Pydantic` para asegurar la integridad de los esquemas de datos en cada Crate.
- **NLP Core:** `Vertex AI SDK`, `Sentence-Transformers` (SBERT) y `PySentimiento`.
- **Orchestration:** `Functions-Framework` para habilitar puntos de entrada HTTP.
- **Logging:** `Structlog` para trazabilidad de eventos analíticos.

## 3. Arquitectura "Crate" (Modularidad)
El sistema abandona el modelo monolítico para adoptar el patrón **Smart Crate**:
- **Aislamiento:** Cada unidad (Extractor, Sensemaker, Calculator) tiene su propio `manifest.json`.
- **Versionamiento:** Permite actualizar el motor de Scikit-Learn sin afectar la recolección de datos.
- **Interoperabilidad:** Crates conectados mediante una Matriz de Adyacencia dinámica.

---
*Stack certificado para despliegue de Grado Gubernamental.*
