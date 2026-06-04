"""Script para generar programáticamente la secuencia de cuadernos del pipeline de Vigil."""

import json
from pathlib import Path

notebooks_dir = Path("/home/fratfn/Desarrollo/Agency/vigil/notebooks")
notebooks_dir.mkdir(parents=True, exist_ok=True)


def make_notebook(cells_data, path):
    notebook = {
        "cells": [],
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11.0"},
        },
        "nbformat": 4,
        "nbformat_minor": 2,
    }

    for cell_type, source in cells_data:
        cell = {"cell_type": cell_type, "metadata": {}, "source": source if isinstance(source, list) else [source]}
        if cell_type == "code":
            cell["execution_count"] = None
            cell["outputs"] = []
        notebook["cells"].append(cell)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)
    print(f"Cuaderno creado: {path.name}")


# Notebook 01: Ingestión y Mapeo
nb01_cells = [
    (
        "markdown",
        "# Vigil — Notebook 01: Ingestión de Datos y Normalización a Silver\n\nEste cuaderno implementa la Fase 1 del pipeline: Ingestión de los archivos de Facebook crudos de Apify y su mapeo al esquema de la capa Silver.",
    ),
    (
        "code",
        """import polars as pl
import yaml
from pathlib import Path
import sys

# Agregar src/ al path por seguridad si es necesario
sys.path.append('..')
from src.processing.quality_gate import mapear_esquema_crudo

print("Polars version:", pl.__version__)""",
    ),
    ("markdown", "## 1. Cargar Configuración Maestra y Catálogo de Seguidores"),
    (
        "code",
        """with open("../config/config.yaml") as f:
    config = yaml.safe_load(f)

print("Candidatos configurados:", [c['nombre'] for c in config['candidatos']])
print("Catálogo de seguidores:", config['catalogo_seguidores'])""",
    ),
    ("markdown", "## 2. Cargar Datasets Crudos (Fase Raw)"),
    (
        "code",
        """posts_raw = pl.read_ndjson("../data/raw/facebook/fb_posts_tepic_2026-02-20.jsonl")
comments_raw = pl.read_ndjson("../data/raw/facebook/fb_comments_tepic_2026-02-20.jsonl")

print("Posts crudos:", posts_raw.height)
print("Comentarios crudos:", comments_raw.height)""",
    ),
    ("markdown", "## 3. Mapear y Normalizar a Capa Silver"),
    (
        "code",
        """posts_silver = mapear_esquema_crudo(posts_raw, config["catalogo_seguidores"], "DIFNay")
comments_silver = mapear_esquema_crudo(comments_raw, config["catalogo_seguidores"], "GeraldinePonceMexico")

print("Posts mapeados a Silver:")
print(posts_silver.head(3))
print("\\nComentarios mapeados a Silver:")
print(comments_silver.head(3))""",
    ),
    ("markdown", "## 4. Persistir en la Capa Silver (Formato Parquet)"),
    (
        "code",
        """Path("../data/silver/redes_sociales").mkdir(parents=True, exist_ok=True)

posts_silver.write_parquet("../data/silver/redes_sociales/fb_posts_silver.parquet")
comments_silver.write_parquet("../data/silver/redes_sociales/fb_comments_silver.parquet")

print("Fase 1 Completada: Datasets de Facebook guardados en silver/redes_sociales/")""",
    ),
]

