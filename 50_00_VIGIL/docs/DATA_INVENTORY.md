# DATA INVENTORY — Vigil / Nayarit 2026
> Catálogo maestro de fuentes de datos. Generado: 2026-06-01
> Uso: cruzar con datos ya descargados en equipo de ejecución (SAIEL) antes de desmontar SSD.

---

## ÁRBOL DE MÓDULOS DE DATOS

```
VIGIL::DATA_SOURCES
│
├── M1 :: ELECTORAL
│   ├── M1.1 :: INE — Federal
│   ├── M1.2 :: IEEN — Estatal Nayarit
│   └── M1.3 :: Histórico Electoral
│
├── M2 :: SOCIODEMOGRÁFICO (INEGI)
│   ├── M2.1 :: Censos de Población y Vivienda
│   ├── M2.2 :: Encuestas de Empleo (ENOE)
│   ├── M2.3 :: Encuestas de Ingresos y Gastos (ENIGH)
│   ├── M2.4 :: Economía y Sectores (DENUE, CE)
│   ├── M2.5 :: Banco de Indicadores
│   ├── M2.6 :: Seguridad y Justicia (ENVIPE)
│   ├── M2.7 :: Tecnología y Conectividad (ENDUTIH)
│   └── M2.8 :: Geoespacial y Medio Ambiente
│
├── M3 :: REDES SOCIALES (SCRAPED)
│   ├── M3.1 :: Facebook (Apify) ← DATOS REALES YA DESCARGADOS (SSD)
│   ├── M3.2 :: Instagram (Apify)
│   ├── M3.3 :: TikTok (Apify)
│   └── M3.4 :: YouTube (Apify)
│
├── M4 :: PRESUPUESTO Y TRANSPARENCIA
│   ├── M4.1 :: Financiamiento de Partidos (INE)
│   └── M4.2 :: Gasto Federal en Nayarit
│
├── M5 :: DATASETS EXTERNOS / NLP
│   ├── M5.1 :: MexTwitter (Hugging Face)
│   ├── M5.2 :: MEGA — Mexican Election Twitter 2018
│   └── M5.3 :: Barcenas-Juridico-Mexicano
│
└── M6 :: GEOESPACIAL / TERRITORIO
    ├── M6.1 :: Cartografía INEGI (SHP, GeoJSON)
    ├── M6.2 :: DENUE Georreferenciado
    └── M6.3 :: Áreas Protegidas Nayarit (IEEN Ecología)
```

---

## M1 :: ELECTORAL

### M1.1 — INE Federal (Instituto Nacional Electoral)

| # | Base de Datos | Variables Clave | Formato | Año | URL | Prioridad Vigil |
|---|---|---|---|---|---|---|
| 1 | Proceso Electoral Federal 2024 | Votos por partido, diputados, senadores por distrito Nayarit | XLS, CSV, PDF | 2024 | resultados.ine.mx | 🔴 ALTA |
| 2 | Integración Diputaciones Federales (CEF) | Diputaciones por distrito, % votos | Interactivo web | 2024 | ine.mx/transparencia/datos-abiertos | 🔴 ALTA |
| 3 | Integración de Senadurías | Senadores por fórmula y RP | Interactivo web | 2024 | ine.mx/transparencia/datos-abiertos | 🟡 MEDIA |
| 4 | Lista Nominal de Electores | Electores por municipio, secciones electorales | CSV, PDF | 2025 | ine.mx/transparencia/datos-abiertos | 🔴 ALTA |
| 5 | Credencial para Votar (vigencia) | Electores con credencial vigente por CURP | Estadística PDF | 2025 | ine.mx/transparencia/datos-abiertos | 🟡 MEDIA |
| 6 | Estadísticas Demográficas Electores | Edad, género, escolaridad de electores por municipio | XLS, CSV | 2025 | ine.mx/transparencia/datos-abiertos | 🔴 ALTA |
| 7 | Electores por Rango de Edad | Grupos quinquenales 18-24, 25-29... | XLS | 2025 | ine.mx/transparencia/datos-abiertos | 🔴 ALTA |
| 8 | Electores por Género | Hombres/mujeres por municipio | XLS | 2025 | ine.mx/transparencia/datos-abiertos | 🟡 MEDIA |
| 9 | Financiamiento Público a Partidos | Ingresos, gastos, auditorías por partido | XLS, CSV | 2024 | ine.mx/transparencia/datos-abiertos | 🟡 MEDIA |
| 10 | Financiamiento Privado | Donantes, montos | XLS | 2024 | ine.mx/transparencia/datos-abiertos | 🟡 MEDIA |
| 11 | Gastos de Campaña 2024 | Gastos por distrito, medios, propaganda | XLS, PDF | 2024 | ine.mx/transparencia/datos-abiertos | 🟡 MEDIA |

