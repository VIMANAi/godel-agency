# Informe Técnico de Auditoría: Evolución del Repositorio `godel-agency`

**Clasificación:** Confidencial — Dirección Técnica / CTO  
**Fecha de Generación:** 2026-06-03  
**Período Auditado:** 2026-06-02 (commit inicial) → 2026-06-03 (estado actual)  
**Repositorio:** `VIMANAi/godel-agency`  
**Rama Principal Analizada:** `main` (via branch `copilot/generar-informe-tecnico-completo`)  
**Enfoque:** MLOps · DevSecOps · Platform Engineering · Auditoría Senior  

---

## Resumen Ejecutivo

El repositorio `godel-agency` es la segunda generación formalizada del sistema **SAIEL** (Sistema de Análisis de Inteligencia Electoral Local), rebautizado operativamente como **Godel Agency** en su versión `2.0`. El proyecto tiene como propósito central la construcción de un *war room* digital de inteligencia política para el proceso electoral de Nayarit 2026, orientado al monitoreo multicanal de candidatos con base en análisis de sentimiento, volumen de menciones, engagement y tendencias de crecimiento, sintetizados en el índice propietario **PDIV** (Posicionamiento Digital de Intención de Voto).

La actividad registrada en el repositorio es extremadamente reciente y concentrada: **todos los commits ocurrieron en una ventana de menos de 28 horas** el 2 y 3 de junio de 2026. El historial refleja una migración y formalización acelerada desde un entorno de desarrollo local privado (`/home/fratfn/Escritorio/Agency`) hacia un repositorio público en GitHub, acompañada de un ciclo rápido de revisión de código apoyado por múltiples agentes de IA (Google Jules, Gemini Code Assist, GitHub Copilot Autofix).

**Hallazgos críticos de seguridad:** El commit de seguridad identificado como `3a1acdf` (redacción de tokens Apify) resultó ser un commit vacío desde la perspectiva del diff textual, lo que sugiere que la exposición de credenciales fue detectada y gestionada, pero la evidencia en el historial no es concluyente. Por otro lado, se detectó que toda la capa de agentes (`10_00_SRC/10_20_AGENTS/`) contiene rutas absolutas hardcodeadas (`/home/fratfn/Desarrollo/godel-core`) que la hacen **completamente no ejecutable** en cualquier entorno que no sea la máquina del desarrollador original.