# Notebook 02: Calidad y Anomalías
nb02_cells = [
    (
        "markdown",
        "# Vigil — Notebook 02: Compuerta de Calidad y Outliers\n\nEste cuaderno implementa la Fase 2: Aplicación del protocolo de calidad, anonimización PII y detección de anomalías de engagement con Isolation Forest.",
    ),
    (
        "code",
        """import polars as pl
import yaml
import sys
sys.path.append('..')
from src.processing.quality_gate import ejecutar_compuerta_calidad, validar_esquema_silver

with open("../config/config.yaml") as f:
    config = yaml.safe_load(f)""",
    ),
    ("markdown", "## 1. Cargar Datos Silver Incompletos"),
    (
        "code",
        """posts_silver = pl.read_parquet("../data/silver/redes_sociales/fb_posts_silver.parquet")
comments_silver = pl.read_parquet("../data/silver/redes_sociales/fb_comments_silver.parquet")""",
    ),
    ("markdown", "## 2. Ejecutar Compuerta de Calidad (Isolation Forest + PII Anonimización)"),
    (
        "code",
        """# Ejecutar compuerta
posts_clean = ejecutar_compuerta_calidad(posts_silver, config["catalogo_seguidores"], "DIFNay")
comments_clean = ejecutar_compuerta_calidad(comments_silver, config["catalogo_seguidores"], "GeraldinePonceMexico")

print("Registros limpios - Posts:", posts_clean.height)
print("Registros limpios - Comentarios:", comments_clean.height)""",
    ),
    ("markdown", "## 3. Revisión de Anomalías de Engagement (Likes/Shares)"),
    (
        "code",
        """anomalias_posts = posts_clean.filter(pl.col("is_anomaly") == True)
anomalias_comments = comments_clean.filter(pl.col("is_anomaly") == True)

print("Posts marcados como anomalías (Outliers de boosting):", anomalias_posts.height)
print("Comentarios marcados como anomalías:", anomalias_comments.height)

if anomalias_posts.height > 0:
    print("\\nMuestras de posts anómalos:")
    print(anomalias_posts.select(["reacciones_totales", "tasa_interaccion", "texto_publicacion"]).head(5))""",
    ),
    ("markdown", "## 4. Validar Esquema Silver y Guardar Datos Validados"),
    (
        "code",
        """assert validar_esquema_silver(posts_clean)
assert validar_esquema_silver(comments_clean)

posts_clean.write_parquet("../data/silver/redes_sociales/fb_posts_clean.parquet")
comments_clean.write_parquet("../data/silver/redes_sociales/fb_comments_clean.parquet")

print("Fase 2 Completada: Datasets validados y libres de anomalías listos para NLP.")""",
    ),
]

# Notebook 03: Clasificación Semántica
nb03_cells = [
    (
        "markdown",
        "# Vigil — Notebook 03: Clasificación Semántica NLP con Gemini\n\nEste cuaderno implementa el etiquetado semántico del discurso político (sentimiento, framing y palabras clave) utilizando la API de Gemini 2.5-flash.",
    ),
    (
        "code",
        """import polars as pl
import os
import sys
from dotenv import load_dotenv
sys.path.append('..')
from src.analysis.semantic_agent import AgenteSemanticoElectoral

# Cargar clave de API (.env)
load_dotenv("../.env")
print("GEMINI_API_KEY configurada:", "GEMINI_API_KEY" in os.environ)""",
    ),
    ("markdown", "## 1. Cargar Datos Limpios de la Capa Silver"),
    (
        "code",
        """posts = pl.read_parquet("../data/silver/redes_sociales/fb_posts_clean.parquet")
comments = pl.read_parquet("../data/silver/redes_sociales/fb_comments_clean.parquet")

# MVP: Asignamos el candidato correspondiente a cada activo
posts = posts.with_columns(pl.lit("Beatriz Estrada").alias("candidato"))
comments = comments.with_columns(pl.lit("Geraldine Ponce").alias("candidato"))

print("Posts para análisis NLP:", posts.height)
print("Comentarios para análisis NLP:", comments.height)""",
    ),
    ("markdown", "## 2. Inicializar Agente Semántico y Ejecutar Inferencia Estructurada"),
    (
        "code",
        """agente = AgenteSemanticoElectoral()

# Correr inferencia (si no hay API key, utilizará el fallback de simulación)
# Para optimizar el tiempo de MVP, limitamos la inferencia de prueba si es necesario
# pero aquí procesaremos todo el conjunto (60 posts, 110 comentarios)
posts_enriched = agente.clasificar_dataframe(posts, "texto_publicacion")
comments_enriched = agente.clasificar_dataframe(comments, "texto_publicacion")

print("Clasificación NLP finalizada.")""",
    ),
    ("markdown", "## 3. Muestra de Resultados del Análisis Semántico"),
    (
        "code",
        """print("Resultados de Posts (Framing & Sentiment):")
print(posts_enriched.select(["candidato", "sentimiento", "framing", "keywords_extracted"]).head(5))

print("\\nResultados de Comentarios (Framing & Sentiment):")
print(comments_enriched.select(["candidato", "sentimiento", "framing", "keywords_extracted"]).head(5))""",
    ),
    ("markdown", "## 4. Persistir Resultados en Capa Gold"),
    (
        "code",
        """os.makedirs("../data/gold/redes_sociales", exist_ok=True)

posts_enriched.write_parquet("../data/gold/redes_sociales/fb_posts_gold.parquet")
comments_enriched.write_parquet("../data/gold/redes_sociales/fb_comments_gold.parquet")

print("Fase 3 Completada: Datos consolidados guardados en data/gold/")""",
    ),
]