**URL principal INE:** https://ine.mx/transparencia/datos-abiertos/

---

### M1.2 — IEEN Estatal (Instituto Estatal Electoral de Nayarit)

| # | Base de Datos | Variables Clave | Formato | Año | URL | Prioridad Vigil |
|---|---|---|---|---|---|---|
| 12 | Proceso Electoral Local Nayarit 2024 | Gobernador, Congreso local, presidentes municipales | XLS, PDF | 2024 | ieen.nayarit.gob.mx | 🔴 ALTA |
| 13 | Resultados Locales por Sección | Votación por sección electoral, % participación | CSV | 2024 | resultados.ine.mx/Nayarit | 🔴 ALTA |
| 14 | Diputados al Congreso Local | Diputados electos por distrito, votos | XLS | 2024 | ieen.nayarit.gob.mx | 🔴 ALTA |
| 15 | Concejos Municipales | Regidores y síndicos por municipio, partidos | XLS | 2024 | ieen.nayarit.gob.mx | 🟡 MEDIA |
| 16 | Presidentes Municipales 2024 | Presidentes electos, partidos, votos nulos | XLS, PDF | 2024 | ine.mx/transparencia/datos-abiertos | 🔴 ALTA |
| 17 | Participación por Sección | % participación histórica vs. 2024 | CSV | 2024 | ieen.nayarit.gob.mx | 🔴 ALTA |

---

### M1.3 — Histórico Electoral

| # | Base de Datos | Rango Temporal | Formato | URL | Prioridad Vigil |
|---|---|---|---|---|---|
| 18 | Elecciones Federales Históricas | 1988–2024 | XLS, CSV | ine.mx/archivos3/portal/historico/ | 🟡 MEDIA |
| 19 | Elecciones Locales Históricas Nayarit | 1990–2024 | XLS, PDF | ine.mx/archivos3/portal/historico/ | 🟡 MEDIA |
| 20 | Referendos y Consultas Populares | 2021 | PDF | ine.mx/transparencia/datos-abiertos | 🟢 BAJA |

---

## M2 :: SOCIODEMOGRÁFICO (INEGI)

### M2.1 — Censos de Población y Vivienda

| # | Base de Datos | Variables Clave | Formato | Año | URL | Prioridad Vigil |
|---|---|---|---|---|---|---|
| 21 | CPV 2020 — Resultados principales | 1,235,456 hab, 361,270 viviendas, escolaridad 10.3 años, 2,508 hablantes indígenas | CSV, XLSX | 2020 | inegi.org.mx/app/scitel/Default?ev=10 | 🔴 ALTA |
| 22 | SCITEL — Resultados por AGEB y manzana 2020 | Población por edad, agua entubada, servicios por manzana | CSV, XLSX | 2020 | inegi.org.mx/app/scitel/Default?ev=10 | 🔴 ALTA |
| 23 | ITER — Resultados por localidad 2020 | Población, vivienda, servicios por localidad | CSV, XLSX | 2020 | inegi.org.mx/app/scitel/Default?ev=9 | 🔴 ALTA |
| 24 | Panorama sociodemográfico de Nayarit 2020 | Indicadores clave demográficos (resumen) | PDF | 2020 | inegi.org.mx | 🟢 BAJA |
| 25 | Censo Intercensal 2015 | Comparación 2010–2020 | PDF | 2015 | inegi.org.mx/productos | 🟢 BAJA |
| 26 | Inventario Nacional de Viviendas | Tipo, servicios, materiales por vivienda | Descarga masiva | Actualizado | inegi.org.mx/app/descarga/ | 🟡 MEDIA |

