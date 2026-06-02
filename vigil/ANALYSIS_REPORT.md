# REPORT DE ANÁLISIS TÉCNICO Y DISEÑO DE SISTEMA: PROYECTO VIGIL
> **Rol:** Data Analyst, ETL Engineer & System Designer Architect  
> **Fecha:** 2026-06-01 (Corte Técnico)  
> **Ubicación:** Raíz de Vigil (`/home/fratfn/Desarrollo/Agency/vigil/`)  
> **Contexto:** Proceso Electoral Nayarit 2026 (Tepic)  

---

## 1. INTRODUCCIÓN Y CONTEXTO ELECTORAL

El proyecto **Vigil** es un sistema agnóstico de adquisición, normalización, exploración y perfilamiento digital de procesos electorales locales. En el marco del proceso electoral de **Nayarit 2026**, el sistema está diseñado para monitorear y analizar de forma no invasiva la conversación digital en torno a los actores clave de la contienda por la **Gubernatura 2027** y la **Alcaldía de Tepic (Capital)**.

### Perfiles Identificados en la Demarcación:
*   **Gubernatura 2027:**
    *   **Pavel Jarero:** Consolidado con apoyo de bases ciudadanas (agenda territorial).
    *   **Héctor Santana:** Fuerte eficiencia en gestión de obra pública en el sur (Bahía de Banderas).
    *   **Geraldine Ponce:** Muy alto volumen digital, alta polarización crítica.
    *   **Elizabeth López Blanco:** Crecimiento operativo a través de estructuras partidistas.
    *   **Jazmín Bugarín:** Perfil institucional y estabilizador de alianzas.
*   **Alcaldía de Tepic (Capital):**
    *   **Beatriz Estrada:** Agenda de causa social (DIF Nayarit), posicionada con la más alta valoración positiva neta.
    *   **Adahán Casas:** Perfil legislativo y de estabilidad institucional.
    *   **Andrea Navarro:** Perfil joven de renovación de cuadros con enfoque en el Distrito 2.
    *   **Alejandro Galván:** Fuerte rechazo digital derivado de coyunturas judiciales.

---

## 2. DISEÑO Y ARQUITECTURA DE SISTEMA (SYSTEM DESIGN)

### 2.1 El Principio del Sistema Agnóstico
La premisa arquitectónica de Vigil es el **desacoplamiento total** entre la **lógica de cómputo/pipeline** (código en `src/` y `notebooks/`) y la **configuración operativa** (`config/config.yaml`). 

Para auditar un nuevo municipio, estado o cambiar la lista de candidatos monitoreados, **no se requiere alterar una sola línea de código**. Toda la parametrización (candidatos, alias, fuentes de monitoreo, umbrales de sincronía y volúmenes mínimos viables) se controla de manera declarativa en `config.yaml`.

### 2.2 Estructura del Árbol de Trabajo
El directorio del proyecto se organiza bajo la siguiente estructura modular:

```
vigil/
├── config/
│   ├── config.yaml             ← Parámetros de control activos (Candidatos, fuentes, umbrales)
│   ├── mcp.json                ← Servidores MCP para integración con IDE (Filesystem, Neo4j)
│   └── tools.yaml              ← Definición de herramientas del agente (Neo4j/Cypher)
├── data/
│   ├── raw/                    ← Zona de Ingesta Cruda. Solo lectura. Formatos JSONL/CSV
│   │   └── facebook/           ← Datos de Apify (Posts y Comentarios)
│   ├── silver/                 ← Zona de Normalización. Archivos Parquet optimizados con Polars
│   └── gold/                   ← Zona de Entrega. Datasets consolidados para reporte final
├── src/
│   ├── ingestion/              ← Orquestadores de descarga y web scrapers (Apify API, INE, INEGI)
│   ├── processing/             ← Módulo de compuerta de calidad y normalización (Polars/Pandera)
│   ├── analysis/               ← Clasificación semántica NLP (Gemini API) y topología de red
│   └── graph/                  ← Consultas y persistencia en base de datos de grafos (Neo4j)
├── notebooks/
│   └── 00_setup_and_config.ipynb ← Cuaderno de verificación de entorno y credenciales
├── docs/                       ← Especificaciones técnicas y metodológicas (Source of Truth)
├── evals/                      ← Auditoría de calidad e integridad de datos
└── reports/                    ← Reportes de inteligencia generados en Markdown
```

### 2.3 Flujo de Datos Multicapa (Data Pipeline)
El procesamiento sigue una arquitectura de datos tipo **Lakehouse** dividida en tres capas físicas:

