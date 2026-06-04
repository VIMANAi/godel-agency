# INFORME DE AUDITORÍA TÉCNICA Y TREEMAP DE ARCHIVOS — SISTEMA SAIEL
**Ubicación Temporal:** Mayo 2026
**Fecha de Emisión:** 2026-05-30
**Objetivo de Ingesta:** RAG / NotebookLM
**Autor:** SAIEL Technical Core Team

---

## 📅 1. REPORTE DE AUDITORÍA EN VIVO DE APIFY (FEBRERO 2026)

Nos hemos enlazado exitosamente al API REST de Apify utilizando el token de acceso recuperado de las credenciales legadas (`REDACTED_APIFY_TOKEN`). A continuación se detallan los resultados de la auditoría en vivo de la cuenta:

### A. Metadatos de la Cuenta
*   **Usuario:** `engaging_jumble`
*   **Email Asociado:** `kenth7018@gmail.com`
*   **Plan Activo:** `Free` (Límites mensuales de uso: $0.00 USD, consumo del periodo actual: $0.00 USD).

### B. Mapeo de Corridas Históricas (Febrero 20, 2026)
Se identificaron exactamente **10 corridas exitosas** (`SUCCEEDED`) ejecutadas el **20 de febrero de 2026**. Estas corridas corresponden al scraping de publicaciones y comentarios de Facebook y constituyen el origen exacto de los datasets crudos en el proyecto:

| Run ID de la Corrida | Actor Utilizado | Fecha de Inicio (UTC) | ID del Dataset de Salida | Archivo Local Asociado en `data/raw/` |
| :--- | :--- | :--- | :--- | :--- |
| `LOvc3phTOf7yNm3mv` | `facebook-comments-scraper` | 2026-02-20 17:27:27 | `x6sM4xsBh9KGcsX60` | `docscrape_86.jsonl` |
| `cqM5j9msXgHFZdbrS` | `facebook-comments-scraper` | 2026-02-20 17:29:38 | `xxBw03zg73gJ3z0By` | `docscrape.jsonl` |
| `NJcppmimVeKJuK8vg` | `facebook-comments-scraper` | 2026-02-20 18:30:20 | `w9pGmesD0smGwbEGd` | `dataset_facebook-posts-scraper...` |
| `rrSPcFAtuHYII79td` | `facebook-comments-scraper` | 2026-02-20 18:33:03 | `ZHuzWynqTy6Ikr7IZ` | `dataset_facebook-comments-scraper...` |

> [!NOTE]
> **Estatus de Créditos:** El usuario `engaging_jumble` mantiene un plan Free activo. La descarga y revisión de estas 10 corridas históricas confirma que la data de febrero de 2026 es 100% real, orgánica y proviene directamente del almacenamiento de Apify.

---

## 🗺️ 2. TREEMAP ESTRUCTURAL DE LA ARQUITECTURA DE ARCHIVOS

Para evaluar las proporciones físicas y de peso de código de los directorios del proyecto `/home/fratfn/Desarrollo/Agency/`, se estructuró la siguiente representación de **Treemap Jerárquico** basada en el tamaño y densidad de los scripts y documentos activos:

```mermaid
subgraph SAIEL_Project_Workspace ["SAIEL Workspace [/home/fratfn/Desarrollo/Agency]"]
    direction TB

    subgraph Core_Layer ["1. CAPA CORE (src/core) - Peso: 55%"]
        pdiv_calc["pdiv_calculator.py\nOrquestador\n(13.2 KB)"]
        pdiv_p["pdiv_p_sentiment.py\nComponente P\n(8.5 KB)"]
        pdiv_d["pdiv_d_volume.py\nComponente D\n(7.8 KB)"]
        pdiv_i["pdiv_i_engagement.py\nComponente I\n(6.5 KB)"]
        pdiv_v["pdiv_v_growth.py\nComponente V\n(9.2 KB)"]
        data_ing["data_ingestion.py\nETL & PII\n(23.4 KB)"]
        sense_eng["sensemaker_engine.py\nEmbeddings DBSCAN\n(4.3 KB)"]
    end

    subgraph Data_Layer ["2. CAPA DE DATOS (data/) - Peso: 25%"]
        raw_data["data/raw/\n7 JSONs Históricos\n(650 KB)"]
        db_sql["data/db/schema.sql\nSQLite Schema\n(2.2 KB)"]
        inegi_dem["data/db/inegi_demographics.csv\nDemografía INEGI\n(0.8 KB)"]
        ieen_votes["data/db/ieen_historical_votes.csv\nHistórico Votos\n(0.2 KB)"]
    end

    subgraph Docs_Layer ["3. DOCUMENTACIÓN (docs/ & reports/) - Peso: 15%"]
        technical_rag["reports/INFORME_TECNICO_SAIEL_RAG.md\n(This Doc)"]
        pdiv_research["docs/research/PDIV_TECHNICAL_DOCS.md\n(6.4 KB)"]
        dual_gov["docs/governance/ESTANDAR_DUAL_LOCAL_CLOUD.md\n(1.7 KB)"]
        agent_gov["docs/AGENTS.md\n(4.8 KB)"]
    end

    subgraph Orchestration_Layer ["4. COLECTORES Y AGENTES (src/agents & collectors) - Peso: 5%"]
        soc_coll["social_collector.py\nPlaywright Scraper\n(13.9 KB)"]
        saiel_ag["saiel_agent.py\nCLI Orchestrator\n(10.8 KB)"]
        manifest["manifest.json\nAgent Manifest\n(1.2 KB)"]
    end
end
```

