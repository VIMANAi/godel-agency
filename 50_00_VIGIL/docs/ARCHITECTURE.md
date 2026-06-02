# VIGIL — Arquitectura del Sistema
> Documento maestro de arquitectura del sistema Vigil.
> Proyecto: Vigil / Inteligencia Electoral Nayarit 2026.

---

## PRINCIPIO DE DISEÑO: SISTEMA AGNÓSTICO

El sistema separa **lógica del pipeline** (algoritmos, scrapers, modelos) de la
**configuración del proceso** (`config/config.yaml`).

Para auditar un nuevo municipio o candidato: solo se modifica `config.yaml`.
El código fuente no cambia.

---

## ESTRUCTURA DE DIRECTORIOS

```
vigil/
├── config/
│   ├── config.yaml             ← Configuración activa (región, candidatos, thresholds)
│   ├── mcp.json                ← Servidores MCP (filesystem, Neo4j)
│   ├── tools.yaml              ← Definición de herramientas del agente
│   └── templates/              ← Plantillas por municipio (tepic_alcalde.yaml, etc.)
│
├── data/
│   ├── raw/                    ← Datos crudos de Apify (JSONL). NUNCA modificar.
│   │   ├── facebook/
│   │   ├── ine/
│   │   ├── inegi/
│   │   └── ieen/
│   ├── silver/                 ← Datos validados y normalizados (Parquet/Polars)
│   │   ├── electoral/
│   │   ├── sociodemografico/
│   │   └── redes_sociales/
│   └── gold/                   ← Datos consolidados para reporte (escritos por SAEIL)
│
├── src/
│   ├── ingestion/              ← Orquestadores Apify, descarga APIs INE/INEGI
│   ├── processing/             ← Pipeline de validación (Polars + Pandera)
│   ├── analysis/               ← NLP (Gemini), SNA (NetworkX/Louvain) — SAEIL
│   └── graph/                  ← Neo4j queries — SAEIL
│
├── notebooks/
│   ├── 00_setup_and_config.ipynb
│   ├── 01_explore_facebook_data.ipynb   ← MVP inmediato
│   ├── 02_initial_datasets.ipynb
│   ├── 03_methodology_pipeline.ipynb
│   └── 04_electoral_intelligence_report.ipynb
│
├── docs/                       ← Documentación (Source of Truth)
│   ├── ARCHITECTURE.md         ← este archivo
│   ├── DATA_INVENTORY.md
│   ├── VIGIL_ENVIRONMENT.md
│   ├── DATA_DOWNLOAD_GUIDE.md
│   └── PIPELINE_METHODOLOGY.md
│
├── evals/                      ← Auditorías de calidad (data_integrity.json)
└── reports/                    ← Reportes semanales generados por agentes
    └── reporte_YYYYMMDD.md
```

---

## PIPELINE DE 4 FASES

```
┌─────────────────────┐     ┌─────────────────────┐     ┌───────────────────────┐     ┌──────────────────────────┐
│  FASE 1             │     │  FASE 2             │     │  FASE 3               │     │  FASE 4                  │
│  Ingesta (Apify)    │ --> │  Enriquecimiento    │ --> │  Construcción Grafo   │ --> │  Reporte Consolidado     │
│  + APIs INE/INEGI   │     │  NLP (Gemini)       │     │  (NetworkX / Neo4j)   │     │  (Auditoría Semanal .md) │
│  Batch semanal      │     │  Validación Polars  │     │  Louvain Communities  │     │  PDIV Score              │
└─────────────────────┘     └─────────────────────┘     └───────────────────────┘     └──────────────────────────┘
      Este equipo                  SAEIL                        SAEIL                        SAEIL
      raw/ → silver/           silver/ → gold/             gold/ → Neo4j               gold/ → reporte
```

---

## MÓDULOS (CRATES) DEL SISTEMA

### Módulo 1 — Ingesta y Limpieza (`src/ingestion/`)
**Responsable: Este equipo (Vigil)**

- Ingesta desde Apify: Facebook, Instagram, TikTok, YouTube
- Descarga APIs: INE padrón, INEGI Banco de Indicadores, DENUE
- Estructuración JSON → Polars DataFrame
- Filtrado inicial anti-spam (heurísticas simples)
- **Salida:** `data/raw/*.jsonl` → `data/silver/*.parquet`

### Módulo 2 — Inferencia de Postura NLP (`src/analysis/nlp/`)
**Responsable: SAEIL**