```
[Fuentes Externas]
   │ (Apify Scrapers / APIs INEGI / INE)
   ▼
┌──────────────────────────────────────────────────────────────┐
│ 1. CAPA RAW (data/raw/)                                      │
│ - Almacena las salidas de scraping en JSONL crudo.            │
│ - Descargas directas de tabulares en CSV/Excel y cartografía.│
│ - Datos inmutables: NUNCA se editan directamente.            │
└──────────────────────────────────────────────────────────────┘
   │
   │ (processing/quality_gate.py - Motores Polars)
   ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. CAPA SILVER (data/silver/)                                │
│ - Datos limpios, estructurados y normalizados.               │
│ - Validación estricta de esquemas vía Pandera.               │
│ - Formato: Apache Parquet (tipado fuerte, compresión Snappy).│
└──────────────────────────────────────────────────────────────┘
   │
   │ (analysis/semantic_agent.py & graph/ - Vertex AI / Neo4j)
   ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. CAPA GOLD (data/gold/)                                    │
│ - Índices agregados (PDIV, CAR, CIB, AD).                    │
│ - Estructuras relacionales listas para visualización y grafos│
└──────────────────────────────────────────────────────────────┘
```

### 2.4 Integración de Infraestructura y Gobernanza
*   **Google Cloud Storage (GCS):** El almacenamiento remoto se estructura en buckets paralelos a las capas locales (`gs://vigil-nayarit-2026/raw/`, `silver/`, `gold/`). El equipo **RndmStudio** es responsable de poblar e integrar la capa `raw` y `silver`, mientras que el equipo **SAEIL** consume `silver` para generar la capa `gold`.
*   **Base de Datos de Grafos (Neo4j):** Utilizada para modelar la red de activos digitales. Los **Nodos** representan Candidatos, Activos Digitales (páginas) e Identificadores de Anunciantes de Meta. Las **Relaciones** modelan el flujo de información: `SIGUE`, `RECOMPARTE`, `CO_PATROCINA` (anunciantes compartidos) y `CONTENIDO_SIMILAR` (detección de bots).
*   **Model Context Protocol (MCP) & NotebookLM:** Integración del IDE mediante `mcp-server-filesystem` para permitir que los agentes lean la documentación en `docs/` en tiempo real. Se utiliza NotebookLM como motor de síntesis de documentos extensos (planes de desarrollo regional, leyes, transcripciones de debates) para nutrir la base de conocimiento sin sobrecargar la ventana de contexto del LLM.

---

## 3. INGENIERÍA ETL Y TRATAMIENTO DE DATOS (ETL & QUALITY GATES)

### 3.1 Justificación Técnica de Polars
El pipeline de datos Vigil selecciona **Polars** sobre Pandas basándose en tres pilares de rendimiento:
1.  **Evaluación Perezosa (Lazy Evaluation):** Permite optimizar planes de consulta (Query Plans) mediante el pushdown de filtros y proyecciones antes de cargar datos en memoria.
2.  **Especificación de Memoria Apache Arrow:** Cero copias en operaciones de serialización y lectura de Parquet.
3.  **Procesamiento Paralelo Multihilo (Rust Core):** Crucial para manejar el volumen de comentarios y registros del Banco de Indicadores del INEGI (millones de filas) en hardware local sin incurrir en Out-of-Memory (OOM).

### 3.2 La Compuerta de Calidad (`quality_gate.py`)
El script de calidad implementa un filtro centrado en asegurar el **Mínimo Viable de Datos (MVD)** antes de realizar cualquier inferencia NLP.

```python
# Regla de Negocio del MVD (Mínimo Viable de Datos)
MVD_MINIMO = 50
```

Si el número de registros válidos para un actor en un periodo de 7 días es inferior a `MVD_MINIMO`, el sistema genera una alerta tipo `[DATOS_INSUFICIENTES]` y aborta el pipeline NLP de ese candidato. Esto previene sesgos estadísticos graves y alucinaciones en los reportes de sentimiento generados por IA.

### 3.3 Esquema de Datos Silver (Esquema de Destino)
Las especificaciones del formato Parquet en la capa Silver exigen los siguientes campos obligatorios:

| Campo | Tipo Polars | Descripción |
| :--- | :--- | :--- |
| `id_activo` | `String` | ID único de la página o activo en la plataforma |
| `plataforma` | `String` | Red social de origen (e.g., `facebook`, `instagram`) |
| `texto_publicacion` | `String` | Texto limpio del post/comentario, libre de PII (datos personales) |
| `reacciones_totales` | `Int64` | Métrica agregada: Likes + Shares + Comments |
| `seguidores_cuenta_origen`| `Int64` | Cantidad total de seguidores de la cuenta emisora |
| `tasa_interaccion` | `Float64`| Relación calculada: `reacciones_totales / seguidores` |
| `fecha` | `Datetime` | Timestamp original de publicación |
| `_fuente` | `String` | Origen técnico de la ingesta (e.g., `facebook_apify`) |
| `_fecha_ingesta` | `String` | Fecha ISO del procesamiento en el pipeline |
| `is_valid` | `Boolean` | Flag indicador de validación de calidad aprobado |

---

## 4. ANÁLISIS DE MÉTRICAS MATEMÁTICAS Y ALGORITMOS

### 4.1 Engagement Rate (ER)
Evita la trampa de las "métricas de vanidad" normalizando el nivel de interacción social del activo frente a su tamaño de comunidad local.

$$\text{ER}_{\text{post}} = \frac{\text{Likes} + \text{Compartidos} + \text{Comentarios}}{\text{Seguidores Totales}}$$

Para el consolidado semanal $T$ de un candidato:

$$\text{ER}_{\text{cand}}^T = \frac{1}{|P_T|} \sum_{i \in P_T} \frac{\text{Interacciones}(p_i)}{\text{Seguidores}_{\text{cand}}(t_i)}$$

### 4.2 Concentration Audience Ratio (CAR)
Monitorea la centralidad orgánica del ecosistema digital de un candidato, determinando la autonomía de su red de apoyo.

$$\text{CAR} = \frac{\text{Seguidores de la Cuenta Oficial}}{\text{Seguidores Totales del Ecosistema (Oficial + Satélites)}}$$

*   **CAR > 0.8:** Estructura altamente centralizada. Todo el tráfico y soporte recae en la figura principal. Vulnerable a ataques dirigidos o suspensiones de cuenta.
*   **CAR < 0.3:** Estructura distribuida. Red satélite muy activa. Puede indicar un gran movimiento orgánico ciudadano o la operación coordinada de cuentas artificiales (granjas de apoyo).

### 4.3 Índice de Comportamiento Inauténtico Coordinado (CIB / $S_T$)
Algoritmo para identificar automatizaciones y publicaciones síncronas en páginas satélites.

$$S_T(A) = 1 - \frac{\sigma(t_{\text{publicaciones}})}{\Delta T_{\text{max}}}$$

Donde:
*   $\sigma(t_{\text{publicaciones}})$ es la desviación estándar de los timestamps de publicación entre el conjunto de cuentas $A$.
*   $\Delta T_{\text{max}}$ es la ventana crítica de sincronía, definida por defecto en **300 segundos**.
*   **Condición:** Si $S_T(A) > 0.85$ en la ventana $\Delta T_{\text{max}}$, el sistema emite automáticamente una alerta `[COORDINATION_SUSPECT]` etiquetando los activos involucrados para auditoría forense digital.

### 4.4 Desviación de Agenda (AD)
Mide la brecha de atención entre la prensa regional institucional y los intereses reales de la conversación ciudadana en redes mediante la distancia de Jaccard sobre vectores semánticos extraídos.

$$\text{AD} = 1 - \text{Jaccard\_Similarity}(\text{Tópicos\_Prensa}, \text{Tópicos\_Ciudadanos})$$

*   $\text{AD} > 0.3$ indica una desviación relevante (temas ciudadanos ignorados por la prensa o viceversa).
*   $\text{AD} > 0.7$ señala una desconexión total, característica de bloqueos de prensa o campañas masivas de distracción artificial.

### 4.5 Posicionamiento Digital de Intención de Voto (PDIV)
El algoritmo central de indexación política de la suite (desarrollado por el equipo **SAEIL** y referenciado en `docs/pdiv_calculator_saeil_ref.py`) sigue la siguiente ecuación lineal ponderada:

$$\text{PDIV} = (\text{Sentiment\_Score} \times 0.40) + (\text{Volume\_Score} \times 0.30) + (\text{Engagement\_Score} \times 0.20) + (\text{Growth\_Score} \times 0.10)$$

