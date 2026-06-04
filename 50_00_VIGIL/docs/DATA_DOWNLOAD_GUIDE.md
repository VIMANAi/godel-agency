# DATA DOWNLOAD GUIDE — Vigil
> Guía operativa de descarga y normalización de datos raw.
> Objetivo: poblar `vigil/data/raw/` y producir `vigil/data/silver/*.parquet` listos para SAEIL.

---

## ESTRUCTURA DE DIRECTORIOS

```
vigil/
└── data/
    ├── raw/                    ← Archivos tal como se descargan (nunca modificar)
    │   ├── facebook/           ← JSONL de Apify
    │   ├── ine/                ← CSV/XLS INE
    │   ├── inegi/
    │   │   ├── cpv2020/        ← Censo Población y Vivienda
    │   │   ├── enoe/           ← Empleo
    │   │   ├── denue/          ← Directorio económico
    │   │   ├── shapefiles/     ← SHP/GeoJSON cartografía
    │   │   └── indicadores/    ← Banco de Indicadores
    │   └── ieen/               ← Datos electorales Nayarit
    └── silver/                 ← Parquet normalizado (salida de Polars)
        ├── electoral/
        ├── sociodemografico/
        └── redes_sociales/
```

---

## PRIORIDAD 1 — DATOS YA EN SSD (copiar antes de desmontar)

**Acción inmediata antes de desmontar SERVER_TOOLBOX:**

```bash
# Copiar datos reales de Facebook al workspace
cp /run/media/fnfrater/SERVER_TOOLBOX/centralinfo/dataset_facebook-posts-scraper_2026-02-20_17-43-56-562.jsonl \
   /home/fnfrater/Escritorio/RndmStudio/vigil/data/raw/facebook/fb_posts_tepic_2026-02-20.jsonl

cp /run/media/fnfrater/SERVER_TOOLBOX/centralinfo/dataset_facebook-comments-scraper_2026-02-20_18-34-36-980.jsonl \
   /home/fnfrater/Escritorio/RndmStudio/vigil/data/raw/facebook/fb_comments_tepic_2026-02-20.jsonl

# Copiar Dashboard HTML de referencia
cp "/run/media/fnfrater/SERVER_TOOLBOX/centralinfo/SAIEL/Knowledge_Base/Dev_Migration/SAIEL_Persistence/SAIEL1/reports/DASHBOARD_NAYARIT.html" \
   /home/fnfrater/Escritorio/RndmStudio/vigil/docs/DASHBOARD_NAYARIT_ref.html

# Copiar pdiv_calculator.py para migración futura
cp /run/media/fnfrater/SERVER_TOOLBOX/centralinfo/SAIEL/Knowledge_Base/Dev_Migration/SAIEL_Persistence/SAIEL1/engine/core/pdiv_calculator.py \
   /home/fnfrater/Escritorio/RndmStudio/vigil/docs/pdiv_calculator_saeil_ref.py
```

**Verificación:**

```bash
ls -lh /home/fnfrater/Escritorio/RndmStudio/vigil/data/raw/facebook/
# Esperado: fb_posts_tepic_2026-02-20.jsonl y fb_comments_tepic_2026-02-20.jsonl
```

---

## PRIORIDAD 2 — INE FEDERAL (Datos Electorales)

### 2.1 Lista Nominal y Datos Demográficos de Electores

```
URL: https://ine.mx/transparencia/datos-abiertos/
Sección: "Estadísticas del Padrón Electoral"
Archivos a descargar:
  - ListaNominal_Nayarit_2025.xlsx      → raw/ine/lista_nominal_nayarit_2025.xlsx
  - ElectoresPorEdad_Nayarit.xlsx       → raw/ine/electores_edad_nayarit_2025.xlsx
  - ElectoresPorGenero_Nayarit.xlsx     → raw/ine/electores_genero_nayarit_2025.xlsx
```

### 2.2 Resultados Electorales 2024

```
URL: https://resultados.ine.mx
Filtrar por: Estado = Nayarit
Descargar:
  - Resultados Presidentes Municipales 2024 (XLS)  → raw/ine/presidentes_municipales_nayarit_2024.xlsx
  - Resultados Diputados Locales 2024 (XLS)        → raw/ine/diputados_locales_nayarit_2024.xlsx
  - Participación por Sección Electoral (CSV)       → raw/ine/participacion_secciones_nayarit_2024.csv
```

### 2.3 Secciones Electorales (Cartografía)

```
URL: https://cartografia.ine.mx/sige7/?cartografia=mapas
Filtrar: Nayarit → Secciones Electorales
Formato: Shapefile (.shp + .dbf + .shx + .prj)
Destino: raw/inegi/shapefiles/secciones_electorales_nayarit/
CRÍTICO: Necesario para cruzar votos con AGEB
```

---

## PRIORIDAD 3 — INEGI CENSAL (Sociodemográfico)

### 3.1 Censo de Población y Vivienda 2020