- Modelo: Gemini 2.5-flash (vía `google-genai`) con prompt especializado
- Técnica: NLI (Natural Language Inference) — no sentimiento general
- Evaluación: texto `t` frente a hipótesis `h` (tema electoral)
  - `entailment` → apoyo (+1)
  - `contradiction` → rechazo (-1)
  - `neutral` → no relacionado (0)
- **Salida:** tuplas `(id_activo, id_tema, valor_postura)`

Prompt del agente clasificador:
```
Eres un clasificador experto de discurso político.
Analiza el texto y devuelve JSON con:
  "sentiment": "positive" | "negative" | "neutral"
  "framing": "praising" | "revile" | "informative" | "troll"
  "keywords_extracted": [lista de entidades: candidatos, temas, zonas]
```

### Módulo 3 — Construcción de Espacio Vectorial (`src/analysis/matrix/`)
**Responsable: SAEIL**

- Ensambla matriz dispersa `M[usuarios × temas]`
- Imputación de NaN + centrado de medias (requisito para SVD)
- Implementación: `scipy.sparse.csr_matrix` para evitar OOM en RAM

### Módulo 4 — Topología y Reducción Dimensional (`src/analysis/topology/`)
**Responsable: SAEIL**

**Flujo 4A — PCA (Lineal):**
- Truncated SVD sobre la matriz centrada
- Extrae PC1 como "Índice General de Polarización"
- Útil para regresión predictiva y asignación de presupuestos

**Flujo 4B — UMAP + Leiden (Topológico):**
1. Proyección 2D con UMAP (topología algebraica)
2. Grafo KNN sobre proyecciones UMAP
3. Leiden para detectar comunidades (cámaras de eco, facciones)
- Aplicación: "Táctica Polis" — identificar zonas de consenso

### Módulo 5 — SNA y Grafo de Relaciones (`src/graph/`)
**Responsable: SAEIL**

**Nodos:**
- Cuentas oficiales de candidatos
- Páginas satélite / proxies de medios
- Identificadores de anunciantes compartidos

**Relaciones:**
- `SIGUE`, `RECOMPARTE`, `CO_PATROCINA` (por ID de pago de anuncios)
- `CONTENIDO_SIMILAR` (por umbral de sincronía `S_T`)

**Algoritmos:** PageRank, Betweenness Centrality, Louvain Communities

---

## GESTIÓN DEL CONOCIMIENTO

### NotebookLM (Synthesis Engine)
- Uso: análisis de documentos largos (transcripciones de debates, planes de gobierno,
  leyes estatales, auditorías)
- Integración: MCP filesystem apunta a `docs/` y `data/`

### MCP (Model Context Protocol)
- `mcp-server-filesystem` → acceso del IDE a `docs/` y `data/` en tiempo real
- Permite a los agentes de IA leer/escribir el estado de la auditoría sin RAG propio

---

## TABLAS DE INGESTIÓN DE DATOS

### Fuentes Oficiales / Territoriales

| ID Dataset | Fuente | Descripción | Formato Destino | Estado |
|---|---|---|---|---|
| DAT_INE_PADRON | INE | Lista nominal por sección, por género y edad | .parquet | PENDIENTE |
| DAT_IEE_HISTORICO | IEEN Local | Resultados históricos por casilla y sección | .parquet | PENDIENTE |
| DAT_INEGI_CENSO | INEGI | Variables AGEB/manzana (ingresos, escolaridad, conectividad) | .parquet | PENDIENTE |
| DAT_GEO_MAP | INEGI/INE | Cartografía electoral, límites geográficos | GeoJSON/SHP | PENDIENTE |

> **Prioridad crítica:** `DAT_GEO_MAP` es necesario para construir polígonos que
> filtrarán la API de anuncios de Meta.

### Ecosistema Digital (Apify)

| ID Dataset | Plataforma | Actor Apify | Variables Clave | Formato Destino | Estado |
|---|---|---|---|---|---|
| DAT_META_ADS | Meta Ad Library | facebook-ads-scraper | Gasto, segmentación, ID pagador | JSON | PENDIENTE |
| DAT_SOC_DIG_RAW | Redes Sociales | social-media-scraper | Posts, timestamps, comentarios, ER | .jsonl | FB ✅ Feb 2026 |
| DAT_NEWS_REGIONAL | Prensa Local | web-scraper | Titular, cuerpo, fecha, sentimiento | .parquet | PENDIENTE |

---

## ESQUEMAS DE DATOS SQL (Data Warehouse)