#### Detalles de la Implementación del Calculador:
1.  **Conversión y Normalización de Sentimiento:** Transforma el análisis cualitativo (`positivo: 1`, `negativo: -1`, `neutro: 0`, `irónico: -0.5`) a una escala continua de $0$ a $100$, donde $50.0$ es estrictamente neutral.
2.  **Ponderación del Engagement por Canal:** Aplica coeficientes demográficos según la red social:
    *   Instagram: $1.0$ (Alta correlación de participación electoral en segmentos móviles jóvenes).
    *   TikTok: $0.9$ (Amplificación masiva).
    *   Facebook: $0.8$ (Mayor proporción de votantes mayores de 35 años).
    *   Twitter/X: $0.7$ (Cámara de eco cerrada de círculos políticos y periodísticos).
    *   YouTube: $0.6$ (Consumo pasivo).
3.  **Factor de Escala Territorial (INEGI 2020):** Divide las menciones crudas por el coeficiente poblacional de la región objetivo para evitar que el volumen masivo de la capital sesgue el índice estatal:
    *   Nayarit (Total): $1.0$
    *   Tepic (Capital): $0.33$
    *   Xalisco: $0.05$
    *   Santiago Ixcuintla: $0.04$
    *   Acaponeta: $0.03$
4.  **Penalización por Actividad de Bots:** Aplica penalizaciones acumulativas (hasta un tope de $80\%$) al volumen de un candidato basándose en anomalías del comportamiento:
    *   **Comentarios Excesivos por Usuario:** Usuarios con $> 50$ comentarios semanales penalizan el score de volumen en un $30\%$.
    *   **Anomalía de Likes:** Publicaciones con $>1,000$ likes sin comentarios orgánicos penalizan un $20\%$.
    *   **Spam Narrativo:** Textos idénticos duplicados $>5$ veces en la red del candidato penalizan un $10\%$.
5.  **Normalización Robusta con Rango Intercuartílico (IQR):** Para evitar que outliers masivos (publicaciones virales aisladas) distorsionen la escala del índice, los scores de volumen y engagement se normalizan aplicando un clipeo basado en el rango intercuartílico (IQR):
    *   $\text{Lower Bound} = Q_1 - 1.5 \times \text{IQR}$
    *   $\text{Upper Bound} = Q_3 + 1.5 \times \text{IQR}$
    *   Posteriormente se aplica escalamiento Min-Max tradicional sobre los datos acotados.

---

## 5. DIAGNÓSTICO DEL REPOSITORIO FISICO Y DISCREPANCIAS ENCONTRADAS

Como System Designer y ETL Developer, he auditado la estructura de archivos físicos recién copiada al entorno de ejecución en `/home/fratfn/Desarrollo/Agency/vigil/`. Se identificaron hallazgos críticos de diseño e implementación:

### 5.1 Discrepancia Crítica 1: Los Notebooks del Proyecto
*   **Lo Documentado (`README.md` y `docs/ARCHITECTURE.md`):** Se hace mención a un flujo estructurado de notebooks ordenados secuencialmente:
    *   `00_setup_and_config.ipynb`
    *   `01_explore_facebook_data.ipynb` / `01_data_ingestion_apify.ipynb`
    *   `02_initial_datasets.ipynb` / `02_etl_quality_gate.ipynb`
    *   `03_methodology_pipeline.ipynb` / `03_nlp_classification.ipynb`
    *   `04_electoral_intelligence_report.ipynb` / `04_sna_network_graph.ipynb`
    *   `05_report_generator.ipynb`