---

### M2.2 — Encuestas de Empleo (ENOE)

| # | Base de Datos | Variables Clave | Formato | Año | URL | Prioridad Vigil |
|---|---|---|---|---|---|---|
| 27 | ENOE Nacional 2025 Q2 | PEA 60.5M, informalidad 54.5%, salarios, sector | PDF + Microdatos | 2025 | inegi.org.mx/contenidos/saladeprensa/boletines/2025/enoe/ | 🟡 MEDIA |
| 28 | ENOE Nayarit específico | Ocupación y empleo por municipio | PDF | 2025 Q2 | inegi.org.mx/contenidos/saladeprensa/boletines/2025/enoe/enoe2025_02_Nay.pdf | 🔴 ALTA |
| 29 | ENOE Microdatos | Individuales: empleo, ingresos, características | Stata, SAS, SPSS, CSV | Trimestral | inegi.org.mx/microdatos | 🟡 MEDIA |

---

### M2.3 — Encuestas de Ingresos y Gastos (ENIGH)

| # | Base de Datos | Variables Clave | Formato | Año | URL | Prioridad Vigil |
|---|---|---|---|---|---|---|
| 30 | ENIGH 2024 | Ingresos mensuales, gastos (alimentación, vivienda, salud, educación), NSE | Microdatos (Stata, SAS, SPSS) | 2024–2025 | inegi.org.mx/rnm/index.php/catalog/1116 | 🟡 MEDIA |
| 31 | ENIGH Características de Vivienda | Tipo vivienda, materiales, servicios (agua, electricidad, drenaje) | CSV | 2024 | inegi.org.mx/rnm/index.php/catalog/1116/data-dictionary | 🟡 MEDIA |

---

### M2.4 — Economía y Sectores Productivos

| # | Base de Datos | Variables Clave | Formato | Año | URL | Prioridad Vigil |
|---|---|---|---|---|---|---|
| 32 | DENUE — Directorio Económico | GIROS, coordenadas GPS, dirección, tamaño empresa, CIIU | API + Descarga masiva | Continuo | inegi.org.mx/app/mapa/denue/ | 🔴 ALTA |
| 33 | Censos Económicos 2018 | Establecimientos, personal, nómina, ventas por sector | CSV | 2018 | inegi.org.mx/app/descarga/ficha.html?tit=223754&ag=0&f=csv | 🟡 MEDIA |
| 34 | Censos Económicos 2024 | Pesca, minería, electricidad, agua, construcción, transporte, finanzas | Pendiente publicación | 2024 | inegi.org.mx/programas/ce/2024/ | 🟡 MEDIA |
| 35 | Encuesta Nacional Agropecuaria | Producción agrícola, ganado, superficie cultivada | Descarga masiva | Variable | inegi.org.mx/app/descarga/?p=1683 | 🟢 BAJA |

---

### M2.5 — Banco de Indicadores