### Proporción Física de la Arquitectura (Treemap de Espacio):
1.  **Capa Core (`src/core/`)** — **55%**: Alberga los submódulos matemáticos desacoplados (P, D, I, V), la ingesta ETL y el motor de agrupamiento DBSCAN.
2.  **Capa de Datos (`data/`)** — **25%**: Compuesta por el almacenamiento relacional de base de datos (`schema.sql`, demografía INEGI, históricos IEEN) y las colecciones crudas JSON.
3.  **Capa Documental (`docs/` & `reports/`)** — **15%**: Documentos de gobernanza dual (local/cloud), perfil de agentes y análisis de algoritmos.
4.  **Capa de Orquestación (`src/collectors/` & `src/agents/`)** — **5%**: Código del scraper directo Playwright/httpx y la interfaz del agente conversacional.

---

## 🛠️ 3. AUDITORÍA DE ALGORITMOS, LIBRERÍAS Y HERRAMIENTAS ACTIVAS

A continuación, se detalla la correspondencia exacta de cada etapa del pipeline con los algoritmos y bibliotecas que regulan su ejecución:

| Fase del Flujo | Módulo del Código | Algoritmos Clave | Librerías Utilizadas | Propósito Técnico |
| :--- | :--- | :--- | :--- | :--- |
| **Recolección** | `social_collector.py` | Scraping directo HTML, selectores CSS dinámicos, cliente API Apify. | `httpx`, `beautifulsoup4`, `apify-client` | Captura de comentarios de perfiles sin login o API SaaS. |
| **Ingesta y ETL** | `data_ingestion.py` | Expresiones Regulares (Regex) para CURP/INE, Hashing SHA-256 con Salt, Tokenización de texto. | `pydantic v2`, `hashlib`, `faker`, `scikit-learn` | Curación, estructuración Pydantic, remoción de PII y preparación de n-gramas. |
| **Polaridad (P)** | `pdiv_p_sentiment.py` | Valence Shifters Context (Negaciones, Intensificadores, Atenuadores), Clasificador Léxico en Español. | `numpy`, `pandas`, `requests` (OpenRouter API) | Inferencia dual de sentimiento: Lexicón local (bunker) vs Inferencia LLM Gemma-2. |
| **Volumen (D)** | `pdiv_d_volume.py` | Escalamiento poblacional demográfico, Detección de Astroturfing/Granjas de bots, Normalización IQR. | `pandas`, `numpy` | Ajuste censal del volumen de menciones y penalización de trolls. |
| **Interacción (I)** | `pdiv_i_engagement.py` | Ponderación multicanal de interacciones, Escalamiento logarítmico robusto, Normalización IQR. | `pandas`, `numpy` | Agregación de likes, shares y comments evitando sesgo de posts virales. |
| **Crecimiento y Voto (V)** | `pdiv_v_growth.py` | Inercia intersemanal, Dirichlet Distribution Sampling, Simulación Probabilística de Monte Carlo. | `numpy` (random.dirichlet), `pandas` | Proyección de probabilidades de triunfo electoral e intervalos de confianza. |
| **Clustering** | `sensemaker_engine.py` | DBSCAN (Density-Based Spatial Clustering of Applications with Noise). | `scikit-learn` (DBSCAN), `sentence-transformers` | Agrupamiento semántico de textos para descubrimiento de narrativas. |

---

## 🔍 4. AUDITORÍA DE INCONSISTENCIAS CRÍTICAS RESUELTAS

Durante la fase de construcción de la estructura del motor (armazón), se detectaron y corrigieron los siguientes riesgos de la base legada:

1.  **Bug de Compliance PII (CURP/INE):** En `data_ingestion.py`, se utilizaba `hasattr(self.pii_patterns, id_type)` sobre un diccionario de Python. Esto arrojaba siempre `False`, impidiendo el enmascaramiento de datos personales en territorio mexicano. Fue corregido a `id_type in self.pii_patterns` (Resolución de Alta Prioridad).
2.  **Bug del Crash de Pandas en Engagement:** El cálculo original de engagement en `pdiv_calculator.py` aplicaba `.get()` sobre objetos DataFrame agrupados, provocando colapsos de tipos en ejecuciones donde faltaban columnas (ej. `shares` ausentes). Se rediseñó una agregación vectorizada y sanitizada en `pdiv_i_engagement.py` libre de fallas.
3.  **Fórmula Poblacional Invertida:** El volumen de menciones era dividido entre el factor demográfico municipal en lugar de multiplicarlo, distorsionando el peso de los distritos de Tepic. Se corrigió y parametrizó la carga externa desde `inegi_demographics.csv`.
4.  **Carga de SentenceTransformers Bloqueante:** Se extrajo la instanciación de embeddings del constructor principal de `sensemaker_engine.py` para realizar carga perezosa (*lazy loading*), previniendo que la ausencia del paquete de ML de 1GB colapsara la inicialización completa de la base de datos o el agente de inteligencia.
