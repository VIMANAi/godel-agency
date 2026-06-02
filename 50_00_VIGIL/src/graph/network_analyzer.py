"""Módulo de análisis de redes sociales (SNA) para Vigil.

Implementa la construcción del grafo del ecosistema digital,
la partición de comunidades de Louvain, la descomposición K-Core
y el algoritmo de detección de comportamiento inauténtico coordinado (CIB).
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Tuple
import polars as pl
import networkx as nx
import community as community_louvain
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def build_entity_network(df_nlp: pl.DataFrame) -> nx.Graph:
    """Construye un grafo no dirigido de co-ocurrencia semántica a partir de entidades NLP.

    Cada nodo es una entidad (Candidato, Tema, Zona geográfica).
    Cada arista representa la mención conjunta de ambas entidades en la misma publicación/comentario.
    """
    logger.info("Construyendo grafo semántico de co-ocurrencia.")
    G = nx.Graph()

    # Se asume que df_nlp tiene la columna 'entities' (lista de strings) o similar
    # Si viene del JSON de Gemini, estará como una columna estructurada de Polars
    for row in df_nlp.iter_rows(named=True):
        entidades = row.get("entities", row.get("keywords_extracted", []))
        if not entidades or not isinstance(entidades, list):
            continue
            
        # Filtrar entidades vacías o indeterminadas
        entidades = [e.strip() for e in entidades if e and str(e).strip().lower() not in ["indeterminado", "null", "none"]]
        
        # Agregar relaciones de co-ocurrencia
        for i in range(len(entidades)):
            ent_a = entidades[i]
            # Incrementar peso del nodo o agregarlo
            if G.has_node(ent_a):
                G.nodes[ent_a]["weight"] = G.nodes[ent_a].get("weight", 0) + 1
            else:
                G.add_node(ent_a, weight=1)
                
            for j in range(i + 1, len(entidades)):
                ent_b = entidades[j]
                if G.has_edge(ent_a, ent_b):
                    G[ent_a][ent_b]["weight"] = G[ent_a][ent_b]["weight"] + 1
                else:
                    G.add_edge(ent_a, ent_b, weight=1)

    logger.info(f"Grafo construido con {G.number_of_nodes()} nodos y {G.number_of_edges()} aristas.")
    return G


def detect_louvain_communities(G: nx.Graph) -> Dict[str, int]:
    """Clasifica los nodos del grafo en comunidades utilizando el algoritmo de Louvain.

    Retorna un diccionario {nombre_nodo: id_comunidad}.
    """
    if G.number_of_nodes() == 0:
        return {}

    logger.info("Calculando partición de comunidades de Louvain.")
    try:
        partition = community_louvain.best_partition(G, weight="weight")
        unique_coms = set(partition.values())
        logger.info(f"Detección completada. Se identificaron {len(unique_coms)} comunidades.")
        return partition
    except Exception as e:
        logger.error(f"Error en algoritmo de Louvain: {e}")
        return {node: 0 for node in G.nodes}


def calculate_k_core(G: nx.Graph, k: int = 2) -> nx.Graph:
    """Extrae el subgrafo K-Core de grado k.

    Útil para aislar el 'núcleo duro' de propagación narrativa y eliminar nodos satélites.
    """
    if G.number_of_nodes() == 0:
        return G

    logger.info(f"Calculando K-Core con umbral k={k}.")
    
    # K-core requiere eliminar self-loops
    G_clean = G.copy()
    G_clean.remove_edges_from(nx.selfloop_edges(G_clean))
    
    try:
        k_core = nx.k_core(G_clean, k=k)
        logger.info(f"K-Core extraído con {k_core.number_of_nodes()} nodos nucleares.")
        return k_core
    except Exception as e:
        logger.warning(f"No se pudo calcular K-Core (posiblemente grado insuficiente): {e}")
        return nx.Graph()


def calcular_sincronia_cib(df_posts: pl.DataFrame, delta_t_max: float = 300.0) -> List[Dict[str, Any]]:
    """Detecta comportamiento inauténtico coordinado (CIB) mediante sincronía de publicación.

    Identifica grupos de publicaciones con texto idéntico y calcula el score de sincronía S_T.
    Si S_T > 0.85, se reporta como una anomalía coordinada.
    """
    logger.info("Analizando sincronía de publicación para detección CIB.")
    
    # Verificar columnas de fecha y texto
    cols = df_posts.columns
    if "texto_publicacion" not in cols or "fecha" not in cols:
        logger.warning("Faltan columnas de fecha o texto en el DataFrame de posts.")
        return []

    # Agrupar posts por contenido exacto de texto
    # Filtramos textos muy cortos o genéricos para evitar falsos positivos
    df_agrupado = (
        df_posts.filter(pl.col("texto_publicacion").str.len_chars() > 15)
        .group_by("texto_publicacion")
        .agg([
            pl.col("fecha").alias("timestamps"),
            pl.col("id_activo").alias("paginas_emisoras"),
            pl.col("url").alias("urls_publicaciones"),
            pl.count().alias("cantidad_duplicados")
        ])
        .filter(pl.col("cantidad_duplicados") > 1)
    )

    alertas_cib = []
    
    for row in df_agrupado.iter_rows(named=True):
        timestamps = row["timestamps"]
        
        # Convertir timestamps a objetos datetime e ISO
        dts = []
        for t in timestamps:
            if isinstance(t, str):
                try:
                    # Intentar parsear fecha ISO
                    dts.append(datetime.fromisoformat(t.replace("Z", "+00:00")))
                except ValueError:
                    continue
            elif isinstance(t, datetime):
                dts.append(t)
                
        if len(dts) < 2:
            continue
            
        # Calcular timestamps numéricos (en segundos)
        timestamps_seg = [dt.timestamp() for dt in dts]
        
        # Calcular desviación estándar
        std_dev = float(np.std(timestamps_seg))
        
        # Calcular score S_T
        # Si la desviación es mayor que delta_t_max, la sincronía es baja/cero
        if std_dev >= delta_t_max:
            s_t = 0.0
        else:
            s_t = 1.0 - (std_dev / delta_t_max)
            
        if s_t > 0.85:
            alertas_cib.append({
                "texto_coordinado": row["texto_publicacion"][:150] + "...",
                "paginas_involucradas": list(set(row["paginas_emisoras"])),
                "urls": row["urls_publicaciones"],
                "cantidad": row["cantidad_duplicados"],
                "desviacion_segundos": round(std_dev, 2),
                "sincronia_s_t": round(s_t, 3),
                "status": "COORDINATION_SUSPECT"
            })
            logger.warning(
                f"[COORDINATION_SUSPECT] Detectada sincronía de {round(s_t, 2)} "
                f"entre {row['cantidad_duplicados']} páginas para una publicación idéntica."
            )

    return alertas_cib
