# VIGIL — Metodología del Pipeline y Métricas
> Metodología del pipeline, métricas y algoritmos del sistema Vigil.
> Contexto: Nayarit 2026. Referencia académica: Paper DMI (Facebook Pages Mexican Precampaigns, 2017).

---

## PREGUNTAS DE INVESTIGACIÓN

### Analítica Individual (por Candidato)

| ID | Pregunta | Métrica | Fuente Datos |
|---|---|---|---|
| Q1 | ¿Concentración de audiencia en cuenta oficial vs. red satélite? | CAR (Concentration Audience Ratio) | DAT_SOC_DIG_RAW |
| Q2 | ¿Rol operativo de los activos digitales (praising / revile / clon / troll)? | Clasificación NLP framing | DAT_SOC_DIG_RAW |
| Q3 | ¿Vectores semánticos del clustering sin sesgos predefinidos? | UMAP + Leiden communities | DAT_SOC_DIG_RAW |
| Q4 | ¿Tasa de interacción ajustada por lista nominal del distrito? | ER normalizado por padrón INE | DAT_SOC_DIG_RAW + DAT_INE_PADRON |

### Analítica de Redes y Ecosistema

| ID | Pregunta | Métrica | Fuente Datos |
|---|---|---|---|
| Q5 | ¿Sincronía temporal entre activos (CIB — bots coordinados)? | S_T (Sincronía Temporal) | DAT_SOC_DIG_RAW |
| Q6 | ¿Desviación entre agenda de prensa y conversación orgánica? | AD (Agenda Deviation) | DAT_NEWS_REGIONAL + DAT_SOC_DIG_RAW |
| Q7 | ¿La audiencia coincide con secciones electorales clave del INE/IEEN? | Geolocalización vs. padrón | DAT_GEO_MAP + DAT_INE_PADRON |

---

## MÉTRICAS MATEMÁTICAS

### 1. Tasa de Interacción (ER)

Normaliza el engagement relativo al alcance local, evitando sesgo de "métricas de vanidad":

```
                Likes + Compartidos + Comentarios
ER_post  =   ─────────────────────────────────────
                     Seguidores Totales
```

Para agregados sobre ventana temporal T (lotes semanales):

```
             1        ╭  Interacciones(p_i)          ╮
ER_cand^T = ───  Σ    │  ────────────────────────────  │
            |P_T| i∈P_T╰  Seguidores_cand(t_i)         ╯
```

Donde `P_T` = conjunto de publicaciones de la red del candidato durante semana T.

**Implementación Polars:**
```python
df = df.with_columns(
    pl.when(pl.col("seguidores_cuenta_origen") > 0)
    .then(pl.col("reacciones_totales") / pl.col("seguidores_cuenta_origen"))
    .otherwise(0.0)
    .alias("tasa_interaccion")
)
```

---

### 2. Ratio de Concentración de Audiencia (CAR)

Mide dependencia de cuenta oficial vs. red de apoyo satélite:

```
         Seguidores Cuenta Oficial
CAR  =  ────────────────────────────────────
         Seguidores Totales del Ecosistema
```

- CAR > 0.8: ecosistema concentrado, alta dependencia de cuenta oficial
- CAR < 0.3: ecosistema distribuido, red satélite activa (orgánica o artificialmente)

---

### 3. Índice de Comportamiento Inauténtico Coordinado (CIB / S_T)

Detecta granjas de bots y estructuras de publicación coordinada:

```
              σ(t_publicaciones)
S_T(A) = 1 − ────────────────────
                  ΔT_max
```

Donde:
- `σ(t_publicaciones)` = desviación estándar de los timestamps de publicación
- `ΔT_max` = umbral de tiempo límite (default: **300 segundos**)
- **Si S_T > 0.85** → alerta automática `[COORDINATION_SUSPECT]`

**Filtros complementarios anti-bot (del PDIV Calculator de SAEIL):**
- Usuario con > 50 comentarios únicos → sospechoso
- Post con > 1,000 likes → anomalía
- Texto idéntico publicado > 5 veces → spam

---

### 4. Desviación de Agenda (AD)

Contrasta narrativa de medios tradicionales vs. conversación orgánica en redes:

```
AD = 1 − Jaccard_Similarity(Tópicos_Prensa, Tópicos_Ciudadanos)
```

- AD ≈ 0: prensa y redes hablan de lo mismo
- AD > 0.3: brecha significativa → hay temas que la prensa no cubre pero la ciudadanía sí
- AD > 0.7: desconexión total → indicador de agenda controlada o crisis no cubierta