| # | Base de Datos | Variables Clave | Formato | Año | URL | Prioridad Vigil |
|---|---|---|---|---|---|---|
| 36 | Banco de Indicadores INEGI | Demografía, Economía, Geografía, Gobierno/Seguridad | XLS, IQY, CSV, TSV | Continuo | inegi.org.mx/app/indicadores/ | 🔴 ALTA |
| 37 | Indicadores por Entidad (Nayarit) | Comparativos estatales, series históricas | Interactivo + descarga | Continuo | inegi.org.mx/app/estatal/default.aspx?ag=18 | 🔴 ALTA |
| 38 | Nayarit en Cifras (INEGI) | Indicadores por municipio | Web + tabulados | 2025 | economia.nayarit.gob.mx/nayarit-en-cifras-inegi/ | 🟡 MEDIA |
| 39 | México en Cifras — Tepic | Población, escolaridad, vivienda, economía municipal | Interactivo web | Continuo | inegi.org.mx/app/areasgeograficas?ag=18009 | 🟡 MEDIA |

---

### M2.6 — Seguridad y Justicia

| # | Base de Datos | Variables Clave | Formato | Año | URL | Prioridad Vigil |
|---|---|---|---|---|---|---|
| 40 | ENVIPE 2025 | Tasa delictiva 24,135/100k, delitos frecuentes (fraude, robo/asalto), percepción seguridad | PDF | 2025 | inegi.org.mx/contenidos/saladeprensa/boletines/2025/ENVIPE/ENVIPE_25.pdf | 🟡 MEDIA |
| 41 | Incidencia Delictiva | 41 delitos registrados desde 2010 | Web interactiva | Continuo | inegi.org.mx/temas/incidencia/ | 🟡 MEDIA |
| 42 | Criminología y Seguridad | Tipología delictiva, tasas, resolución | PDF + CSV | Continuo | inegi.org.mx/temas/gobierno-seguridad-justicia/ | 🟢 BAJA |

---

### M2.7 — Tecnología y Conectividad (ENDUTIH)

| # | Base de Datos | Variables Clave | Formato | Año | URL | Prioridad Vigil |
|---|---|---|---|---|---|---|
| 43 | ENDUTIH 2024 — Microdatos | Acceso: computadora, internet, celular; brecha digital | Microdatos (Stata, SAS, SPSS) | 2024 | inegi.org.mx/rnm/index.php/catalog/1102 | 🔴 ALTA |
| 44 | ENDUTIH Informe Operativo | Metodología, factores de expansión | PDF + DOCX | 2024 | inegi.org.mx/rnm/index.php/catalog/1102 | 🟢 BAJA |

> **Relevancia Vigil:** Brecha digital = segmentos del electorado sin presencia en redes → corrección de sesgo en PDIV.

---

### M2.8 — Geoespacial y Medio Ambiente

| # | Base de Datos | Variables Clave | Formato | Año | URL | Prioridad Vigil |
|---|---|---|---|---|---|---|
| 45 | Datos geoespaciales INEGI | Shapefiles, GeoJSON, mallas geoestadísticas, límites administrativos | SHP, GeoJSON, KML | Continuo | inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/mapas/ | 🔴 ALTA |
| 46 | Red Geodésica Nacional | Coordenadas GPS por municipio/clave, elevación | Catálogo descargable | Continuo | inegi.org.mx/temas/geodesia/ | 🟢 BAJA |
| 47 | CDGM — Imágenes Satelitales | 118,000 imágenes Landsat 1984–2020, NDVI, temperatura, uso de suelo | GeoTIFF | 1984–2020 | inegi.org.mx/investigacion/geomediana | 🟢 BAJA |
| 48 | Áreas Naturales Protegidas (IEEN Ecología) | Reservas, decretos, límites geográficos | KML, SHP, PDF | Continuo | sds.nayarit.gob.mx/datos-abiertos | 🟢 BAJA |
| 49 | Sierra de San Juan | Reserva biosfera, límites | KML, SHP | Continuo | sds.nayarit.gob.mx/datos-abiertos | 🟢 BAJA |
| 50 | Zona Metropolitana Tepic-Xalisco | Límites metropolitanos, ordenamiento urbano | KML, SHP | Continuo | sds.nayarit.gob.mx/datos-abiertos | 🔴 ALTA |

---

## M3 :: REDES SOCIALES (SCRAPED)