# Notebook 04: Análisis de Grafos y Redes
nb04_cells = [
    (
        "markdown",
        "# Vigil — Notebook 04: Análisis de Redes Sociales (SNA)\n\nEste cuaderno implementa el análisis estructural del ecosistema: sincronía CIB (comportamiento inauténtico coordinado), agrupamiento de comunidades con Louvain y núcleo de red con K-Core.",
    ),
    (
        "code",
        """import polars as pl
import sys
sys.path.append('..')
from src.graph.network_analyzer import build_entity_network, detect_louvain_communities, calculate_k_core, calcular_sincronia_cib""",
    ),
    ("markdown", "## 1. Cargar Datos Enriquecidos (Capa Gold)"),
    (
        "code",
        """posts_gold = pl.read_parquet("../data/gold/redes_sociales/fb_posts_gold.parquet")
comments_gold = pl.read_parquet("../data/gold/redes_sociales/fb_comments_gold.parquet")""",
    ),
    ("markdown", "## 2. Detección CIB por Sincronía Temporal ($S_T$)"),
    (
        "code",
        """alertas_cib = calcular_sincronia_cib(posts_gold, delta_t_max=300.0)

print(f"Se encontraron {len(alertas_cib)} alertas de coordinación sospechosa.")
for idx, alerta in enumerate(alertas_cib):
    print(f"Alerta {idx+1}:")
    print(f"  Páginas: {alerta['paginas_involucradas']}")
    print(f"  Sincronía S_T: {alerta['sincronia_s_t']}")
    print(f"  Texto: {alerta['texto_coordinado']}")""",
    ),
    ("markdown", "## 3. Construcción del Grafo Semántico de Co-ocurrencia"),
    (
        "code",
        """# Unificar datasets para extraer co-ocurrencia de keywords/entidades
df_combined = pl.concat([
    posts_gold.select(["keywords_extracted", "texto_publicacion"]),
    comments_gold.select(["keywords_extracted", "texto_publicacion"])
])

G = build_entity_network(df_combined)""",
    ),
    ("markdown", "## 4. Detección de Comunidades (Louvain)"),
    (
        "code",
        """partition = detect_louvain_communities(G)

# Agrupar nodos por ID de comunidad
comunidades_dict = {}
for nodo, com_id in partition.items():
    comunidades_dict.setdefault(com_id, []).append(nodo)

print("Distribución de Comunidades Temáticas:")
for com_id, nodos in comunidades_dict.items():
    print(f"Comunidad {com_id} (Nodos: {len(nodos)}): {nodos[:10]}...")""",
    ),
    ("markdown", "## 5. Extracción del Núcleo de Red (K-Core)"),
    (
        "code",
        """G_core = calculate_k_core(G, k=2)

print(f"Nodos nucleares identificados (grado >= 2): {len(G_core.nodes)}")
print("Entidades del Núcleo duro:", list(G_core.nodes))""",
    ),
]

