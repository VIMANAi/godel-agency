# PROVENANCE: Registro Formal de Procedencia y Trazabilidad Cronológica
**Proyecto:** SAIEL — Sistema de Análisis de Inteligencia Electoral Local
**Generado:** 2026-05-30
**Metodología:** Análisis de Series Temporales (`stat.st_mtime`) sobre el workspace `/home/fratfn/Escritorio/Agency`

---

## ⚠️ Hallazgo Principal: Inversión de Versiones por Nombre de Carpeta

El análisis temporal demostró que **el nombre de las carpetas engañaba sobre su antigüedad real**:

| Carpeta              | Última Modificación  | Estatus Real           |
|----------------------|---------------------|------------------------|
| `saiel-v2/`          | **2026-02-18**      | 🕰️ Piloto más ANTIGUO  |
| Raíz `/` (scripts)   | **2026-04-03**      | 📋 Copias intermedias   |
| `SAIEL/SAIEL_Persistence/SAIEL1/` | **2026-05-02** | ✅ Versión más RECIENTE |

> **Decisión Técnica:** El código fuente activo en `src/` fue extraído **exclusivamente** de `SAIEL1` (Mayo 2, 2026).

---

## 📋 Mapa de Archivos Duplicados y Reemplazos

| Archivo                 | Versión Archivada (Origen)                      | Última Modificación | Tamaño   | Reemplazado por (Activo)             |
|-------------------------|--------------------------------------------------|---------------------|----------|--------------------------------------|
| `apify_client.py`       | `root_duplicates/` (raíz)                       | 2026-04-03          | 0 bytes  | `src/collectors/apify_client.py`     |
| `apify_client.py`       | `legacy_saiel_v2_pilot/engine/`                 | 2026-02-18          | 0 bytes  | `src/collectors/apify_client.py`     |
| `local_sentiment.py`    | `root_duplicates/` (raíz)                        | 2026-04-03          | 3,280 B  | `src/core/local_sentiment.py` (12,930 B) |
| `local_sentiment.py`    | `legacy_saiel_v2_pilot/engine/`                 | 2026-02-18          | 3,280 B  | `src/core/local_sentiment.py`        |
| `mass_collector.py`     | `root_duplicates/` (raíz)                        | 2026-04-03          | 2,898 B  | `src/collectors/mass_collector.py` (3,381 B) |
| `mass_collector.py`     | `legacy_saiel_v2_pilot/engine/`                 | 2026-02-18          | 2,898 B  | `src/collectors/mass_collector.py`   |
| `sensemaker_engine.py`  | `root_duplicates/` (raíz)                        | 2026-04-03          | 4,563 B  | `src/core/sensemaker_engine.py` (4,352 B) |
| `sensemaker_engine.py`  | `legacy_saiel_v2_pilot/engine/`                 | 2026-02-18          | 4,563 B  | `src/core/sensemaker_engine.py`      |
| `social_collector.py`   | `root_duplicates/` (raíz)                        | 2026-04-03          | 3,116 B  | `src/collectors/social_collector.py` (3,631 B) |
| `social_collector.py`   | `legacy_saiel_v2_pilot/engine/`                 | 2026-02-18          | 3,116 B  | `src/collectors/social_collector.py` |
| `saiel_agent.py`        | `legacy_saiel_v2_pilot/engine/`                 | 2026-02-18          | 10,861 B | `src/agents/saiel_agent.py`          |
| `piloto_matriz.py`      | `legacy_saiel_v2_pilot/`                        | 2026-02-18          | 2,304 B  | `src/core/piloto_matriz.py` (2,349 B en SAIEL1) |
| `datos_piloto_matriz.json` | `legacy_saiel_v2_pilot/`                     | 2026-02-18          | 307 B    | Archivado (datos de simulación, no producción) |
| `ESTRATEGIA.md`         | `legacy_saiel_v2_pilot/`                        | 2026-02-18          | 5,728 B  | `docs/research/ESTRATEGIA.md`        |
| `FLUJO_PROYECTO.md`     | `legacy_saiel_v2_pilot/`                        | 2026-02-18          | 10,666 B | `docs/research/FLUJO_PROYECTO.md`    |
| `PERFIL_CORPORATIVO.md` | `legacy_saiel_v2_pilot/`                        | 2026-02-18          | 3,195 B  | `docs/research/PERFIL_CORPORATIVO.md`|
| `DASHBOARD_NAYARIT.html`| `legacy_saiel_v2_pilot/reports/`                | 2026-02-18          | 10,409 B | `reports/DASHBOARD_NAYARIT.html`     |

---

## 📦 Inventario de Archivos en `legacy_crates/`

Estos son los módulos experimentales del ciclo de desarrollo `v1.0 crates`. Su función fue prototipada y luego absorbida en `SAIEL1`:

| Crate                    | Archivado en               | Reemplazado por                  |
|--------------------------|----------------------------|----------------------------------|
| `crate_apify_extractor/` | `legacy_crates/`           | `src/collectors/apify_client.py` |
| `crate_data_anonymizer/` | `legacy_crates/`           | `src/core/data_ingestion.py`     |
| `crate_pdiv_calculator/` | `legacy_crates/`           | `src/core/pdiv_calculator.py`    |
| `crate_sensemaker/`      | `legacy_crates/`           | `src/core/sensemaker_engine.py`  |
| `crate_test_suite/`      | `legacy_crates/`           | `src/tests/test_pipeline.py`     |
| `saiel_v1.0_crates/`     | `legacy_crates/`           | Superseded by SAIEL1 (Mayo 2026) |

---

## 📝 Snapshots de Sesiones Archivadas

| Snapshot      | Archivado en              | Fecha Original |
|---------------|---------------------------|----------------|
| `v2.0/`       | `archive/session_snapshots/v2.0/` | 2026-04-28 |
| `v3.0/`       | `archive/session_snapshots/v3.0/` | 2026-04-29 |

Los reportes en estos snapshots (`REPORT_ALGORITHMS.md`, `REPORT_PIPELINE.md`, `REPORT_STACK.md`, `REPORT_META_GRAPH.md`, `SESSION_SNAPSHOT.md`) son copias de sesiones de trabajo anteriores y han sido superados por los reportes activos en `reports/`.

---

## 🔑 Datos Sin Reemplazar (Solo Archivados)

| Archivo                               | Ubicación Archivada         | Motivo                                           |
|---------------------------------------|-----------------------------|--------------------------------------------------|
| `system_prompt_gemini.yaml`           | `legacy_saiel1/SAIEL/`      | Config de IA — consultar para ajuste futuro de prompts |
| `knowledge_graph_manifest.json`       | (en legacy_saiel1)          | Metadatos de grafo de conocimiento               |
| `37_pending_tasks_and_roadmap.md`     | (en legacy_crates)          | Roadmap obsoleto, superado por este plan         |
| `open_interpreter_config.py`          | `src/core/` (activo)        | Se conserva en área activa por ser configuración viva |

---

*Documento generado por análisis de series temporales sobre metadatos `stat.st_mtime`.*
*Gobernanza Técnica SAIEL — Ingeniería Senior ETL/DevOps*
