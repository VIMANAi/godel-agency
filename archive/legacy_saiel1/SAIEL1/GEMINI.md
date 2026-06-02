# SAIEL Project Rules

Este Crate gestiona la Inteligencia Política de SAIEL CONSULTORIA.

## 🛠 Estándares
- **Rutas:** Utilizar siempre rutas relativas al `base_path` definido en `manifest.json`.
- **Inteligencia:** Priorizar el uso de **Vertex AI (Gemini 1.5 Flash)** para análisis de sentimiento masivo.
- **Persistencia:** Todos los resultados finales deben subirse a **BigQuery** (`saiel_intel.pdiv_results`).

## 📁 Estructura
- `engine/core/`: Scripts de procesamiento.
- `data/`: Datos crudos y procesados locales.
- `reports/`: Documentos ejecutivos.

---
*Gobernado por el Grafo de Grafos.*