---

### 5. PDIV — Posicionamiento Digital de Intención de Voto (de SAEIL)

Métrica central del ecosistema SAEIL, adaptable a Vigil:

```
PDIV = (Sentimiento × 0.40) + (Volumen × 0.30) + (Engagement × 0.20) + (Crecimiento × 0.10)
```

Pesos de fuente aplicados al engagement:
- Instagram: 1.0 (audiencia joven, alta correlación electoral)
- TikTok: 0.9
- Facebook: 0.8 (adultos 30+)
- Twitter/X: 0.7
- YouTube: 0.6

Escala: 0–100 (50 = posición neutral)

> Implementación completa: `vigil/docs/pdiv_calculator_saeil_ref.py`

---

## CLASIFICACIÓN DE FRAMING POLÍTICO (NLP)

### Taxonomía de Activos Digitales (del paper DMI 2017)

| Tipo | Definición | Indicadores |
|---|---|---|
| **Oficial** | Cuenta verificada del candidato | URL/username declarado, badge verificado |
| **Praising** | Cuenta de apoyo/alabanza activa | Menciona al candidato positivamente, comparte contenido oficial |
| **Informative** | Reporte neutral de actividades | Lenguaje descriptivo, sin carga emocional |
| **Revile** | Crítica agresiva / guerra sucia | Ataques, desacreditación, memes negativos |
| **Clone** | Cuenta que imita la identidad oficial | Username similar, foto de perfil copiada |
| **Troll** | Cuenta de distracción / vulgaridad coordinada | Spam, contenido ofensivo, volumen alto |

### Prompt del Clasificador (Gemini 2.5-flash)

```python
NLP_SYSTEM_PROMPT = """
Eres un clasificador experto de discurso político electoral.
Analiza el texto proporcionado y devuelve ÚNICAMENTE un objeto JSON con:
  "sentiment": "positive" | "negative" | "neutral"
  "framing": "praising" | "revile" | "informative" | "troll" | "irrelevante"
  "keywords_extracted": [lista de entidades: candidatos, temas, zonas geográficas]
  "confidence": 0.0 a 1.0

Contexto: Elecciones municipales Nayarit 2026.
"""
```

---

## ANÁLISIS DE REDES (SNA)

### Grafo del Ecosistema Digital

```
Nodos:
  - Cuenta Oficial (candidato)
  - Páginas Satélite
  - Proxies de Medios
  - Anunciantes compartidos (Meta Ad Library)

Relaciones:
  SIGUE           → seguimiento entre cuentas
  RECOMPARTE      → reshare de contenido
  CO_PATROCINA    → mismo ID de pago en anuncios Meta
  CONTENIDO_SIMILAR → umbral S_T < 300s (coordinación sospechosa)
```

### Métricas de Centralidad a Calcular

| Métrica | Qué mide | Aplicación electoral |
|---|---|---|
| Degree Centrality | Número de conexiones directas | Influencia local de una cuenta |
| Betweenness Centrality | Control de flujo entre nodos | Identificar intermediarios/bridges |
| PageRank | Importancia por calidad de conexiones | Ranking de influencers reales |
| Eigenvector Centrality | Conexión con nodos importantes | Cuentas con amplificación élite |
| Louvain Communities | Grupos densamente conectados | Facciones políticas, burbujas |

### Cypher Query Neo4j (referencia SAEIL)

```cypher
MERGE (c:Candidato {nombre: $nombre})
MERGE (a:ActivoDigital {id: $id_activo})
SET a.plataforma = $plataforma
MERGE (a)-[r:APOYA_A {framing: $framing}]->(c)
```

---

## MATRIZ DE REQUERIMIENTOS DE DATOS (MVD)

Volúmenes mínimos para que los algoritmos sean estadísticamente válidos:

| Subproceso | Volumen Mínimo (MVD) | Filtro de Calidad | Umbral Significancia |
|---|---|---|---|
| Análisis Sentimiento NLP | 50 comentarios únicos / candidato / semana | Longitud > 3 palabras, sin emojis duplicados | α < 0.05 prueba Z |
| Detección CIB (SNA) | 10+ activos coordinados | S_T > 0.85 en ΔT < 300s | Desviación σ < 0.1 |
| Desviación de Agenda (AD) | 100 artículos/semana en prensa | Relevancia > 0.7 en clustering | Jaccard AD > 0.3 |
| Tasa de Interacción (ER) | Calculado (sin mínimo) | Activos con > 100 seguidores | ER > 0.01 (1%) |
| Perfilamiento Ideológico | 5+ interacciones mutuas | Nodos con grado de entrada > 2 | Centralidad > 0.05 |

