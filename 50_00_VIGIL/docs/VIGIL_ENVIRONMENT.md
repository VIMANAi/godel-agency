# VIGIL — Decisiones de Entorno y Stack
> Documento de arquitectura técnica. Equipo: este equipo = adquisición/normalización de datos RAW.
> Equipo SAEIL/persival = ejecución algorítmica, modelos, pipelines de producción.

---

## DIVISIÓN DE RESPONSABILIDADES ENTRE EQUIPOS

```
ESTE EQUIPO (Vigil/RndmStudio)          EQUIPO SAEIL (persival/producción)
─────────────────────────────────        ──────────────────────────────────────
Descarga de datos INE/INEGI/IEEN         Ejecución del pipeline PDIV
Scraping Facebook/IG/TikTok (Apify)      Análisis de sentimiento (pysentimiento)
Normalización y limpieza (Polars)         Clustering narrativas (sensemaker)
Generación de Parquet / JSON limpio      SNA / NetworkX / Louvain
Subida a GCS raw/ y silver/              Vertex AI embeddings
Exploración geoespacial (geopandas)      BigQuery (saeil_intel.pdiv_results)
Documentación y reportes                 Dashboard HTML / Looker Studio
```

**Implicación técnica:** Este equipo NO necesita modelos ML pesados, CUDA, Ollama,
ni librerías de deep learning. Solo necesita un entorno ligero de ETL + scraping + exploración.

---

## STACK DEFINITIVO PARA VIGIL (ESTE EQUIPO)

### CORE — Lo que se queda (justificado)

```
vigil/requirements.txt — estado final recomendado
```

| Librería | Versión mínima | Función | Justificación |
|---|---|---|---|
| `google-genai` | >=1.0.0 | Gemini API (clasificación ligera, OCR de PDFs) | Reemplaza google-generativeai deprecado |
| `polars` | >=1.0.0 | ETL — normalización, filtrado, joins | 10-100x más rápido que pandas para CSV grandes del INEGI |
| `pyarrow` | >=16.0.0 | Serialización Parquet | Backend de Polars; formato de intercambio con SAEIL |
| `apify-client` | >=1.7.0 | Scraping Facebook/IG/TikTok/YT | Actores pre-hechos, sin mantener scrapers propios |
| `networkx` | >=3.3 | SNA exploratorio | Grafo de menciones/páginas para exploración previa |
| `python-louvain` | >=0.16 | Comunidades (exploración) | Detección de clusters antes de enviar a SAEIL |
| `geopandas` | — | Cartografía INEGI, secciones electorales | Cruzar resultados electorales con AGEB/manzanas |
| `folium` | — | Mapas interactivos HTML | Visualización territorial rápida |
| `pyyaml` | >=6.0 | Lectura config.yaml | Configuración del proyecto |
| `python-dotenv` | >=1.0.0 | Variables de entorno (.env) | API keys seguras |
| `jupyter` + `ipykernel` | >=1.1.0 | Notebooks | Exploración interactiva |
| `pandera` | — | Validación de esquemas | Gate de calidad antes de subir a GCS/SAEIL |
| `requests` | — | Descargas HTTP directas (APIs INEGI/INE) | Descarga de datasets |

### A AGREGAR (no estaban en requirements.txt)

| Librería | pip install | Función | Por qué ahora |
|---|---|---|---|
| `geopandas` | `geopandas` | Shapefiles INEGI, secciones INE | Cruzar votos con territorio |
| `folium` | `folium` | Mapas HTML interactivos | Visualización rápida de DENUE, secciones |
| `pandera` | `pandera` | Validación de Polars DataFrames | Gate de calidad del raw antes de entregar |
| `httpx` | `httpx` | Descargas asíncronas de datasets | APIs INEGI/INE con rate limiting |
| `tqdm` | `tqdm` | Barras de progreso en descargas masivas | UX en notebooks |
| `orjson` | `orjson` | Lectura rápida de JSONL (datos Apify) | Los .jsonl de Facebook son pesados |
| `duckdb` | `duckdb` | Consultas SQL sobre Parquet/JSONL locales | Análisis exploratorio sin Polars completo |