*   **La Realidad Física:** El directorio `vigil/notebooks/` **solo contiene físicamente un archivo**: [00_setup_and_config.ipynb](file:///home/fratfn/Desarrollo/Agency/vigil/notebooks/00_setup_and_config.ipynb). Los notebooks del `01` al `05` son planificaciones de arquitectura y no han sido codificados o integrados en esta rama del repositorio.

### 5.2 Discrepancia Crítica 2: Mapeo de Campos de Entrada en ETL
*   **La Inconsistencia de Datos:** El módulo de validación `src/processing/quality_gate.py` está escrito asumiendo que los datos crudos entrantes ya cuentan con columnas normalizadas en español como `texto_publicacion`, `reacciones_totales` y `seguidores_cuenta_origen`.
*   **La Estructura Real de Ingesta:** Al analizar los archivos físicos que residen en `data/raw/facebook/`, descubrimos que la salida directa del scraper de Apify tiene una estructura distinta y en inglés:
    *   **Posts (`fb_posts_tepic_2026-02-20.jsonl`):**
        ```json
        {"media": [...], "url": "...", "text": "...", "likes": 16, "comments": 1, "shares": 8}
        ```
    *   **Comments (`fb_comments_tepic_2026-02-20.jsonl`):**
        ```json
        {"postTitle": "...", "text": "...", "likesCount": 10, "facebookUrl": "..."}
        ```
*   **Consecuencia Directa:** Si ejecutamos `quality_gate.py` directamente sobre estos datos crudos, la ejecución fallará inmediatamente o producirá un DataFrame vacío, ya que los campos `texto_publicacion` y `reacciones_totales` no existen en el archivo JSONL de posts (se llaman `text` y `likes`, `shares`, `comments`). Tampoco existe la columna `seguidores_cuenta_origen`.

### 5.3 Diagnóstico de los Datos Raw Disponibles
Hemos inspeccionado programáticamente los archivos JSONL en `vigil/data/raw/facebook/` obteniendo los siguientes hallazgos:
1.  **`fb_posts_tepic_2026-02-20.jsonl` (60 Registros):**
    *   Todos los registros corresponden a publicaciones realizadas por la página del **DIF Nayarit** (`DIFNay`), la cual es el activo digital de **Beatriz Estrada**.
    *   Contiene textos institucionales, fotos y enlaces de videos/reels relacionados con actividades del DIF.
2.  **`fb_comments_tepic_2026-02-20.jsonl` (110 Registros):**
    *   Curiosamente, los comentarios en este archivo están asociados a publicaciones de **Geraldine Ponce** (Alcaldesa de Tepic) y no a los posts de DIF Nayarit. Se identifican por el campo `postTitle` que hace mención explícita a temas personales y políticos de Geraldine (su hija María Alejandra, reuniones de seguridad nacional, etc.).
    *   **Implicación de Datos:** Contamos con los posts de una candidata (Beatriz Estrada) y los comentarios de otra candidata (Geraldine Ponce). Para realizar un análisis cruzado limpio, es indispensable unificar fuentes de posts y comentarios para ambas candidatas en la fase de ingesta.

---

## 6. HOJA DE RUTA Y RECOMENDACIONES DE INGENIERÍA

Para avanzar de forma robusta en la implementación, se proponen las siguientes acciones correctivas inmediatas:

### Fase 1: Corrección de Mapeo en ETL (Mapeo a Capa Silver)
Se debe reescribir la función de normalización en el pipeline para transformar el esquema crudo al esquema Silver requerido por `quality_gate.py`.

```
[Posts Crudos JSONL]                              [Silver Parquet]
text ───────────────────────────────────────────► texto_publicacion
likes + comments + shares ──────────────────────► reacciones_totales
(Buscar en catálogo de páginas o setear default)──► seguidores_cuenta_origen
"facebook" ─────────────────────────────────────► plataforma
"fb_posts_tepic_2026-02-20" ────────────────────► id_activo
```

### Fase 2: Automatización del Script de Ingestión (`src/ingestion/`)
Crear un orquestador simple en Python que consuma el token de Apify desde el archivo `.env` para descargar de forma unificada los posts y comentarios correspondientes a las páginas de Facebook de todos los candidatos configurados en `config/config.yaml` (Beatriz Estrada, Geraldine Ponce, Andrea Navarro, etc.).

### Fase 3: Creación de los Notebooks Faltantes
1.  **`01_data_ingestion.ipynb`:** Script paso a paso para conectarse a Apify y descargar lotes de prueba.
2.  **`02_etl_processing.ipynb`:** Aplicación de la compuerta de calidad corregida con Polars y almacenamiento en formato `.parquet`.
3.  **`03_nlp_inference.ipynb`:** Bucle de inferencia utilizando `google-genai` para clasificar sentimiento y framing con `gemini-2.5-flash`.
4.  **`04_network_analysis.ipynb`:** Modelado del grafo de menciones/comentarios con NetworkX y cálculo de comunidades de Louvain.
5.  **`05_consolidated_report.ipynb`:** Implementación del algoritmo de cálculo PDIV y generación automática del reporte markdown final.

### Fase 4: Protocolos de Compliance y Anonimización
Asegurar que el proceso de normalización limpie cualquier dato personal identificable (PII) de los comentarios antes de guardarlos en la capa Silver:
*   Eliminar nombres de usuario explícitos en los textos.
*   Enmascarar URLs de perfiles personales.
*   Cumplir con las directrices del Protocolo de Berkeley para la conservación de evidencias de dominio público.

---
*Reporte elaborado por el agente de análisis e ingeniería de sistemas de RndmStudio para el proyecto Vigil.*
