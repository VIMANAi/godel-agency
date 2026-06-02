# ESTRATEGIA: SAIEL CLOUD-NATIVE EVOLUTION

Este documento define la transición de herramientas locales a servicios administrados de Google Cloud para el proyecto de Inteligencia Política.

## 1. Mapeo de Transición

| Módulo | Local (Legacy) | Cloud (Propuesto) |
| :--- | :--- | :--- |
| **Sentimiento** | Ollama / DeepSeek | Vertex AI (Gemini 1.5 Flash) |
| **Embeddings** | SBERT (Local) | Vertex AI Text-Embeddings-004 |
| **Clustering** | Scikit-Learn (Local) | BigQuery ML (K-Means) |
| **Pipeline** | Scripts Python manuales | Google Cloud Workflows / Cloud Run |
| **Data Lake** | Carpetas `/data` | BigQuery Tables / GCS Buckets |

## 2. Ventajas del Enfoque Google
1. **Infraestructura Zero-Ops:** No más errores de "espacio en disco" o "modelo no descargado".
2. **Velocidad:** Procesamiento paralelo masivo.
3. **Escalabilidad:** De 100 comentarios a 10 millones sin cambiar el código.
4. **Seguridad:** Datos protegidos por la IAM de Google, no en archivos locales.

## 3. Registro de Nuevo Crate de Infraestructura
- **ID:** `saiel.cloud_orchestrator`
- **Componentes:**
  - `vertex_adapter.py`: Comunicación con Gemini.
  - `bq_schema.sql`: Definición de tablas de inteligencia.
  - `cloud_run_service`: Servicio HTTP para disparar el pipeline.