---

### LO QUE SE DESCARTA — Y POR QUÉ

#### De SAEIL/requirements.txt (NO traer a Vigil)

| Librería | Motivo de descarte |
|---|---|
| `sentence-transformers` | Solo necesaria en SAEIL para embeddings. Pesa 2GB+ con modelos |
| `pysentimiento` | Análisis de sentimiento → tarea de SAEIL. Requiere CUDA/MPS ideal |
| `transformers` | Dependencia pesada. Vigil usa Gemini API, no modelos locales |
| `ollama-python` | Ollama es el fallback local de SAEIL. No aplica aquí |
| `great-expectations` | Reemplazado por `pandera` (más ligero, integración Polars nativa) |
| `faker` + `presidio` + `cryptography` | Anonimización → tarea de SAEIL antes de persistir en BQ |
| `prometheus-client` + `structlog` | Monitoreo de producción → SAEIL |
| `schedule` | Cron jobs de producción → SAEIL |
| `sqlalchemy` + `sqlite3` | SAEIL usa BigQuery; aquí usamos DuckDB para exploración |
| `pytest` + `pytest-cov` + `black` + `flake8` | Diferir — no hay tests formales en MVP de datos |
| `psutil` | Monitoreo de sistema → no necesario |
| `MLflow` / `DVC` | Versionado de modelos → SAEIL |

#### Del inventario de Naydatabases.txt (herramientas a descartar completamente)

| Herramienta | Razón |
|---|---|
| `tensorflow` / `PyTorch` / `keras` | Deep learning. No corresponde a este equipo |
| `Airflow` / `Prefect` / `Luigi` / `Dagster` | Orquestación de producción → SAEIL o fase 3 |
| `CatBoost` / `LightGBM` / `XGBoost` | ML predictivo → SAEIL |
| `AutoML` (H2O, TPOT, AutoGluon) | Modelado → SAEIL |
| `LangChain` / `LlamaIndex` / `DSPy` | LLM orchestration → usar Gemini directo vía `google-genai` |
| `CrewAI` / `AutoGen` | Agentes multi-LLM → innecesario en MVP |
| `Hugging Face Trainer` / `LoRA` / `DeepSpeed` | Fine-tuning → no aplica |
| `Looker Studio` / `PowerBI` / `Tableau` | BI para cliente → SAEIL entregables |
| `ArcGIS` / `MapInfo` | GIS propietario caro. QGIS + geopandas es suficiente |
| `Brand24` / `Hootsuite` / `Talkwalker` / `Meltwater` | Herramientas de pago para listening. Apify cubre esto |
| `Polis` / `Computation Democracy` | Plataformas de participación ciudadana. No son de análisis |
| `graph-tool` | Requiere compilación C++. NetworkX es suficiente para exploración |
| `SNAP` (Stanford) | Escala de Facebook/Twitter real. Overkill para Tepic |
| `Pajek` | Software antiguo. NetworkX + Gephi lo cubre mejor |
| `cuDF / RAPIDS` | Requiere GPU NVIDIA. No disponible |
| `Vaex` | Overkill — Polars cubre el caso de uso |
| `Modin` | Polars ya es paralelo nativo |
| `fastText` | Embeddings → SAEIL |
| `flair` | NLP embeddings → SAEIL |

---

## REQUIREMENTS.TXT FINAL RECOMENDADO

Actualizar `vigil/requirements.txt` con este contenido:

```toml
# ============================================================
# Vigil — Stack de Adquisición y Exploración de Datos
# Equipo: RndmStudio (este equipo)
# Rol: Descarga, normalización, exploración de datos raw
# Ejecutar con: pip install -r requirements.txt
# ============================================================

# --- Gemini API (clasificación ligera, OCR de PDFs) ---
google-genai>=1.0.0

# --- ETL / Core ---
polars>=1.0.0
pyarrow>=16.0.0
python-dotenv>=1.0.0
pyyaml>=6.0
orjson>=3.9.0

# --- Descarga de datos ---
httpx>=0.27.0
requests>=2.31.0
tqdm>=4.66.0

# --- Scraping ---
apify-client>=1.7.0

# --- Geoespacial ---
geopandas>=0.14.0
folium>=0.17.0
shapely>=2.0.0

# --- Exploración / SNA ---
networkx>=3.3
python-louvain>=0.16
duckdb>=1.0.0

# --- Calidad de datos ---
pandera>=0.19.0

# --- Jupyter ---
jupyter>=1.1.0
ipykernel>=6.29.0

# ============================================================
# Diferidas (equipo SAEIL — NO instalar aquí)
# ============================================================
# sentence-transformers  → embeddings (SAEIL)
# pysentimiento          → sentimiento (SAEIL)
# transformers           → modelos HF (SAEIL)
# scikit-learn           → ML (SAEIL)
# neo4j                  → grafo producción (SAEIL)
# google-cloud-bigquery  → BigQuery (SAEIL)
# google-cloud-storage   → GCS upload (SAEIL)
```

---

## HERRAMIENTAS DE ESCRITORIO (FUERA DE PYTHON)

Estas herramientas SÍ tienen valor en este equipo para exploración visual:

| Herramienta | Función | Instalación | Veredicto |
|---|---|---|---|
| **QGIS** | Visualizar SHP/GeoJSON de INEGI, secciones electorales | `sudo apt install qgis` | ✅ INSTALAR |
| **Gephi** | Visualización de grafos de red (candidatos, páginas) | Descargar gephi.org | ✅ INSTALAR |
| **DBeaver** | UI sobre DuckDB local para consultas SQL | `sudo snap install dbeaver-ce` | ✅ OPCIONAL |
| **Inkscape** | Edición de mapas SVG exportados de QGIS | `sudo apt install inkscape` | 🟡 OPCIONAL |

---

## SEPARACIÓN GCS (GOOGLE CLOUD STORAGE)

```
gs://vigil-nayarit-2026/
│
├── raw/                    ← Este equipo escribe aquí
│   ├── facebook/           ← JSONL de Apify (posts, comments)
│   ├── ine/                ← CSV/XLS descargados de INE
│   ├── inegi/              ← CSV/XLS/SHP del INEGI
│   └── ieen/               ← XLS del IEEN estatal
│
├── silver/                 ← Este equipo escribe, SAEIL lee
│   └── *.parquet           ← Polars normalizado, esquema validado por Pandera
│
├── gold/                   ← SAEIL escribe
│   └── pdiv_results/
│
└── embeddings/             ← SAEIL escribe (Vertex AI)
```

---

## DECISIÓN SOBRE EL NOTEBOOKLM-MCP-CLI

La dependencia `notebooklm-mcp-cli` en `requirements.txt` actual:
- **Mantener** si se usa NotebookLM como base de conocimiento del proyecto (útil para consultar documentos PDF de INEGI/INE dentro del flujo de trabajo)
- **Remover** si no hay integración activa con NotebookLM

**Recomendación:** mantener comentada hasta confirmar uso activo.

---

## ORDEN DE INSTALACIÓN RECOMENDADO

```bash
# 1. Crear entorno virtual limpio
python3 -m venv .venv
source .venv/bin/activate

# 2. Instalar stack base
pip install -r requirements.txt

# 3. Verificar Polars + DuckDB (los más críticos)
python -c "import polars; import duckdb; print('OK')"

# 4. Verificar geopandas (puede requerir libspatialindex)
sudo apt install libspatialindex-dev   # si falla geopandas
pip install geopandas

# 5. Verificar Gemini API
python -c "from google import genai; print('Gemini OK')"
```

---

*Documento Vigil — revisión semestral o cuando cambie la división de tareas entre equipos.*