> ⚠️ **DATOS REALES YA DESCARGADOS** en `SERVER_TOOLBOX/centralinfo/`:
> - `dataset_facebook-comments-scraper_2026-02-20_18-34-36-980.jsonl`
> - `dataset_facebook-posts-scraper_2026-02-20_17-43-56-562.jsonl`
> - `dataset_facebook-posts-scraper_2026-02-20_17-43-56-562 (1).jsonl` ← DUPLICADO

### M3.1 — Facebook (Scraping Apify)

| # | Fuente | Actor Apify | Datos | Formato | Candidatos Monitoreados | Estado |
|---|---|---|---|---|---|---|
| 51 | Páginas Facebook Candidatos Tepic | facebook-posts-scraper | Posts, likes, shares, comentarios, fecha | JSONL | Andrea Navarro, Geraldine Ponce y otras | ✅ DESCARGADO (Feb 2026) |
| 52 | Comentarios Facebook | facebook-comments-scraper | Texto comentario, usuario hash, fecha, likes | JSONL | Mismos | ✅ DESCARGADO (Feb 2026) |
| 53 | Meta Ad Library | meta-ads-library-scraper | Anuncios políticos activos, presupuesto, alcance | JSON | Todos los candidatos Nayarit | ⏳ PENDIENTE |

### M3.2 — Instagram