```sql
-- Tabla base de candidatos
CREATE TABLE candidatos (
    id_candidato    VARCHAR(50)  PRIMARY KEY,
    nombre          VARCHAR(255) NOT NULL,
    partido_coalicion VARCHAR(150) NOT NULL,
    cargo_postulacion VARCHAR(150) NOT NULL,
    lista_nominal_target INT DEFAULT 0
);

-- Activos digitales del ecosistema
CREATE TABLE activos_digitales (
    id_activo     VARCHAR(255) PRIMARY KEY,
    id_candidato  VARCHAR(50)  REFERENCES candidatos(id_candidato),
    plataforma    VARCHAR(50)  NOT NULL,
    url_perfil    VARCHAR(500) NOT NULL,
    es_oficial    BOOLEAN      DEFAULT FALSE,
    tipo_funcion  VARCHAR(50)  -- 'informativa','praising','ataque','clon','troll'
);
```

---

## ESQUEMA SILVER (Polars / Parquet)

Campos obligatorios en cualquier DataFrame silver:

| Campo | Tipo | Descripción |
|---|---|---|
| `id_activo` | String | ID único del activo digital |
| `plataforma` | String | facebook, instagram, tiktok, youtube |
| `texto_publicacion` | String | Texto limpio, sin PII |
| `reacciones_totales` | Int64 | Likes + shares + comentarios |
| `seguidores_cuenta_origen` | Int64 | Seguidores de la cuenta fuente |
| `tasa_interaccion` | Float64 | `reacciones / seguidores` (calculado) |
| `fecha` | Datetime | Timestamp de la publicación |
| `_fuente` | String | Metadata: origen del dato |
| `_fecha_ingesta` | Date | Metadata: cuándo se procesó |
| `is_valid` | Boolean | Pasó la compuerta de calidad |

---

## PROTOCOLOS DE COMPLIANCE

1. **Solo datos públicos** — prohibido acceder a perfiles privados, grupos cerrados o DMs
2. **Scrapers vía Apify** — respetan `robots.txt` y TOS mediante proxies residenciales
3. **Anonimización PII** — al almacenar comentarios: eliminar nombres de usuario,
   teléfonos y emails con regex antes de escribir en silver/
4. **Berkeley Protocol** — estándar de documentación de evidencia digital

---

## CONFIGURACIÓN (config.yaml) — Referencia

```yaml
metadata:
  nombre_proyecto: "Inteligencia Electoral Municipal"
  region: "Tepic, Nayarit"
  periodo_eleccion: "2026"
  version_vigil: "1.0.0"

candidatos:
  - nombre: "Candidato A"
    partido: "Partido X"
  - nombre: "Candidato B"
    partido: "Partido Y"

fuentes_monitoreo:
  paginas_facebook:
    - "url_o_id_pagina_oficial"
  medios_locales:
    - "portal_noticias_tepic"

pipeline_settings:
  ventana_analisis_dias: 7
  threshold_sincronia: 0.85       # Sensibilidad CIB (0.0 a 1.0)
  modelo_ia: "gemini-2.5-flash"
  mvd_minimo_comentarios: 50      # Mínimo viable de datos por candidato/semana

knowledge_base:
  ruta_documentos: "./data/knowledge_base/"
  idioma_reporte: "es"
```

---

## PROTOCOLO DE ACTUALIZACIÓN (Batch Semanal)

1. **Backfill Histórico** (solo una vez al iniciar):
   - Ingestar últimos 24 meses vía Apify
   - Almacenar en `data/raw/historico/`

2. **Incremento Semanal:**
   - Ingestar últimos 7 días
   - Validar con Polars + Pandera
   - Concatenar con `data/silver/historico_consolidado.parquet`

3. **Cierre de Auditoría:**
   - Generar hash SHA-256 de cada archivo silver para verificar integridad
   - Guardar reporte como `reports/reporte_YYYYMMDD.md`

---

## INSTRUCCIONES PARA AGENTES DEL IDE

1. Leer siempre `config/config.yaml` antes de iniciar cualquier proceso
2. Usar `mcp-server-filesystem` para actualizar documentos en `docs/`
3. Consultar NotebookLM para sintetizar documentos largos antes del reporte final
4. Si volumen de posts < `mvd_minimo_comentarios`, marcar periodo como
   `[DATOS_INSUFICIENTES]` y abortar NLP — no generar reporte

---

*Vigil Architecture v1.0 — Jun 2026*
