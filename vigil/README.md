# Vigil — Sistema de Análisis Electoral e Inteligencia Local

Sistema agnóstico de perfilamiento y monitoreo digital de procesos electorales. Proyecto **RndmStudio**.

## Setup rápido

```bash
# 1. Clonar y entrar al proyecto
cd /home/fnfrater/Escritorio/RndmStudio/vigil

# 2. Crear entorno virtual
python3 -m venv .venv && source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar credenciales
cp .env.example .env
# Edita .env con tus claves reales

# 5. Configurar candidatos y región
# Edita config/config.yaml

# 6. Abrir notebook de setup
jupyter lab notebooks/00_setup_and_config.ipynb
```

## Flujo de notebooks

| Notebook | Descripción |
|---|---|
| `00_setup_and_config.ipynb` | Verificación de entorno y credenciales Vigil |
| `01_data_ingestion_apify.ipynb` | Scraping de páginas Facebook + Meta Ad Library |
| `02_etl_quality_gate.ipynb` | ETL con Polars: limpieza, ER, CAR, filtros |
| `03_nlp_classification.ipynb` | Clasificación NLP con Gemini 2.5-flash |
| `04_sna_network_graph.ipynb` | Grafo de ecosistema + detección CIB (NetworkX/Louvain) |
| `05_report_generator.ipynb` | Generación del reporte final en Markdown |

## MCP Servers (opcionales, activar bajo demanda)

Ver `config/mcp.json` para configuración. **No activar todos a la vez** — impacto en RAM.

- **vigil-filesystem**: acceso del IDE a `docs/`, `data/gold/`, `reports/`
- **vigil-db** (`mcp-toolbox`): consultas Neo4j en lenguaje natural — activar cuando tengas datos en Aura
- **notebooklm**: síntesis de documentos largos — activar solo para consultas puntuales

### Ejecutar mcp-toolbox manualmente (cuando sea necesario)

```bash
source .venv/bin/activate
./bin/toolbox --config config/tools.yaml
```

## Estructura del proyecto

```
vigil/
├── .env                    # Credenciales (gitignored)
├── .env.example            # Template de credenciales
├── .venv/                  # Entorno virtual Python (gitignored)
├── .notebooklm/            # Auth notebooklm-mcp-cli (gitignored, symlink desde ~/.notebooklm-mcp-cli)
├── requirements.txt
├── config/
│   ├── config.yaml         # Configuración activa de la elección
│   ├── tools.yaml          # MCP Toolbox — herramientas Neo4j
│   ├── mcp.json            # Configuración MCP para el IDE
│   └── templates/          # Configuraciones para otras demarcaciones
├── notebooks/              # Análisis y reporte (ejecutar en orden)
├── src/                    # Scripts Python para automatización
│   ├── ingestion/
│   ├── processing/
│   ├── analysis/
│   └── graph/
├── data/
│   ├── raw/                # Datos crudos de Apify (gitignored)
│   ├── silver/             # Datos limpios Polars (gitignored)
│   └── gold/               # Datos para reporte (gitignored)
├── bin/
│   └── toolbox             # Binario mcp-toolbox v1.3.0 (gitignored)
├── docs/                   # Documentación del proyecto
├── reports/                # Reportes generados (gitignored)
└── evals/                  # Auditorías de calidad (gitignored)
```