| # | Fuente | Actor Apify | Datos | Estado |
|---|---|---|---|---|
| 54 | Perfiles candidatos Instagram | instagram-scraper | Posts, reels, followers, engagement | ⏳ PENDIENTE |
| 55 | Hashtags electorales (#Nayarit, #Tepic2026) | instagram-hashtag-scraper | Posts por hashtag, fecha, likes | ⏳ PENDIENTE |

### M3.3 — TikTok

| # | Fuente | Actor Apify | Datos | Estado |
|---|---|---|---|---|
| 56 | Videos candidatos TikTok | tiktok-scraper | Videos, vistas, likes, comentarios, shares | ⏳ PENDIENTE |
| 57 | Hashtags TikTok electorales | tiktok-hashtag-scraper | Hashtags #nayarit, #elecciones2026 | ⏳ PENDIENTE |

### M3.4 — YouTube

| # | Fuente | Actor Apify | Datos | Estado |
|---|---|---|---|---|
| 58 | Canal oficial candidatos YouTube | youtube-scraper | Videos, vistas, likes, comentarios | ⏳ PENDIENTE |
| 59 | Búsqueda "Nayarit elecciones 2026" | youtube-search-scraper | Videos mencionando candidatos | ⏳ PENDIENTE |

---

## M4 :: PRESUPUESTO Y TRANSPARENCIA

| # | Base de Datos | Variables Clave | Formato | URL | Prioridad Vigil |
|---|---|---|---|---|---|
| 60 | Transparencia Presupuestaria Nayarit | Gasto federal por programa en Nayarit | CSV, XLSX | transparenciapresupuestaria.gob.mx | 🟡 MEDIA |
| 61 | CONEVAL Nayarit | Pobreza multifactorial, rezago social | PDF, Excel | coneval.org.mx/coordinacion/entidades/Nayarit | 🟡 MEDIA |
| 62 | datos.gob.mx — tag "nayarit" | 6,753 bases de datos federales filtradas | CSV, JSON, XLSX, SHP | datos.gob.mx/dataset/?q=tags:nayarit | 🟡 MEDIA |
| 63 | IFT — Cobertura Telecomunicaciones | Cobertura 4G/5G por municipio | CSV, Excel | ift.org.mx | 🟡 MEDIA |
| 64 | SIGEE Nayarit (IPLANAY) | Demográfico, geográfico-ambiental, territorial, social, económico | Web, Excel | iplanay.gob.mx/sigee | 🟡 MEDIA |

---

## M5 :: DATASETS EXTERNOS / NLP

| # | Dataset | Fuente | Tamaño | Tema | Formato | Uso en Vigil |
|---|---|---|---|---|---|---|
| 65 | MexTwitter | Hugging Face | 500k tweets | Tweets políticos México en español | JSON | Fine-tuning/contexto NLP |
| 66 | MEGA — Mexican Election Twitter 2018 | Académico (figshare) | 2M tweets | Elecciones México 2018 | JSON | Referencia de framing electoral |
| 67 | Barcenas-Juridico-Mexicano | Hugging Face | — | Leyes mexicanas, plataformas electorales | JSON, CSV | Contexto legal/normativo |
| 68 | OpinionFinder español | Kaggle | 10k+ | Reseñas/opiniones en español | CSV | Benchmarking NLP |
| 69 | Twitter Conversations México | Hugging Face | 50k hilos | Conversaciones políticas México | JSON | SNA de conversaciones |

---

## M6 :: GEOESPACIAL / TERRITORIO

> Incluido en M2.8. Referencias cruzadas para operaciones GIS:

```
M6.1 → Cartografía INEGI (SHP, GeoJSON)  ← ver M2.8 #45
M6.2 → DENUE Georreferenciado            ← ver M2.4 #32
M6.3 → Zona Metropolitana Tepic-Xalisco  ← ver M2.8 #50
M6.4 → Secciones Electorales (shapefiles INE)
        URL: ine.mx/voto-y-elecciones/cartografia-y-resultado/
        Formato: SHP
        Prioridad: 🔴 ALTA — permite cruzar resultados con AGEB
```

---

## RESUMEN EJECUTIVO DE INVENTARIO

```
TOTAL DE FUENTES IDENTIFICADAS: 69 datasets/fuentes

Por módulo:
  M1 Electoral            → 20 fuentes  (INE + IEEN + Histórico)
  M2 Sociodemográfico     → 29 fuentes  (INEGI completo)
  M3 Redes Sociales       →  9 fuentes  (Facebook ✅, Instagram/TikTok/YT ⏳)
  M4 Presupuesto          →  5 fuentes
  M5 NLP Externos         →  5 fuentes
  M6 Geoespacial          →  1 adicional (Secciones INE)

Por prioridad para Vigil MVP:
  🔴 ALTA   → 19 fuentes  (descargar primero)
  🟡 MEDIA  → 24 fuentes  (segunda ola)
  🟢 BAJA   →  8 fuentes  (diferir o ignorar)

Por estado de descarga:
  ✅ DESCARGADO   →  2 archivos JSONL (Facebook Feb 2026 — SSD)
  ⏳ PENDIENTE   → 67 fuentes
```

---

## CRUCE: LO QUE TIENE SAEIL vs. LO QUE FALTA

| Fuente | ¿En SAEIL/SSD? | ¿En Vigil? | Acción |
|---|---|---|---|
| Facebook posts Tepic Feb 2026 | ✅ `centralinfo/` raíz | ❌ | **Copiar a `vigil/data/raw/`** |
| Facebook comments Tepic Feb 2026 | ✅ `centralinfo/` raíz | ❌ | **Copiar a `vigil/data/raw/`** |
| Dashboard HTML Nayarit | ✅ `SAIEL1/reports/` | ❌ | Copiar como referencia a `vigil/docs/` |
| PDIV Calculator (algoritmo) | ✅ `SAIEL1/engine/core/` | ❌ | **Migrar y adaptar con Polars** |
| Datos INE/INEGI Nayarit | ❌ | ❌ | **Descargar en este equipo → raw/** |
| Secciones electorales INE (SHP) | ❌ | ❌ | Descargar |
| CPV 2020 AGEB/manzana Nayarit | ❌ | ❌ | Descargar |
| ENOE 2025 Nayarit | ❌ | ❌ | Descargar |
| ENDUTIH 2024 microdatos | ❌ | ❌ | Descargar |

---

*Documento de referencia Vigil — no ejecutar ninguna descarga hasta confirmar con DATA_DOWNLOAD_GUIDE.md*