**Señal de madurez:** El uso de agentes de IA como co-autores (Jules bot, Gemini Code Assist, Copilot Autofix) dentro del mismo sprint de publicación demuestra una postura MLOps moderna y un flujo de mejora continua asistida. Sin embargo, el patrón de revert inmediato de los cambios de documentación del bot Jules (PR #1 → Revert en PR #3) indica fricciones en la confianza hacia la automatización y control de calidad insuficiente antes de mergear.

---

## Contexto General del Repositorio

### Propósito del Sistema

El sistema SAIEL/Godel es una plataforma de **inteligencia electoral local** diseñada para:

1. **Recolectar** datos de redes sociales (Instagram, Facebook) mediante scrapers Apify.
2. **Procesar** y anonimizar los datos (pipeline ETL con Pydantic, presidio-analyzer, structlog).
3. **Analizar** el sentimiento de comentarios políticos mediante LLMs locales (Ollama + DeepSeek-R1:7b) o en nube (Gemini Flash vía OpenRouter).
4. **Calcular** el índice PDIV multicomponente de posicionamiento digital de candidatos.
5. **Generar** reportes estratégicos HTML/Markdown para consultoría política.

El proyecto está enmarcado en el proceso electoral de **Nayarit 2026**, con foco en candidatos de la **Alcaldía de Tepic** (Beatriz Estrada, Geraldine Ponce, Andrea Navarro, Adahán Casas, Alejandro Galván) y aspirantes a la **Gubernatura 2027** (Pavel Jarero, Héctor Santana, Geraldine Ponce, Elizabeth López Blanco, Jazmín Bugarín).

### Equipo y Actores del Repositorio

| Actor | Tipo | Rol Identificado |
|---|---|---|
| `fratfn` | Humano (propietario original) | Autor del commit inicial, responsable de seguridad inicial |
| `David Cambero` (`VIMANAi`) | Humano (mantenedor activo) | Merge de PRs, correcciones manuales post-refactor |
| `google-labs-jules[bot]` | Agente IA (Google) | Refactor automatizado de código, mejoras de documentación |
| `gemini-code-assist[bot]` | Agente IA (Google) | Co-autor en fixes de pdiv_i_engagement y mass_collector |
| `Copilot Autofix` | Agente IA (GitHub) | Sugerencias de code review aplicadas en PR #4 |

---

## Estructura General Detectada

El repositorio adopta un sistema de numeración jerárquico tipo **Zettelkasten** como convención de organización, lo cual es una decisión arquitectónica inusual pero deliberada:

```
godel-agency/
├── 00_00_00_INDEX.md            ← Índice maestro de navegación del repo
├── .env.example                 ← Plantilla de configuración segura
├── .gitignore                   ← Configuración de exclusiones
├── Cargo.toml                   ← Manifiesto Rust (declarativo, sin código Rust activo)
├── pyproject.toml               ← Manifiesto Python moderno (PEP 517/518)
├── requirements.txt             ← Dependencias explícitas de producción
├── README.md                    ← Documentación principal (con paths obsoletos)
├── agency_structure_index.json  ← Índice estructural del agente
├── agent.md                     ← Manual cognitivo global para agentes IA
│
├── 10_00_SRC/                   ← CÓDIGO FUENTE ACTIVO
│   ├── 10_10_CORE/              ← Motores analíticos (PDIV, sentimiento, ETL)
│   ├── 10_20_AGENTS/            ← Capa agéntica (ROTA — ver análisis)
│   │   └── 10_20_10_CONFIG/     ← Thin adapters a godel-core (ROTA)
│   ├── 10_30_COLLECTORS/        ← Scrapers OSINT (Apify, Instagram, Facebook)
│   ├── 10_40_DEPLOY/            ← Docker + Cloud Run + scripts
│   └── 10_50_TESTS/             ← Suite de pruebas de integración
│
├── 20_00_DATA/                  ← DATOS (¡PROBLEMA: datos reales en repo!)
│   ├── 20_10_RAW/               ← Datasets crudos JSONL/JSON de redes sociales
│   ├── 20_20_PROCESSED/         ← Datos analizados: matrices PDIV, análisis
│   └── 20_30_DB/                ← Schema SQL, datos históricos electorales
│
├── 30_00_NOTEBOOKS/             ← Jupyter Notebooks
├── 40_00_DOCS/                  ← Documentación técnica y gobernanza
│   ├── 40_10_GOVERNANCE/        ← Estándares, auditoría, compliance
│   ├── 40_20_MANUALS/           ← Manuales operativos
│   └── 40_30_RESEARCH/          ← Estrategia, investigación, arquitectura
│
├── 50_00_VIGIL/                 ← SUB-PROYECTO VIGIL (semi-autónomo)
│   ├── src/                     ← Pipeline Lakehouse (raw/silver/gold)
│   ├── config/config.yaml       ← Configuración declarativa (bien diseñada)
│   └── notebooks/               ← Notebooks (solo 1 de 6 implementado)
│
├── 80_00_OUTPUTS/               ← Reportes generados (HTML, MD)
│
└── 90_00_ARCHIVE/               ← Histórico de versiones SAIEL v1 y v2
    ├── legacy_saiel1/           ← SAIEL v1.0 (Mayo 2026, más reciente real)
    ├── legacy_saiel_v2_pilot/   ← SAIEL v2 pilot (Feb 2026, más antiguo real)
    ├── legacy_crates/           ← Módulos experimentales "crates"
    ├── root_duplicates/         ← Copias de archivos raíz archivadas
    └── session_snapshots/       ← Snapshots v2.0 y v3.0 de sesiones de trabajo
```

> **Observación arquitectónica:** Existe una dualidad estructural: la estructura "activa" está en `10_00_SRC/` pero también existe un directorio `src/` en la raíz (sin numeración) que duplica parcialmente los colectores y el core. Este doble mapping genera ambigüedad en imports y fue la fuente de bugs corregidos en el PR #4.

---

## Línea de Tiempo Detallada de Modificaciones

### Fase 0: Pre-Historia (Febrero 2026 → Mayo 2026) — Fuera del Historial Git

Documentada en `90_00_ARCHIVE/PROVENANCE.md` mediante análisis de timestamps del filesystem. La evolución pre-GitHub fue:

- **Feb 2026:** `saiel-v2` (piloto más antiguo real, a pesar del nombre). Arquitectura básica de scrapers Apify y engine de análisis rudimentario.
- **Apr 2026:** Copias intermedias en raíz del filesystem. Refactor parcial.
- **May 2026:** `SAIEL1` (el código más reciente y activo). Introducción de la arquitectura modular con separación de componentes PDIV.

El equipo documentó una "inversión de versiones por nombre de carpeta": el código más nuevo estaba en la carpeta con nombre más antiguo (`SAIEL1`) y el código más viejo en la carpeta con nombre más reciente (`saiel-v2`). Esta documentación en `PROVENANCE.md` es una decisión de gobernanza técnica madura.

---

### Commit 1 — `944bc01` | 2026-06-02 17:56 | `fratfn`

**Mensaje:** `Initial commit: Prepare Agency repository for GitHub with dynamic paths, root agent.md, Cargo.toml, pyproject.toml, and .gitignore`

**Alcance:** Commit masivo de fundación. Incluye la totalidad del repositorio: ~200+ archivos.

**Archivos y Decisiones Clave:**
- Se estableció la estructura numerada `10_00_SRC/`, `20_00_DATA/`, `30_00_NOTEBOOKS/`, etc.
- Se creó `.env.example` con documentación de variables: `SAIEL_ENGINE_MODE`, `APIFY_TOKEN`, `GOOGLE_APPLICATION_CREDENTIALS`, `SAIEL_PROJECT_ID`.
- Se añadió `Cargo.toml` (Rust) con `[dependencies]` vacías, señalizando intención de módulos Rust futuros.
- Se incluyeron `__pycache__/` con archivos `.pyc` — señal de que el `.gitignore` no fue aplicado correctamente en el commit inicial.
- Se comprometieron datos reales de scraping: `dataset_facebook-comments-scraper_2026-02-20_18-34-36-980.jsonl`, `raw_instagram_COHJ9TSnfT6.json`, `raw_instagram_geraldine.json`.
- Se comprometieron matrices PDIV procesadas: `matrix_latest.json`, `matriz_gubernatura_real.json`, `matriz_tepic_real.json`.
- Se incluyeron datos electorales históricos: `ieen_historical_votes.csv`, `inegi_demographics.csv`, `electoral_polls.csv`.

**Impacto Técnico:** El commit inicial **mezcla código, configuración, datos reales y archivos de caché** en una sola operación. Es comprensible en una migración acelerada desde entorno local a GitHub, pero representa una deuda de higiene de repositorio significativa.

**Riesgo de Seguridad:** Los datos de usuarios de redes sociales (incluso si están parcialmente anonimizados) almacenados en el repositorio constituyen un riesgo GDPR/LGPDPPSO, especialmente considerando el contexto político sensible.

---

### Commit 2 — `3a1acdf` | 2026-06-02 18:13 | `fratfn`

**Mensaje:** `security: redact hardcoded Apify tokens in archive and scratch files`

**Alcance:** Intento de sanitización de tokens Apify expuestos en archivos de archivo y scratch.

**Análisis Técnico:**
El diff de este commit no muestra cambios textuales, lo que puede indicar:
1. Los cambios fueron exclusivamente en archivos `.pyc` (binarios), o
2. El token ya había sido reemplazado por `[REDACTED_FROM_ENV]` en el commit inicial, y este commit es un fix de limpieza sin rastro textual visible.

Revisando el código activo (`10_00_SRC/10_30_COLLECTORS/mass_collector.py`), se observa que el token se gestiona mediante:
```python
APIFY_TOKEN = os.getenv("APIFY_TOKEN", "[REDACTED_FROM_ENV]")
```

En los archivos de archivo (`90_00_ARCHIVE/`), el patrón se mantiene. Sin embargo, en archivos legacy se detectan variantes: `"TU_TOKEN_AQUI"` y `"[REDACTED_FROM_ENV]"`, lo que confirma que en versiones anteriores los tokens estaban hardcodeados y fueron reemplazados antes del commit inicial.

**Evaluación:** La acción de seguridad fue apropiada y muestra conciencia del riesgo. Sin embargo, el hecho de que existieran tokens hardcodeados en versiones anteriores (aunque ya reemplazados antes del push) es una señal de deuda de seguridad en las prácticas de desarrollo.

---

### Commits 3-4 — PR #1 y su Merge | 2026-06-02/03 18:50 | `google-labs-jules[bot]` + `David Cambero`

**Branch:** `update-readme-docs-1483628573142006933`  
**Mensaje:** `docs: improve README.md readability and clarity for contributors`

**Autor del PR:** `google-labs-jules[bot]` (Google AI coding agent), co-autorado con `VIMANAi`.

**Cambios Realizados por Jules:**
1. Añadió descripción de flujo principal al párrafo de introducción.
2. Añadió sección "Requisitos Previos" con Python >=3.10, `uv`/`pip`, Ollama y credenciales.
3. **Corrigió paths hardcodeados** en Quick Start: reemplazó `/home/fratfn/.local/bin/uv pip install -r requirements.txt --python /home/fratfn/vertex_env` por `python -m venv venv && source venv/bin/activate`.
4. Añadió sección "Cómo Contribuir".
5. Corrigió el bloque de código de ```` ``` ```` a ````text```` para Markdown correcto.

**Evaluación de los cambios:** Los cambios de Jules eran técnicamente **correctos y necesarios**. Los paths hardcodeados en el README eran un problema real de portabilidad. La adición de prerequisitos y guía de contribución mejoraba la accesibilidad del proyecto.

---

### Commits 5-6 — PR #3 (Revert) | 2026-06-02 19:16-19:20 | `David Cambero`

**Branch:** `revert-1-update-readme-docs-1483628573142006933`  
**Mensaje:** `Revert "docs: improve README.md readability and clarify execution modes"`

**Análisis del Revert:**
David Cambero decidió revertir los cambios del bot Jules menos de **30 minutos después** del merge del PR #1. Esto es una señal de que:

1. **Falta de revisión pre-merge:** Si los cambios hubiesen sido revisados correctamente, el merge no se habría realizado o el revert no habría sido necesario.
2. **Posible preferencia editorial:** El contenido puede no haberse ajustado al tono o formato deseado por el equipo.
3. **Confianza fragmentada en IA generativa:** El patrón merge-inmediato → revert-inmediato sugiere que la confianza en los cambios automáticos de documentación es baja.

**Impacto:** Al revertir, el README activo **volvió a contener los paths hardcodeados** (`/home/fratfn/vertex_env/bin/python src/agents/godel_agent.py --sdk`) que Jules había correctamente corregido. Esto significa que el README principal del repositorio **no es ejecutable en ningún entorno diferente a la máquina del desarrollador original**.

---

### Commits 7-11 — PR #4 (Refactor Polars) | 2026-06-02/03 | `google-labs-jules[bot]` + correcciones manuales

**Branch:** `refactor-improve-collectors-and-core-13188969873293089235`  
**Mensaje:** `refactor: improve type hints, docstrings and optimize core metrics with polars`

#### Commit `79d3ab5` — Jules bot: Refactor Polars

Este es el commit técnico más significativo del repositorio. Jules realizó una **reescritura parcial del pipeline PDIV** para migrar de Pandas puro a Polars lazy evaluation:

**Archivos modificados (600 inserciones, 486 eliminaciones):**

**`src/core/pdiv_i_engagement.py`** — Reescritura con Polars LazyFrame:
- Reemplazó `df.groupby().apply(lambda x: ...)` (problemático con tipos mixtos) por pipelines Polars vectorizados.
- Implementó limpieza segura de tipos en Pandas antes de la conversión a Arrow (para evitar crashes de PyArrow con tipos mixtos).
- Añadió logging estructurado con `logging.getLogger(__name__)`.
- Mantuvo compatibilidad backward convirtiendo el resultado de vuelta a `pd.Series` al finalizar.

**`src/core/pdiv_d_volume.py`** — Bot-detection con Polars:
- Vectorizó los cálculos de penalización por bots (Ataque Sybil, spam de texto, likes anormales).
- Reemplazó un loop `for candidate in candidates: c_df = df[df['candidato'] == candidate]` (O(n×m)) por joins y aggregations Polars (O(n log n) en el peor caso).
- Implementó la penalización como pipeline funcional con `.clip(0.0, 0.8)`.

**`src/collectors/mass_collector.py`** — Calidad de código:
- Añadió type hints completos (`def collect_from_post(self, post_url: str, limit: int = 20) -> List[Dict[str, Any]]`).
- Añadió docstrings profesionales a todos los métodos.
- Reemplazó `print()` por `logging.getLogger(__name__)`.
- Añadió manejo de errores específicos vs. catch-all `except Exception`.

**`src/core/local_sentiment.py`** — Logging y exception handling:
- Añadió type hints y docstrings.
- Reemplazó manejo genérico de errores en la carga de Ollama por excepciones específicas (`ConnectionError`, `OSError`).

**`requirements.txt`** — Dependencia nueva:
```
polars>=0.20.0
```

**`.gitignore`** — Corrección tardía:
```
__pycache__/
```
> **Nota:** Esta corrección llegó después de que los archivos `.pyc` ya habían sido comprometidos en el commit inicial. No elimina los existentes.

---

#### Commit `8f5c4cb` — David + Gemini Code Assist: Fix pdiv_i_engagement.py

Corrección crítica de un bug introducido por Jules en el pipeline Polars:

**Problema original (Jules):**
```python
source_df = pl.DataFrame({
    "source": list(self.source_weights.keys()),  # ← Nombre de columna incorrecto
    "weight": list(self.source_weights.values())
}).lazy()
lf = lf.join(source_df, left_on="source_lower", right_on="source", how="left")  # ← Join con nombre conflictivo
```

**Fix aplicado (David + Gemini):**
```python
source_df = pl.DataFrame({
    "source_lower": list(self.source_weights.keys()),  # ← Nombre alineado
    "weight": list(self.source_weights.values())
}).lazy()
lf = lf.join(source_df, on="source_lower", how="left")  # ← Join simple
```

También se corrigió la línea de transformación de interacciones:
```python
# Antes (Jules): Mutación implícita + rename problemático
lf = lf.with_columns(...).rename({"temp_interactions": "temp_weighted_interactions"})
# Después (Fix): Expresión con alias limpio
lf = lf.with_columns((...).alias("temp_weighted_interactions"))
```

**Evaluación:** Este bug refleja que el código generado por IA no fue testeado antes de ser mergeado. El join con columnas de nombre inconsistente habría producido resultados incorrectos en runtime (todos los pesos `null`, usando el `default` para todos los canales), afectando la precisión del cálculo del índice PDIV.

---

#### Commits `bf251bd` y `f88376c` — David + Gemini Code Assist: Fix mass_collector.py (2 commits en 16 segundos)

**Primera corrección (`bf251bd`):**
```python
# Eliminó logging.basicConfig del nivel de módulo (Jules lo había puesto incorrectamente):
- logging.basicConfig(level=logging.INFO, format='...')
  logger = logging.getLogger(__name__)
```

**Segunda corrección (`f88376c`):**
```python
# Lo reubicó correctamente en el bloque __main__:
if __name__ == "__main__":
+   logging.basicConfig(level=logging.INFO, format='...')
```

**Análisis:** `logging.basicConfig()` al nivel de módulo (fuera de `if __name__ == "__main__"`) afecta la configuración de logging del proceso completo cuando el módulo es importado por otro módulo, lo que rompería el logging estructurado con `structlog` configurado en `data_ingestion.py`. La corrección es técnicamente correcta. La separación en dos commits sugiere un proceso iterativo directo en la UI de GitHub o un error de precisión en la edición.

---

#### Commit `63c0e49` — David + Copilot Autofix: Code Review Suggestions

**Cambio 1 — Validación de token en MassCollector:**
```python
def __init__(self) -> None:
+   if not APIFY_TOKEN or "REDACTED" in APIFY_TOKEN or "TU_TOKEN" in APIFY_TOKEN:
+       raise ValueError("APIFY_TOKEN no configurado. Configura la variable de entorno APIFY_TOKEN.")
    self.client = ApifyClient(APIFY_TOKEN)
```

**Evaluación:** Excelente mejora de defensividad. Previene la instanciación del cliente Apify con un token inválido, generando un error claro en lugar de un fallo críptico en runtime.

**Cambio 2 — sys.exit → raise SystemExit:**
```python
# local_sentiment.py
- sys.exit(1)
+ raise SystemExit(1)
```

**Evaluación:** Cambio menor de estilo. `raise SystemExit(1)` es más Pythónico y permite que el código sea testeado sin realmente matar el proceso en contextos de testing. Señal de code review de calidad.

---

### Commit 12 — `96fa352` | 2026-06-02 20:45 | `David Cambero`

**Mensaje:** `Merge pull request #4 from VIMANAi/refactor-improve-collectors-and-core-...`

Merge final del PR #4 con todos los fixes aplicados. Cierra el sprint de mejora del día.

---

## Análisis por Dominios de Ingeniería

### 1. Arquitectura

**Fortalezas:**
- **Separación de Concerns (SoC)** bien aplicada en el motor PDIV: cada componente (P, D, I, V) es un módulo independiente (`pdiv_p_sentiment.py`, `pdiv_d_volume.py`, `pdiv_i_engagement.py`, `pdiv_v_growth.py`) orquestados por `pdiv_calculator.py`.
- **Arquitectura Dual Local/Cloud** claramente documentada con variables de entorno como mecanismo de conmutación (`SAIEL_ENGINE_MODE=local|cloud`).
- **Triple fallback en imports** para soporte multi-entorno (local, notebook, cloud):
  ```python
  try:
      from src.core.pdiv_p_sentiment import PSentimentModule
  except ImportError:
      try:
          from core.pdiv_p_sentiment import PSentimentModule
      except ImportError:
          from pdiv_p_sentiment import PSentimentModule
  ```
- **Subproyecto VIGIL** con arquitectura Lakehouse (raw/silver/gold) y configuración declarativa en `config.yaml`.
- **Manifiesto de Agente** (`manifest.json`) bien estructurado como contrato de integración.

**Debilidades:**
- **Duplicación de estructura de directorios:** Existe `10_00_SRC/10_10_CORE/` y también `src/core/` en la raíz. El README apunta a `src/`, el código principal vive en `10_00_SRC/`. Esto crea ambigüedad de imports y fue fuente de bugs.
- **Capa de agentes completamente no funcional fuera del entorno de desarrollo:** Todos los módulos en `10_00_SRC/10_20_AGENTS/` y `10_00_SRC/10_20_AGENTS/10_20_10_CONFIG/` son "thin adapters" que importan desde:
  ```python
  CORE_PATH = Path("/home/fratfn/Desarrollo/godel-core")
  ```
  Esta ruta **no existe en el repositorio** y nunca existirá en ningún otro entorno. La capa agéntica entera (godel_agent.py, security.py, gateway.py, orchestrator.py, etc.) está rota en producción.
- **Dependencia externa no declarada:** El repositorio `godel-core` mencionado en los adapters no existe en GitHub (o es privado) y no está referenciado en ningún archivo de configuración (`requirements.txt`, `pyproject.toml`). Esto crea una dependencia implícita crítica.
- **Cargo.toml con dependencias vacías:** La presencia de Rust es solo declarativa. No hay código Rust. Agrega complejidad sin valor actual.

### 2. Seguridad / DevSecOps

**Fortalezas:**
- **`.env.example`** bien estructurado con comentarios y sin valores reales. Patrón correcto de gestión de credenciales.
- **Validación de token en tiempo de instanciación** (Copilot Autofix en PR #4):
  ```python
  if not APIFY_TOKEN or "REDACTED" in APIFY_TOKEN or "TU_TOKEN" in APIFY_TOKEN:
      raise ValueError("APIFY_TOKEN no configurado.")
  ```
- **Módulo de anonimización** robusto en `data_ingestion.py` usando `presidio-analyzer`, `presidio-anonymizer` y `Faker('es_MX')` para PII (CURP, INE, emails, teléfonos).
- **Hashing de IDs de usuarios** y pseudonimización documentada en `AnonymizationConfig`.
- **Policy Enforcement Gateway** documentado en el security posture report con detección de prompt injection.
- **Compliance declarado:** LGPDPPSO · GDPR · Berkeley Protocol · EU AI Act (mencionado en README).

**Debilidades Críticas:**
- **Datos reales de scraping comprometidos en el repositorio** (`20_00_DATA/20_10_RAW/`): Los archivos `dataset_facebook-comments-scraper_2026-02-20_18-34-36-980.jsonl`, `raw_instagram_geraldine.json`, etc., contienen comentarios reales de usuarios de redes sociales sobre candidatos políticos. Esto es una **violación directa de LGPDPPSO y GDPR**, independientemente de si los datos están anonimizados, porque los metadatos del archivo y el contexto político los hacen sensibles.
- **Matrices PDIV con nombres reales** comprometidas (`20_00_DATA/20_20_PROCESSED/matriz_gubernatura_real.json`, `analisis_local_andrea.json`). Estos archivos contienen análisis políticos reales que podrían tener implicaciones legales.
- **Datos históricos electorales oficiales** comprometidos (`ieen_historical_votes.csv`). Dependiendo de la fuente, puede requerir atribución o restricciones de redistribución.
- **Hardcoded paths en README** (post-revert): La guía de instalación incluye rutas absolutas del entorno del desarrollador original que no aplican a ningún colaborador nuevo.
- **`__pycache__`** comprometido en el repositorio (aunque `.gitignore` fue actualizado, el daño ya está hecho en el historial).
- **Thin adapters de agentes apuntan a path local** que constituye un punto de falla silencioso: el código no falla hasta runtime con un `ImportError` difícil de diagnosticar.

### 3. Performance

**Estado Antes de PR #4:**
El cálculo de engagement (módulo I del PDIV) usaba `df.groupby().apply()` con lambdas, un patrón notoriamente lento en Pandas para operaciones que pueden vectorizarse. La detección de bots en el módulo D usaba un loop `for candidate in candidates` que escalaba O(n × m).

**Estado Después de PR #4:**
- **`pdiv_i_engagement.py`:** Migrado a Polars LazyFrame con `from_pandas()` → pipeline vectorizado → `collect()` → conversión a `pd.Series`. La transformación log robusta y normalización IQR se mantienen.
- **`pdiv_d_volume.py`:** Migrado a Polars con joins y aggregations vectorizadas para cálculo de penalizaciones por bots.

**Evaluación del trade-off:**
La migración es parcial (solo 2 de 4 módulos PDIV) y usa un patrón híbrido Pandas→Polars→Pandas que introduce overhead de conversión. Para los volúmenes de datos actuales (scraping de candidatos locales, típicamente miles de comentarios), el overhead puede superar el beneficio. La migración completa a Polars nativo (sin conversiones intermedias) sería más beneficiosa para conjuntos de datos grandes (>100k registros).

El subproyecto VIGIL sí adopta Polars nativo en toda su pipeline (`silver/` en Parquet + Polars), lo que es más consistente.

### 4. Observabilidad

**Fortalezas:**
- **Structlog configurado** en `data_ingestion.py` con output JSON, incluyendo timestamp ISO, nivel, nombre del logger, y traceback.
- **Prometheus client** declarado en `requirements.txt` (señal de intención de métricas).
- **Audit log** documentado en `40_00_DOCS/40_10_GOVERNANCE/AUDIT_LOG_SAIEL.md`.
- **Security posture report** generado programáticamente (detectado en `80_00_OUTPUTS/`).
- **Logging migrado de `print()` a `logging.getLogger(__name__)`** en mass_collector y local_sentiment (PR #4).

**Debilidades:**
- El módulo `local_sentiment.py` mantiene mezclado `print()` y `logging`: el prompt LLM y los resultados de análisis se imprimen directamente a stdout.
- No hay configuración de Prometheus activa: la dependencia está declarada pero no hay métricas instrumentadas en el código de producción analizado.
- El `AUDIT_LOG_SAIEL.md` documenta puntos de control manuales (checkboxes), no es un log automático.
- No hay trazas distribuidas (Jaeger, Zipkin, OpenTelemetry) a pesar de tener una arquitectura multi-capa.

### 5. Calidad de Código

**Antes de PR #4:**
- Type hints ausentes en colectores y módulos de sentimiento.
- Docstrings mínimos o inexistentes.
- `print()` como mecanismo de logging.
- `except Exception as e: print(f"[ERROR] {str(e)}")` como manejo de errores genérico.
- `logging.basicConfig()` a nivel de módulo (anti-patrón).

**Después de PR #4:**
- Type hints añadidos en colectores y módulos core.
- Docstrings con sección `Args/Returns` añadidos.
- `logging.getLogger(__name__)` adoptado.
- Manejo de excepciones específicas (`ConnectionError`, `OSError`) en local_sentiment.
- Validación defensiva de token en MassCollector.

**Deuda pendiente:**
- `local_sentiment.py` mantiene variables globales hardcoded (`BASE_DIR` con detección de SO):
  ```python
  if os.name == "nt":  # Windows
      BASE_DIR = Path("G:/Mi unidad/SAIEL_Inteligencia_Politica")
  else:  # Linux/Parrot
      BASE_DIR = Path.home() / "GoogleDrive/Mi unidad/SAIEL_Inteligencia_Politica"
  ```
  Este patrón es un residuo de desarrollo local que no debería existir en código de producción.
- `mass_collector.py` mantiene URLs de Instagram hardcodeadas de candidatos específicos en el bloque `if __name__ == "__main__":`.
- Sin cobertura de tests automáticos verificable (los archivos de test existen pero no hay pipeline CI/CD configurado).

### 6. MLOps / Operación de Pipelines

**Fortalezas:**
- **Separación clara de capas** en el pipeline: Colección → Ingesta/Anonimización → Análisis de Sentimiento → Cálculo PDIV → Sensemaking → Reporte.
- **Configuración de pipeline por variables de entorno** (12-Factor App).
- **Idempotencia documentada** en `PDIVPipeline.setup_paths()` con detección automática de `SAIEL_BASE_PATH`.
- **Arquitectura Lakehouse en VIGIL** (raw/silver/gold) con validación de esquemas Pandera.
- **Manifiesto de herramientas del agente** declarativo en `manifest.json`.

**Debilidades:**
- **No hay pipeline CI/CD**: No existe `.github/workflows/` con tests automáticos, linting o builds.
- **Sin gestión de dependencias fijadas**: `requirements.txt` usa rangos de versión (`>=`) sin lock file (`requirements.lock` mencionado en AUDIT_LOG pero no presente en el repositorio).
- **Sin containerización activa en la estructura principal**: El `Dockerfile` existe en `10_00_SRC/10_40_DEPLOY/` pero solo aplica al extractor de Cloud Run, no al pipeline completo.
- **Notebooks como artefactos de entrenamiento**: Los notebooks Jupyter están versionados pero sin exportación a scripts `.py` como buena práctica MLOps.
- **Sin gestión de modelos**: No hay versionado de modelos LLM ni tracking de experimentos (MLflow, W&B).

### 7. Mantenibilidad

**Fortalezas:**
- **`agent.md` en cada directorio clave** para guiar a agentes IA en la operación del módulo: decisión arquitectónica innovadora y pragmática para un proyecto con colaboración IA-humano.
- **PROVENANCE.md** como registro de procedencia formal: documenta decisiones técnicas, versiones archivadas y razones de los reemplazos.
- **Numeración jerárquica** del filesystem facilita la navegación y establece un orden de precedencia claro.
- **`agency_structure_index.json`** como índice legible por máquina de la estructura.
- **Documentación técnica del algoritmo PDIV** completa en `40_00_DOCS/40_30_RESEARCH/PDIV_TECHNICAL_DOCS.md`.

**Debilidades:**
- **La capa de agentes no es mantenible sin `godel-core`**: Ningún colaborador externo puede trabajar en `10_00_SRC/10_20_AGENTS/` sin acceso a un repositorio privado no documentado.
- **Dos estructuras de directorio paralelas** (`10_00_SRC/` vs `src/`) generan confusion sobre cuál es el código activo.
- **README desactualizado** (por el revert del PR #1): Los paths de instalación y ejecución son incorrectos para cualquier entorno que no sea el del desarrollador original.
- **Archivos `.pyc` en el historial de git**: Aunque `.gitignore` fue actualizado, los archivos ya comprometidos permanecen en el historial y pueden afectar el tamaño del repositorio.

---

## Diagnóstico Global Tipo Senior

### Madurez del Sistema: 6/10

El repositorio muestra señales de un sistema en transición rápida de "proyecto personal avanzado" a "producto de ingeniería colaborativo". La arquitectura subyacente del motor PDIV es técnicamente sólida y bien pensada desde el punto de vista matemático y de SoC. Sin embargo, la publicación en GitHub fue acelerada sin los controles de higiene mínimos necesarios para un repositorio compartido.

**Lo que se hizo bien:**
1. El diseño matemático del índice PDIV con 4 componentes independientes y ponderaciones configurables.
2. El sistema de anonimización PII con presidio-analyzer y Faker.
3. La documentación técnica del algoritmo (PDIV_TECHNICAL_DOCS.md).
4. La adopción de Polars para optimización de rendimiento (dirección correcta).
5. El uso de `agent.md` por módulo para guiar colaboración IA-humano.
6. La configuración dual local/cloud con conmutación por variable de entorno.
7. La documentación de procedencia (PROVENANCE.md).

**Lo que fue un error o riesgo:**
1. Commit de datos reales de usuarios de RRSS en el repositorio (riesgo legal/privacidad).
2. Thin adapters en la capa de agentes que dependen de un path absoluto local inexistente en producción.
3. Revert del PR #1 de Jules que restauró paths hardcodeados incorrectos en README.
4. Ausencia de CI/CD: ningún test automático en el pipeline de GitHub Actions.
5. Commit masivo inicial mezclando código, datos, caché y documentación.
6. Dependencia implícita en `godel-core` (repositorio externo no documentado ni accesible).

### Nivel de Colaboración IA: Alto (con supervisión mejorable)

El proyecto utiliza activamente 3 agentes IA diferentes (Jules, Gemini Code Assist, Copilot Autofix) en un solo sprint de publicación. Esto es un indicador de una postura MLOps/DevOps moderna. Sin embargo, el patrón observado —merge automático → bug en producción → fix manual— indica que no hay tests automáticos que actúen como puerta de calidad antes del merge.

### Deuda Técnica Acumulada: Media-Alta

La deuda más significativa es **estructural** (capa de agentes rota, dualidad de directorios, README obsoleto) más que **algorítmica** (el motor PDIV es sólido). La deuda algorítmica existente (migración Polars parcial, variables globales hardcodeadas) es manejable en 1-2 sprints.

---

## Riesgos Principales

### 🔴 Riesgo Crítico: Datos de Usuarios Reales en Repositorio Público

**Archivos afectados:**
- `20_00_DATA/20_10_RAW/dataset_facebook-comments-scraper_2026-02-20_18-34-36-980.jsonl`
- `20_00_DATA/20_10_RAW/dataset_facebook-posts-scraper_2026-02-20_17-43-56-562.jsonl`
- `20_00_DATA/20_10_RAW/raw_instagram_COHJ9TSnfT6.json`
- `20_00_DATA/20_10_RAW/raw_instagram_geraldine.json`
- `20_00_DATA/20_20_PROCESSED/analisis_local_andrea.json`
- `20_00_DATA/20_20_PROCESSED/matriz_gubernatura_real.json`

**Impacto:** Violación potencial de LGPDPPSO (Ley General de Protección de Datos Personales en Posesión de Sujetos Obligados), GDPR (si hay ciudadanos europeos), y los términos de servicio de Instagram y Facebook. En el contexto de análisis político, la exposición de opiniones de usuarios identificables puede tener consecuencias legales graves.

**Acción requerida:** Eliminar estos archivos del historial de git (no solo del working tree) usando `git filter-repo` o BFG Repo-Cleaner, y revisar el alcance del repositorio (privado vs público).

---

### 🔴 Riesgo Crítico: Capa de Agentes No Funcional en Producción

**Archivos afectados:** Todo `10_00_SRC/10_20_AGENTS/` (14+ archivos Python).

**Código roto:**
```python
CORE_PATH = Path("/home/fratfn/Desarrollo/godel-core")
if str(CORE_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_PATH))
from godel_agent import *  # ImportError garantizado en cualquier otro entorno
```

**Impacto:** El orquestador principal del sistema, el agente SAIEL, y todas las configuraciones de seguridad, gateway y orquestación son **completamente no ejecutables** en cualquier entorno que no sea la máquina del desarrollador original. Cualquier colaborador nuevo que intente ejecutar el sistema obtendrá un `ImportError` sin solución posible sin acceso al repositorio privado `godel-core`.

---

### 🟠 Riesgo Alto: README con Paths Hardcodeados (Post-Revert)

Tras el revert del PR #1, el README principal contiene:
```bash
/home/fratfn/.local/bin/uv pip install -r requirements.txt --python /home/fratfn/vertex_env
/home/fratfn/vertex_env/bin/python src/agents/godel_agent.py --sdk
```

Esto hace que la guía de instalación sea inútil para cualquier colaborador y daña la credibilidad técnica del proyecto ante revisores externos.

---

### 🟠 Riesgo Alto: Ausencia de CI/CD

Sin GitHub Actions configurado:
- Los bugs introducidos por IA (como el join incorrecto en `pdiv_i_engagement.py`) no son detectados automáticamente.
- No hay garantía de que el código en `main` esté en estado ejecutable.
- No hay linting automático (a pesar de que `flake8` y `black` están en `requirements.txt`).

---

### 🟡 Riesgo Medio: Migración Polars Parcial con Patrón Híbrido

El patrón `from_pandas() → polars lazy → collect() → to_pandas()` introduce overhead de conversión. Para datasets pequeños, puede ser más lento que Pandas puro. Si el objetivo es Polars, la migración debería ser completa; si se mantiene Pandas, el overhead de conversión no tiene justificación.

---

### 🟡 Riesgo Medio: Dependencia Implícita en godel-core (Repositorio Privado)

No documentado en `requirements.txt`, `pyproject.toml`, ni en `README.md`. El repositorio `godel-core` puede contener código crítico de negocio que no está bajo control de versiones en este repositorio.

---

## Recomendaciones Prioritarias

### Prioridad 1 — Seguridad y Cumplimiento (Inmediato)

1. **Purgar datos de usuarios del repositorio** usando `git filter-repo`:
   ```bash
   git filter-repo --path 20_00_DATA/20_10_RAW/ --invert-paths
   git filter-repo --path 20_00_DATA/20_20_PROCESSED/ --invert-paths
   ```
   Y añadir `20_00_DATA/20_10_RAW/*.jsonl`, `20_00_DATA/20_10_RAW/*.json` al `.gitignore`.

2. **Determinar si el repositorio debe ser privado**: Si contiene datos de análisis de candidatos electorales reales, considerar seriamente mantenerlo privado o separar código (público) de datos (privado/restringido).

3. **Documentar la dependencia `godel-core`**: Si es un repositorio privado, añadirlo como git submodule o documentarlo explícitamente. Si el código puede ser internalizado, hacerlo.

### Prioridad 2 — Funcionalidad y Mantenibilidad (Sprint 1)

4. **Reparar la capa de agentes** en `10_00_SRC/10_20_AGENTS/`: Reemplazar los thin adapters con el código real o documentar claramente que se requiere `godel-core` como dependencia externa.

5. **Actualizar el README** con los paths correctos (los que Jules intentó corregir en PR #1): Debería usar `python -m venv venv` y rutas relativas.

6. **Unificar la estructura de directorios**: Decidir si el código vive en `10_00_SRC/` o en `src/`, y eliminar la duplicación.

7. **Eliminar `__pycache__` del historial** o al menos asegurar que no se commiteen más:
   ```bash
   git filter-repo --path-glob '*/__pycache__/*' --invert-paths
   ```

### Prioridad 3 — Calidad y MLOps (Sprint 2-3)

8. **Implementar CI/CD** con GitHub Actions:
   - Lint con `flake8`/`black` en cada PR.
   - Tests automáticos con `pytest` en cada PR.
   - Build check del Dockerfile.

9. **Añadir `requirements.lock`** para reproducibilidad determinista del entorno (usando `pip-compile` o `uv lock`).

10. **Completar la migración Polars** o hacer rollback: No mantener el patrón híbrido. Migrar también `pdiv_p_sentiment.py` y `pdiv_v_growth.py`, o volver a Pandas puro con vectorización correcta.

11. **Eliminar variables globales hardcodeadas** en `local_sentiment.py` (detección de OS, paths absolutos) y reemplazar por dotenv + `Path(__file__).parents[]`.

12. **Completar los 5 notebooks de VIGIL** (del `01` al `05`): Actualmente solo existe `00_setup_and_config.ipynb`, los demás son planificación.

### Prioridad 4 — Deuda Técnica (Backlog)

13. **Resolver la inversión de nomenclatura** entre `10_00_SRC/10_20_AGENTS/10_20_10_CONFIG/` y los módulos de config reales.

14. **Instrumentar métricas Prometheus** activas (la dependencia está declarada pero sin uso).

15. **Formalizar política de datos**: Definir claramente qué datos pueden estar en el repositorio, cuáles en storage externo (GCS/S3), y cuáles nunca deben versionarse.

---

## Conclusión Final

El repositorio `godel-agency` representa un sistema analítico técnicamente ambicioso con un núcleo matemático bien diseñado (el motor PDIV), pero publicado en un estado que mezcla artefactos de desarrollo local con código de producción. El sprint intensivo del 2 de junio de 2026 logró varios avances reales: la migración parcial a Polars, la mejora de type hints y logging, la validación defensiva de tokens, y el refactoring del manejo de excepciones.

Sin embargo, los tres problemas fundamentales que deben abordarse con urgencia son:
1. **Los datos de usuarios de redes sociales están en el repositorio** — riesgo legal inmediato.
2. **La capa de agentes está rota** — riesgo operativo crítico para quien intente usar el sistema.
3. **El README está desactualizado con paths del desarrollador original** — barrera de entrada para cualquier colaborador.

El uso de múltiples agentes IA para code review y refactoring es una fortaleza estratégica, pero requiere como contrapeso obligatorio un pipeline de tests automáticos que actúe como puerta de calidad. Sin CI/CD, los bugs introducidos por IA solo se detectan en producción o mediante revisión manual reactiva, como se observó con el fix del join Polars en `pdiv_i_engagement.py`.

El proyecto tiene el potencial de ser una referencia técnica sólida en el espacio de inteligencia electoral computacional. Con las correcciones prioritarias descritas, puede alcanzar un nivel de madurez apto para un equipo de ingeniería formal.

---

## Anexo Cronológico de Commits

| # | Hash | Fecha (UTC-6) | Autor | Tipo | Descripción |
|---|---|---|---|---|---|
| 1 | `944bc01` | 2026-06-02 17:56 | fratfn | feat | Commit inicial masivo: estructura completa del repositorio, ~200+ archivos |
| 2 | `3a1acdf` | 2026-06-02 18:13 | fratfn | security | Redacción de tokens Apify en archivos de archivo y scratch |
| 3 | `9edc72a` | 2026-06-03 00:33 UTC | google-labs-jules[bot] | docs | Mejoras de README: fix paths, sección prerequisites, guía de contribución (PR #1) |
| 4 | `325d12c` | 2026-06-02 18:50 | David Cambero | merge | Merge de PR #1 (docs README) |
| 5 | `0d8eb38` | 2026-06-02 19:16 | David Cambero | revert | Revert de PR #1 — restaura README con paths hardcodeados |
| 6 | `6b601f3` | 2026-06-02 19:20 | David Cambero | merge | Merge de PR #3 (revert del PR #1) |
| 7 | `79d3ab5` | 2026-06-03 02:33 UTC | google-labs-jules[bot] | refactor | Migración a Polars (pdiv_i_engagement, pdiv_d_volume, mass_collector, local_sentiment) |
| 8 | `8f5c4cb` | 2026-06-02 20:41 | David Cambero + gemini-code-assist | fix | Corrección de bug en join Polars de pdiv_i_engagement.py |
| 9 | `bf251bd` | 2026-06-02 20:42 | David Cambero + gemini-code-assist | fix | Corrección de logging.basicConfig en mass_collector (remove from module level) |
| 10 | `f88376c` | 2026-06-02 20:42 | David Cambero + gemini-code-assist | fix | Reubicación de logging.basicConfig en bloque __main__ |
| 11 | `63c0e49` | 2026-06-02 20:44 | David Cambero + Copilot Autofix | fix | Validación defensiva de APIFY_TOKEN; raise SystemExit vs sys.exit |
| 12 | `96fa352` | 2026-06-02 20:45 | David Cambero | merge | Merge de PR #4 (refactor Polars + fixes) |

---

## Anexo de PRs Relevantes

### PR #1 — `update-readme-docs-1483628573142006933`
- **Estado:** Mergeado y luego revertido
- **Autor:** google-labs-jules[bot] (co-autor: VIMANAi)
- **Fecha Merge:** 2026-06-02 18:50
- **Cambios:** README.md (+44 líneas, -19 líneas)
- **Acciones Clave:**
  - Fix de paths hardcodeados en Quick Start (`/home/fratfn/...` → rutas relativas)
  - Adición de sección "Requisitos Previos"
  - Adición de sección "Cómo Contribuir"
  - Corrección de bloque de código markdown
- **Decisión de Revert:** 30 minutos post-merge, por David Cambero vía PR #3
- **Evaluación:** Los cambios eran técnicamente correctos. El revert fue una decisión editorial, no técnica, y resultó en una regresión de calidad en la documentación.

---

### PR #3 — `revert-1-update-readme-docs-1483628573142006933`
- **Estado:** Mergeado
- **Autor:** David Cambero
- **Fecha Merge:** 2026-06-02 19:20
- **Cambios:** README.md (revert completo al estado del commit `3a1acdf`)
- **Impacto:** El README volvió a contener:
  ```bash
  /home/fratfn/.local/bin/uv pip install -r requirements.txt --python /home/fratfn/vertex_env
  /home/fratfn/vertex_env/bin/python src/agents/godel_agent.py --sdk
  ```
- **Evaluación:** Regresión documentada. Pendiente de corrección manual.

---

### PR #4 — `refactor-improve-collectors-and-core-13188969873293089235`
- **Estado:** Mergeado con 4 commits de corrección post-refactor
- **Autor:** google-labs-jules[bot] + David Cambero (con Gemini Code Assist y Copilot Autofix)
- **Fecha Merge:** 2026-06-02 20:45
- **Archivos Modificados:** 6 archivos (600 inserciones, 486 eliminaciones en el commit de Jules)
- **Contenido:**
  - `pdiv_i_engagement.py`: Migración Polars lazy + fix de bug de join de columnas
  - `pdiv_d_volume.py`: Bot detection vectorizado con Polars
  - `mass_collector.py`: Type hints, docstrings, logging, validación de token, fix de logging.basicConfig
  - `local_sentiment.py`: Type hints, docstrings, exception handling específico, raise SystemExit
  - `requirements.txt`: Adición de `polars>=0.20.0`
  - `.gitignore`: Adición de `__pycache__/` (tardía)
- **Bugs Encontrados Post-Merge:** 1 bug de join Polars (columna `"source"` vs `"source_lower"`), 1 bug de logging.basicConfig a nivel de módulo. Ambos corregidos en la misma sesión.
- **Evaluación:** PR de mayor impacto técnico del repositorio. La migración a Polars es acertada en dirección pero requiere tests para validar correctitud. El proceso de corrección iterativa post-merge (3 commits de fix en 3 minutos) es rápido pero señala la ausencia de tests automáticos.

---

*Informe generado mediante análisis exhaustivo del historial de git, revisión de código fuente, documentación técnica y artefactos del repositorio `VIMANAi/godel-agency`.*  
*Enfoque: MLOps · DevSecOps · Platform Engineering · Auditoría Senior*  
*Auditor: GitHub Copilot Coding Agent — 2026-06-03*