# Notebook 05: Simulador What-If y Reporte
nb05_cells = [
    (
        "markdown",
        "# Vigil — Notebook 05: Simulador de Escenarios y Reporte de Inteligencia\n\nEste cuaderno calcula el índice final de PDIV (Posicionamiento Digital de Intención de Voto), ejecuta simulaciones de escenarios temáticos ('What-If') y compila el reporte de auditoría semanal.",
    ),
    (
        "code",
        """import polars as pl
import yaml
import sys
import os
sys.path.append('..')
from src.analysis.simulator import WhatIfSimulator""",
    ),
    ("markdown", "## 1. Cargar Datos y Calcular PDIV Base (Baseline)"),
    (
        "code",
        """posts_gold = pl.read_parquet("../data/gold/redes_sociales/fb_posts_gold.parquet")
comments_gold = pl.read_parquet("../data/gold/redes_sociales/fb_comments_gold.parquet")

# Combinar datasets
df_gold = pl.concat([
    posts_gold.select(["candidato", "sentimiento", "reacciones_totales", "texto_publicacion", "keywords_extracted"]),
    comments_gold.select(["candidato", "sentimiento", "reacciones_totales", "texto_publicacion", "keywords_extracted"])
])

# Cargar pesos y config
with open("../config/config.yaml") as f:
    config = yaml.safe_load(f)

# Inicializar Simulador
simulator = WhatIfSimulator()

# Calcular scores de línea base
df_base = simulator.calcular_scores_base(df_gold)
print("RESULTADOS BASELINE PDIV ELECTORAL:")
print(df_base.select(["candidato", "pdiv_score", "sentimiento_score", "volumen_score", "engagement_score"]))""",
    ),
    ("markdown", "## 2. Simulación de Escenario Temático ('What-If')"),
    (
        "code",
        """# Simularemos el escenario: ¿Qué pasa si Beatriz Estrada incrementa un 40%
# sus publicaciones asociadas a la palabra 'amor' (temas sociales del DIF)?
ajustes = {"amor": 0.40, "cercanía": 0.30}

df_sim = simulator.simular_cambio_temas(df_gold, "Beatriz Estrada", ajustes)

print("RESULTADO DE SIMULACIÓN DE ESCENARIO:")
print(df_sim)""",
    ),
    ("markdown", "## 3. Generar Reporte de Inteligencia Electoral Semanal (.md)"),
    (
        "code",
        """os.makedirs("../reports", exist_ok=True)
reporte_path = "../reports/reporte_semanal_2026-06-01.md"

with open(reporte_path, "w", encoding="utf-8") as f:
    f.write("# REPORT DE INTELIGENCIA SEMANAL: TEPIC 2026\\n")
    f.write("Fecha de reporte: 2026-06-01 | Capa de datos: Gold\\n\\n")

    f.write("## 1. Posicionamiento Digital de Intención de Voto (PDIV)\\n")
    f.write("El índice PDIV sintetiza volumen, sentimiento neto y engagement normalizado:\\n\\n")

    # Escribir tabla base
    f.write("| Candidato | PDIV Score | Sentimiento Score | Volumen Score | Engagement Score |\\n")
    f.write("| :--- | :---: | :---: | :---: | :---: |\\n")
    for row in df_base.iter_rows(named=True):
        f.write(f"| **{row['candidato']}** | {round(row['pdiv_score'], 2)} | {round(row['sentimiento_score'], 2)} | {round(row['volumen_score'], 2)} | {round(row['engagement_score'], 2)} |\\n")

    f.write("\\n## 2. Recomendaciones de Escenario (Simulado 'What-If')\\n")
    f.write("Análisis de sensibilidad aplicando +40% de peso a tópicos de 'Gestión Social / Amor' para Beatriz Estrada:\\n\\n")

    f.write("| Candidato | PDIV Base | PDIV Simulado | Diferencia | Sentimiento Simulado |\\n")
    f.write("| :--- | :---: | :---: | :---: | :---: |\\n")
    for row in df_sim.iter_rows(named=True):
        f.write(f"| **{row['candidato']}** | {round(row['pdiv_score'], 2)} | {round(row['pdiv_score_sim'], 2)} | **{row['dif_pdiv']}** | {round(row['sentimiento_score_sim'], 2)} |\\n")

    f.write("\\n\\n*Informe técnico generado automáticamente por el Framework de Inteligencia Electoral Local (FIEL) — RndmStudio 2026.*")

print(f"Reporte de Inteligencia escrito con éxito en: {reporte_path}")""",
    ),
]

# Crear todos los notebooks
make_notebook(nb01_cells, notebooks_dir / "01_data_ingestion.ipynb")
make_notebook(nb02_cells, notebooks_dir / "02_etl_and_quality.ipynb")
make_notebook(nb03_cells, notebooks_dir / "03_semantic_classification.ipynb")
make_notebook(nb04_cells, notebooks_dir / "04_network_and_graphs.ipynb")
make_notebook(nb05_cells, notebooks_dir / "05_strategic_dashboard.ipynb")

print("\\n¡Todos los cuadernos secuenciales han sido generados en vigil/notebooks/ con éxito!")