> **Regla del MVD:** Si ingesta < 50 registros para un candidato en la semana,
> el sistema marca el periodo como `[DATOS_INSUFICIENTES]` y NO genera reporte de sentimiento.
> Esto protege la credibilidad del análisis.

---

## PROTOCOLO DE COMPUERTA DE CALIDAD (ETL Gate)

Aplicar antes de escribir cualquier dato en `data/silver/`:

```python
import polars as pl
import pandera.polars as pa

def ejecutar_compuerta_calidad(df_crudo: pl.DataFrame) -> pl.DataFrame:
    """Aplica controles de calidad y normalización.
    Entrada: DataFrame crudo de Apify.
    Salida: DataFrame procesado con métricas calculadas, listo para silver/.
    """
    df_procesado = (
        df_crudo.lazy()
        .filter(pl.col("texto_publicacion").is_not_null())
        .filter(pl.col("reacciones_totales") >= 0)
        .with_columns(
            pl.when(pl.col("seguidores_cuenta_origen") > 0)
            .then(pl.col("reacciones_totales") / pl.col("seguidores_cuenta_origen"))
            .otherwise(0.0)
            .alias("tasa_interaccion"),
            pl.lit(True).alias("is_valid"),
        )
        .collect()
    )
    return df_procesado
```

### Filtros Anti-Spam / Anti-Bot

1. **Anti-Spam:** Descartar posts con > 70% caracteres especiales, o réplicas idénticas del mismo ID en < 1 hora
2. **Anti-Bot:** Filtrar cuentas con < 30 días de antigüedad sin actividad orgánica sostenida
3. **Voz Fantasma:** Para medir ER, descartar cuentas con solo likes masivos sin comentarios (granjas)

---

## CONEXIÓN CON EL PAPER DMI 2017

*"Facebook Pages in Mexican Presidential Pre-campaigns" — Digital Methods Initiative*

El paper estudió las precampañas presidenciales 2012 en México analizando páginas de Facebook.
Sus conceptos se mapean directamente al stack Vigil:

| Concepto DMI | Implementación Vigil | Módulo |
|---|---|---|
| Likeconomy — likes como moneda política | ER normalizado por padrón | Módulo 2 NLP |
| Mapping the ecosystem (páginas oficiales + satélite) | Grafo de activos digitales (Neo4j) | Módulo 5 SNA |
| Tipos de páginas (fan, attack, parody) | Taxonomía framing: praising/revile/clon/troll | Módulo 2 NLP |
| Engagement Rate por página | CAR + ER por candidato | Módulo 2 |
| Network of co-likers | Louvain communities sobre grafo | Módulo 4B |
| Content analysis de publicaciones | Clasificación Gemini (framing + keywords) | Módulo 2 |
| Temporal patterns | Sincronía S_T para detección CIB | Módulo 5 |

> El paper es la referencia metodológica para el reporte final de inteligencia.
> El objetivo de Vigil es producir un análisis equivalente pero con datos de Tepic 2026
> y stack moderno (Polars, Gemini 2.5-flash, NetworkX, Louvain).

---

## PLANTILLA DE REPORTE SEMANAL

Estructura del `reports/reporte_YYYYMMDD.md`:

```
# Reporte de Inteligencia Electoral — Tepic, Nayarit
## Semana: [FECHA_INICIO] al [FECHA_FIN]

### 5.1 Ficha: [CANDIDATO_X]
  Estado: [PROCESADO / DATOS_INSUFICIENTES]
  Activos detectados: [N]
  CAR: [valor]
  ER promedio: [valor]
  PDIV Score: [valor 0-100]

### A. Balance de Polarización y Sentimiento
  | Tendencia     | Activos | Seguidores |
  | Pro (Apoyo)   | [N]     | [N]        |
  | Contra        | [N]     | [N]        |

### B. Alertas CIB
  [Lista de activos con S_T > 0.85]

### C. Desviación de Agenda (AD)
  AD = [valor]
  Temas en prensa NO en redes: [lista]
  Temas en redes NO en prensa: [lista]

### 7. Recomendaciones Estratégicas
  [Generado por Gemini basado en hallazgos]
```

---

*Vigil Pipeline Methodology v1.0 — Jun 2026*
*Fuentes: DMI paper 2017, SAEIL pdiv_calculator.py*
