"""Script de integración de punta a punta para probar y ejecutar el pipeline MVP de Vigil/FIEL."""

import logging
import os
import yaml
from pathlib import Path
import polars as pl
from dotenv import load_dotenv

from src.processing.quality_gate import ejecutar_compuerta_calidad, validar_esquema_silver, mapear_esquema_crudo
from src.analysis.semantic_agent import AgenteSemanticoElectoral
from src.graph.network_analyzer import build_entity_network, detect_louvain_communities, calculate_k_core, calcular_sincronia_cib
from src.analysis.simulator import WhatIfSimulator

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()


def main():
    logger.info("==================================================")
    logger.info("INICIANDO INTEGRACIÓN Y PRUEBA DEL MVP VIGIL (FIEL)")
    logger.info("==================================================")

    # 1. Cargar Configuración
    config_path = Path("config/config.yaml")
    if not config_path.exists():
        logger.error("No se encontró config/config.yaml. Abortando.")
        return

    with open(config_path) as f:
        config = yaml.safe_load(f)

    logger.info(f"Configuración cargada. Región: {config['metadata']['region']}")
    logger.info(f"Candidatos: {[c['nombre'] for c in config['candidatos']]}")

    # 2. Ingestar datos crudos (Fase Raw)
    posts_raw_path = Path("data/raw/facebook/fb_posts_tepic_2026-02-20.jsonl")
    comments_raw_path = Path("data/raw/facebook/fb_comments_tepic_2026-02-20.jsonl")

    if not posts_raw_path.exists() or not comments_raw_path.exists():
        logger.error("Faltan archivos de datos raw en data/raw/facebook/. Abortando.")
        return

    posts_raw = pl.read_ndjson(posts_raw_path)
    comments_raw = pl.read_ndjson(comments_raw_path)
    logger.info(f"Datos Raw cargados. Posts: {posts_raw.height}, Comentarios: {comments_raw.height}")

    # 3. Mapear y normalizar a Capa Silver + Compuerta de Calidad (Isolation Forest / PII)
    logger.info("--- Fase 2: Ejecutando Compuerta de Calidad ---")
    posts_clean = ejecutar_compuerta_calidad(posts_raw, config["catalogo_seguidores"], "DIFNay")
    comments_clean = ejecutar_compuerta_calidad(comments_raw, config["catalogo_seguidores"], "GeraldinePonceMexico")

    # Validar esquemas
    if not validar_esquema_silver(posts_clean) or not validar_esquema_silver(comments_clean):
        logger.error("Fallo de validación de esquema Silver.")
        return

    # Guardar silver procesado
    silver_dir = Path("data/silver/redes_sociales")
    silver_dir.mkdir(parents=True, exist_ok=True)
    posts_clean.write_parquet(silver_dir / "fb_posts_clean.parquet")
    comments_clean.write_parquet(silver_dir / "fb_comments_clean.parquet")
    logger.info("Capa Silver guardada exitosamente.")

    # 4. Inferencia Semántica NLP (Capas Silver -> Gold)
    logger.info("--- Fase 3: Ejecutando Enriquecimiento Semántico NLP ---")
    # Para el MVP, asociamos cada post/comentario con su candidato correspondiente
    posts_clean = posts_clean.with_columns(pl.lit("Beatriz Estrada").alias("candidato"))
    comments_clean = comments_clean.with_columns(pl.lit("Geraldine Ponce").alias("candidato"))

    agente = AgenteSemanticoElectoral()
    posts_enriched = agente.clasificar_dataframe(posts_clean, "texto_publicacion")
    comments_enriched = agente.clasificar_dataframe(comments_clean, "texto_publicacion")

    # Guardar en Gold
    gold_dir = Path("data/gold/redes_sociales")
    gold_dir.mkdir(parents=True, exist_ok=True)
    posts_enriched.write_parquet(gold_dir / "fb_posts_gold.parquet")
    comments_enriched.write_parquet(gold_dir / "fb_comments_gold.parquet")
    logger.info("Capa Gold guardada exitosamente.")

    # 5. Análisis de Redes (SNA & CIB)
    logger.info("--- Fase 4: Ejecutando Análisis de Redes (SNA) ---")
    alertas_cib = calcular_sincronia_cib(posts_enriched)
    logger.info(f"Alertas CIB encontradas: {len(alertas_cib)}")

    # Unir datasets para el grafo
    df_combined = pl.concat([
        posts_enriched.select(["keywords_extracted", "texto_publicacion"]),
        comments_enriched.select(["keywords_extracted", "texto_publicacion"])
    ])

    G = build_entity_network(df_combined)
    comunidades = detect_louvain_communities(G)
    G_core = calculate_k_core(G, k=2)
    logger.info(f"Nodos en el K-Core (k=2): {len(G_core.nodes)}")

    # 6. Simulación What-If y Reporte Final
    logger.info("--- Fase 5: Ejecutando Simulación Estratégica ---")
    df_gold = pl.concat([
        posts_enriched.select(["candidato", "sentimiento", "reacciones_totales", "texto_publicacion", "keywords_extracted"]),
        comments_enriched.select(["candidato", "sentimiento", "reacciones_totales", "texto_publicacion", "keywords_extracted"])
    ])

    simulator = WhatIfSimulator()
    df_base = simulator.calcular_scores_base(df_gold)
    logger.info("Línea base PDIV calculada:")
    print(df_base.select(["candidato", "pdiv_score", "sentimiento_score", "volumen_score", "engagement_score"]))

    # Simular cambios de tema (enriquecimiento sobre temas de Gestión)
    ajustes = {"amor": 0.40, "cercanía": 0.30}
    df_sim = simulator.simular_cambio_temas(df_gold, "Beatriz Estrada", ajustes)
    logger.info("Escenario de simulación calculado:")
    print(df_sim)

    # 7. Generar reporte Markdown final
    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    reporte_path = reports_dir / "reporte_semanal_2026-06-01.md"

    with open(reporte_path, "w", encoding="utf-8") as f:
        f.write("# REPORTE SEMANAL DE INTELIGENCIA ELECTORAL (FIEL MVP)\n")
        f.write("Fecha de corte: 2026-06-01 | Análisis de Ecosistema Tepic 2026\n\n")

        f.write("## 1. Índice de Posicionamiento Digital (PDIV)\n")
        f.write("El PDIV resume las métricas de Sentimiento, Volumen y Engagement:\n\n")

        f.write("| Candidato | PDIV Score | Sentimiento Score | Volumen Score | Engagement Score |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: |\n")
        for row in df_base.iter_rows(named=True):
            f.write(f"| **{row['candidato']}** | {round(row['pdiv_score'], 2)} | {round(row['sentimiento_score'], 2)} | {round(row['volumen_score'], 2)} | {round(row['engagement_score'], 2)} |\n")

        f.write("\n## 2. Detección de Coordinación Sospechosa (CIB)\n")
        if alertas_cib:
            f.write("Se han detectado indicios de comportamiento inauténtico coordinado:\n\n")
            for idx, a in enumerate(alertas_cib):
                f.write(f"- **Alerta {idx+1} ({a['status']})**: Sincronía $S_T$ = **{a['sincronia_s_t']}** | Desviación: {a['desviacion_segundos']}s\n")
                f.write(f"  * Páginas: {', '.join(a['paginas_involucradas'])}\n")
                f.write(f"  * Texto: *\"{a['texto_coordinado']}\"*\n")
        else:
            f.write("No se detectó actividad de publicación síncrona sospechosa ($S_T > 0.85$ en ventana de 300s).\n")

        f.write("\n## 3. Análisis de Sensibilidad Temática (What-If Simulator)\n")
        f.write("Simulación de incremento de +40% en tópicos de Gestión Social ('amor', 'cercanía') para Beatriz Estrada:\n\n")

        f.write("| Candidato | PDIV Base | PDIV Simulado | Diferencia | Sentimiento Simulado |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: |\n")
        for row in df_sim.iter_rows(named=True):
            f.write(f"| **{row['candidato']}** | {round(row['pdiv_score'], 2)} | {round(row['pdiv_score_sim'], 2)} | **{row['dif_pdiv']}** | {round(row['sentimiento_score_sim'], 2)} |\n")

        f.write("\n\n*Informe de consultoría técnica generado automáticamente por FIEL MVP.*")

    logger.info(f"==================================================")
    logger.info(f"PROCESAMIENTO EXITOSO. REPORTE EN: {reporte_path}")
    logger.info(f"==================================================")


if __name__ == "__main__":
    main()
