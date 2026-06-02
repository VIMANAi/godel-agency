# REPORTE TÉCNICO: PIPELINE DE INTELIGENCIA SAIEL v2.0

Este documento describe el flujo de datos de extremo a extremo (E2E) para el sistema de Inteligencia Política.

## 1. Arquitectura del Flujo
El pipeline ha sido rediseñado para ser **Cloud-Native**, eliminando cuellos de botella locales y garantizando escalabilidad masiva.

### Fase A: Ingesta Escalable (Apify + Cloud Run)
- **Origen:** Redes Sociales (Instagram, Facebook, TikTok).
- **Orquestador:** Un microservicio en **Cloud Run** lanza dinámicamente "Actors" de Apify.
- **Persistencia:** Los datos crudos (Raw JSON) se depositan automáticamente en un Bucket de **Google Cloud Storage (GCS)** con particionamiento por fecha y plataforma.

### Fase B: Procesamiento e Inteligencia (Vertex AI)
- **Tratamiento:** Los textos pasan por una capa de anonimización robusta (vía Crate `saiel.data_anonymizer`).
- **Inferencia:** Se utiliza **Gemini 1.5 Flash** mediante el `VertexSentimentAnalyzer` para:
  1. Extraer score de sentimiento político (-1.0 a 1.0).
  2. Identificar etiquetas (positivo, negativo, irónico).
  3. Categorizar temas (Seguridad, Economía, etc.).

### Fase C: Persistencia Analítica y Dashboarding (BigQuery)
- **Destino:** Los resultados finales del score PDIV se inyectan en tablas de **BigQuery**.
- **Consumo:** Disponibilidad inmediata para visualización en herramientas de BI (Looker Studio/PowerBI).

## 2. Gobernanza de Datos
- **Privacidad:** Implementación estricta de anonimización PII antes de cualquier análisis.
- **Auditoría:** Cada ejecución genera un "Test Report" automático que valida la paridad entre lo procesado y la teoría del manual.

---
*Certificado por el Agente Supervisor - Ecosistema SAIEL.*