```
URL: https://www.inegi.org.mx/app/scitel/Default?ev=9
Seleccionar: Entidad = Nayarit (18)
Descargar ITER (resultados por localidad):
  - iter_18CSV20.zip    → descomprimir en raw/inegi/cpv2020/

URL alternativa AGEB: https://www.inegi.org.mx/app/scitel/Default?ev=10
  - ageb_manzana_urbana_18.zip  → raw/inegi/cpv2020/ageb/
```

### 3.2 DENUE (Directorio Económico)

```
API: https://www.inegi.org.mx/app/mapa/denue/default.aspx
Alternativa descarga masiva:
  URL: https://www.inegi.org.mx/app/descarga/?p=denue
  Filtrar: Estado = 18 (Nayarit)
  Formato: CSV
  Destino: raw/inegi/denue/denue_nayarit_2024.csv
```

### 3.3 Banco de Indicadores (API)

```python
# Script de descarga via API INEGI
import httpx, json

INDICADORES = {
    "poblacion_total": "1002000001",
    "escolaridad_promedio": "6207019014",
    "tasa_informalidad": "444258",
}

ENTIDAD = "18"  # Nayarit
TOKEN = "tu_token_inegi"  # Registrar en: www.inegi.org.mx/app/indicadores/

base_url = "https://www.inegi.org.mx/app/indicadores/inapi/indicadores"

for nombre, ind_id in INDICADORES.items():
    url = f"{base_url}/{ind_id}/false/BIE/BIE_TABLA/{ENTIDAD}/es.json?token={TOKEN}"
    r = httpx.get(url)
    with open(f"data/raw/inegi/indicadores/{nombre}.json", "w") as f:
        json.dump(r.json(), f, ensure_ascii=False, indent=2)
```

### 3.4 Cartografía INEGI (Shapefiles)

```
Marco Geoestadístico Nacional 2020:
URL: https://www.inegi.org.mx/app/biblioteca/ficha.html?upc=889463807469
  - Descargar: Nayarit completo
  - Archivos clave:
      18mun.shp     → municipios
      18ent.shp     → entidad
      18ageb_ur.shp → áreas geoestadísticas básicas urbanas
  Destino: raw/inegi/shapefiles/marco_geoestadistico_nayarit/
```

### 3.5 ENOE Nayarit 2025

```
URL: https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2025/enoe/enoe2025_02_Nay.pdf
Destino: raw/inegi/enoe/enoe_nayarit_2025_q2.pdf
Nota: PDF tabular → extraer con Gemini API (vision) si se necesitan datos tabulados
```

### 3.6 ENDUTIH 2024 Microdatos

```
URL: https://www.inegi.org.mx/rnm/index.php/catalog/1102
Registrarse para descarga
Archivos: datos_endutih_2024.zip (Stata, SAS, SPSS)
Convertir Stata → Polars:
  pip install pyreadstat
  df = polars.from_pandas(pandas.read_stata("endutih_2024.dta"))
Destino: raw/inegi/endutih/
```

---

## PRIORIDAD 4 — IEEN ESTATAL (Instituto Estatal Electoral Nayarit)

```
URL: https://ieen.nayarit.gob.mx
Secciones a revisar:
  - "Resultados Electorales" → XLS por cargo
  - "Estadísticas" → participación por sección

Archivos a descargar:
  - ResultadosGobernador_Nayarit_2024.xlsx    → raw/ieen/gobernador_nayarit_2024.xlsx
  - ResultadosDiputados_Nayarit_2024.xlsx     → raw/ieen/diputados_nayarit_2024.xlsx
  - ResultadosMunicipios_Nayarit_2024.xlsx    → raw/ieen/municipios_nayarit_2024.xlsx
  - ParticipacionPorSeccion_2024.csv          → raw/ieen/participacion_secciones_2024.csv
```

---

## PRIORIDAD 5 — DATOS EXTERNOS NLP

### 5.1 MexTwitter (Hugging Face)

```python
# Descarga selectiva (muestra 50k)
from datasets import load_dataset
ds = load_dataset("IIC/MexTwitter", split="train[:50000]")
ds.to_json("data/raw/nlp/mextwitter_sample_50k.jsonl")
```

### 5.2 MEGA — Mexican Election Twitter 2018

```
URL: https://figshare.com (buscar "MEGA Mexican Election")
Tamaño: ~2GB comprimido
Destino: raw/nlp/mega_election_2018/
Nota: Solo descargar si se hará fine-tuning o comparación histórica
Prioridad: BAJA para MVP
```

---

## NORMALIZACIÓN ESTÁNDAR (Silver Layer)

Para cada dataset descargado, aplicar este pipeline con Polars antes de subir al silver:

```python
import polars as pl
import pandera.polars as pa
from pandera.typing.polars import DataFrame
from datetime import date

def normalizar_electoral(path_raw: str, fuente: str) -> pl.DataFrame:
    """
    Normalización estándar para datos electorales INE/IEEN
    """
    df = pl.read_csv(path_raw, infer_schema_length=10000)

    # 1. Nombres de columnas: snake_case, sin acentos, sin espacios
    df = df.rename({
        col: col.lower()
               .replace(" ", "_")
               .replace("á", "a").replace("é", "e")
               .replace("í", "i").replace("ó", "o").replace("ú", "u")
               .replace("ñ", "n")
        for col in df.columns
    })

    # 2. Añadir metadata
    df = df.with_columns([
        pl.lit(fuente).alias("_fuente"),
        pl.lit(date.today().isoformat()).alias("_fecha_ingesta"),
        pl.lit("raw").alias("_capa"),
    ])

    # 3. Filtrar solo Nayarit si hay columna de estado
    if "cve_ent" in df.columns:
        df = df.filter(pl.col("cve_ent") == 18)
    elif "entidad" in df.columns:
        df = df.filter(pl.col("entidad").str.contains("(?i)nayarit"))

    # 4. Escribir Parquet particionado
    nombre = path_raw.split("/")[-1].replace(".csv", "").replace(".xlsx", "")
    df.write_parquet(f"data/silver/electoral/{nombre}.parquet")

    print(f"OK: {len(df):,} registros → silver/electoral/{nombre}.parquet")
    return df


def normalizar_facebook_jsonl(path_raw: str) -> pl.DataFrame:
    """
    Normalización de datos de Apify Facebook scraper
    """
    df = pl.read_ndjson(path_raw)

    # Campos estándar Vigil
    campos = {
        "postId": "post_id",
        "pageName": "pagina",
        "message": "texto",
        "likesCount": "likes",
        "sharesCount": "shares",
        "commentsCount": "comentarios",
        "date": "fecha",
        "url": "url",
    }

    # Seleccionar solo campos que existan
    cols_disponibles = [c for c in campos.keys() if c in df.columns]
    df = df.select(cols_disponibles).rename({k: v for k, v in campos.items() if k in cols_disponibles})

    # Parsear fecha
    if "fecha" in df.columns:
        df = df.with_columns(
            pl.col("fecha").str.to_datetime(strict=False).alias("fecha")
        )

    # Metadata
    df = df.with_columns([
        pl.lit("facebook_apify").alias("_fuente"),
        pl.lit(date.today().isoformat()).alias("_fecha_ingesta"),
        pl.lit("silver").alias("_capa"),
    ])

    nombre = path_raw.split("/")[-1].replace(".jsonl", "")
    df.write_parquet(f"data/silver/redes_sociales/{nombre}.parquet")

    print(f"OK: {len(df):,} registros → silver/redes_sociales/{nombre}.parquet")
    return df
```

---

## CHECKLIST PREVIO A DESMONTAR SSD

Antes de desconectar `SERVER_TOOLBOX`:

- [ ] `fb_posts_tepic_2026-02-20.jsonl` copiado a `vigil/data/raw/facebook/`
- [ ] `fb_comments_tepic_2026-02-20.jsonl` copiado a `vigil/data/raw/facebook/`
- [ ] `DASHBOARD_NAYARIT.html` copiado a `vigil/docs/`
- [ ] `pdiv_calculator.py` copiado a `vigil/docs/` (referencia)
- [ ] `REPORTE_TECNICO_NAYARIT_SEM1.md` copiado a `vigil/docs/`
- [ ] `saiel-v2.zip` copiado a `SERVER_TOOLBOX/RndmStudio/` (ya está en el espejo)
- [ ] `docscrape.jsonl` y `docscrape_86.jsonl` revisados y copiados si contienen datos útiles
- [ ] Espejo `SERVER_TOOLBOX/RndmStudio/` actualizado con último `rsync`

**Último rsync antes de desmontar:**

```bash
rsync -a --exclude='.venv/' --exclude='__pycache__/' \
  /home/fnfrater/Escritorio/RndmStudio/ \
  /run/media/fnfrater/SERVER_TOOLBOX/RndmStudio/ \
  && echo "Espejo actualizado OK"
```

---

## CONVENCIÓN DE NOMBRES DE ARCHIVOS

```
raw/
  {fuente}_{tema}_{territorio}_{año}[-{periodo}].{ext}

Ejemplos:
  ine_lista_nominal_nayarit_2025.csv
  inegi_cpv2020_iter_nayarit_2020.csv
  inegi_denue_nayarit_2024.csv
  ieen_presidentes_municipales_nayarit_2024.xlsx
  apify_fb_posts_tepic_2026-02.jsonl
  apify_fb_comments_tepic_2026-02.jsonl

silver/
  {tema}_{territorio}_{año}.parquet

Ejemplos:
  electoral_nayarit_2024.parquet
  cpv2020_nayarit_ageb.parquet
  redes_fb_posts_tepic_2026-02.parquet
```

---

*Documento operativo Vigil — actualizar con cada nueva descarga completada.*
