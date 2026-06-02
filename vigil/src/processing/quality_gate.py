"""Módulo de compuerta de calidad de datos para Vigil.

Implementa el flujo ETL: raw/ -> validación (Polars) -> silver/
Módulo central de validación, normalización de datos y detección de anomalías.
"""

import logging
import re
from datetime import date
from typing import Dict, Any

import polars as pl
import numpy as np
from sklearn.ensemble import IsolationForest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

MVD_MINIMO = 50


def anonimizar_polars(df: pl.DataFrame, columna: str) -> pl.DataFrame:
    """Aplica regex de anonimización PII en una columna de texto en Polars.

    Remueve menciones de usuario (@username), correos electrónicos y teléfonos.
    """
    # Expresión regular para usernames
    rx_user = r"@[a-zA-Z0-9._]+"
    # Expresión regular para emails
    rx_email = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    # Expresión regular para teléfonos (heurística simple para evitar borrar números normales)
    rx_phone = r"\+?[0-9\s-]{9,15}"

    return df.with_columns(
        pl.col(columna)
        .str.replace_all(rx_user, "[USUARIO_ANONIMO]")
        .str.replace_all(rx_email, "[CORREO_ANONIMO]")
        .str.replace_all(rx_phone, "[TELEFONO_ANONIMO]")
        .alias(columna)
    )


def mapear_esquema_crudo(df_crudo: pl.DataFrame, catalogo_seguidores: Dict[str, int], fuente_nombre: str) -> pl.DataFrame:
    """Detecta las columnas del dataset crudo y las estandariza al esquema Silver.

    Mapea campos como text, likes, shares, comments, likesCount.
    """
    logger.info(f"Normalizando esquema crudo para fuente: {fuente_nombre}")
    
    # 1. Determinar el tipo de datos (Posts o Comments)
    cols = df_crudo.columns
    
    # Mapeo por defecto de columnas obligatorias
    id_activo = pl.lit(fuente_nombre).alias("id_activo")
    plataforma = pl.lit("facebook").alias("plataforma")
    texto_publicacion = pl.lit("").alias("texto_publicacion")
    reacciones_totales = pl.lit(0, dtype=pl.Int64).alias("reacciones_totales")
    fecha = pl.lit(date.today().isoformat()).alias("fecha")
    url = pl.lit("").alias("url")

    # Si es un dataset de POSTS (tiene likes, comments, shares, etc.)
    if "text" in cols and ("likes" in cols or "shares" in cols or "comments" in cols):
        texto_publicacion = pl.col("text").fill_null("").alias("texto_publicacion")
        
        # Sumar reacciones totales
        likes_expr = pl.col("likes").fill_null(0) if "likes" in cols else pl.lit(0)
        shares_expr = pl.col("shares").fill_null(0) if "shares" in cols else pl.lit(0)
        comments_expr = pl.col("comments").fill_null(0) if "comments" in cols else pl.lit(0)
        reacciones_totales = (likes_expr + shares_expr + comments_expr).cast(pl.Int64).alias("reacciones_totales")
        
        if "url" in cols:
            url = pl.col("url").alias("url")
            # Extraer el identificador de la página de la URL
            id_activo = (
                pl.col("url")
                .str.extract(r"facebook\.com/([^/]+)/")
                .fill_null(fuente_nombre)
                .alias("id_activo")
            )
            
    # Si es un dataset de COMENTARIOS (tiene postTitle, text, likesCount, facebookUrl)
    elif "text" in cols and "likesCount" in cols:
        texto_publicacion = pl.col("text").fill_null("").alias("texto_publicacion")
        reacciones_totales = pl.col("likesCount").fill_null(0).cast(pl.Int64).alias("reacciones_totales")
        
        if "facebookUrl" in cols:
            url = pl.col("facebookUrl").alias("url")
            # En comentarios, asignamos el canal como el handle del candidato principal
            # Se intentará extraer del postTitle o URL, o se usa el default de la ingesta
            id_activo = pl.lit(fuente_nombre).alias("id_activo")

    # Crear el dataframe base normalizado
    df_normalizado = df_crudo.select([
        id_activo,
        plataforma,
        texto_publicacion,
        reacciones_totales,
        url,
        fecha
    ])

    # 2. Agregar número de seguidores desde el catálogo
    # Convertimos las llaves del catálogo a expresiones Polars
    # Si no se encuentra en el catálogo, por defecto se asignan 500 seguidores
    df_normalizado = df_normalizado.with_columns(
        pl.col("id_activo")
        .replace(catalogo_seguidores, default=500)
        .cast(pl.Int64)
        .alias("seguidores_cuenta_origen")
    )

    # 3. Calcular tasa de interacción
    df_normalizado = df_normalizado.with_columns(
        pl.when(pl.col("seguidores_cuenta_origen") > 0)
        .then(pl.col("reacciones_totales") / pl.col("seguidores_cuenta_origen"))
        .otherwise(0.0)
        .alias("tasa_interaccion")
    )

    # 4. Agregar metadatos de capa
    df_normalizado = df_normalizado.with_columns([
        pl.lit("facebook_apify").alias("_fuente"),
        pl.lit(date.today().isoformat()).alias("_fecha_ingesta"),
        pl.lit(True).alias("is_valid"),
    ])

    # 5. Aplicar anonimización PII sobre la columna de texto
    df_normalizado = anonimizar_polars(df_normalizado, "texto_publicacion")

    return df_normalizado


def detectar_anomalias_engagement(df: pl.DataFrame, contamination: float = 0.05) -> pl.DataFrame:
    """Utiliza un Isolation Forest de scikit-learn para detectar anomalías de engagement.

    Agrega la columna booleana 'is_anomaly' al DataFrame.
    """
    if df.height == 0:
        return df.with_columns(pl.lit(False).alias("is_anomaly"))

    logger.info("Entrenando Isolation Forest para detección de anomalías en engagement.")
    
    # Extraer variables para entrenamiento
    features = df.select(["reacciones_totales", "tasa_interaccion"]).to_numpy()
    
    # Rellenar NaNs por seguridad
    features = np.nan_to_num(features, nan=0.0)

    # Entrenar Isolation Forest
    model = IsolationForest(contamination=contamination, random_state=42)
    preds = model.fit_predict(features)  # Inliers = 1, Outliers = -1
    
    # Convertir a bandera booleana: True para anomalías, False para inliers
    is_anomaly = preds == -1
    
    # Inyectar la columna en Polars
    return df.with_columns(
        pl.Series("is_anomaly", is_anomaly)
    )


def ejecutar_compuerta_calidad(df_crudo: pl.DataFrame, catalogo_seguidores: Dict[str, int] = None, fuente_nombre: str = "Unknown") -> pl.DataFrame:
    """Aplica controles de calidad, normalización y detección de anomalías.

    Args:
        df_crudo: DataFrame de entrada con datos crudos de Apify.
        catalogo_seguidores: Catálogo de mapeo de seguidores por canal/página.
        fuente_nombre: Nombre de la fuente para logs y fallback de id_activo.

    Returns:
        DataFrame procesado y validado listo para la capa Silver.
    """
    if catalogo_seguidores is None:
        catalogo_seguidores = {}

    logger.info("Iniciando Compuerta de Calidad con Polars + Sklearn.")

    # 1. Mapeo y Normalización de esquemas crudos
    df_normalizado = mapear_esquema_crudo(df_crudo, catalogo_seguidores, fuente_nombre)

    # 2. Filtrado inicial de registros vacíos
    df_validado = df_normalizado.filter(pl.col("texto_publicacion") != "")

    # 3. Detección de Anomalías de Likes/Interacción con Isolation Forest
    df_procesado = detectar_anomalias_engagement(df_validado)

    total = df_procesado.height
    logger.info(f"Procesamiento completado. Registros válidos: {total}")

    if total < MVD_MINIMO:
        logger.warning(
            f"[DATOS_INSUFICIENTES] Solo {total} registros válidos procesados. "
            f"Mínimo requerido (MVD): {MVD_MINIMO}. No se recomienda inferencia NLP masiva."
        )

    return df_procesado


def validar_esquema_silver(df: pl.DataFrame) -> bool:
    """Verifica que el DataFrame cumple el esquema silver antes de persistir.

    Args:
        df: DataFrame a validar.

    Returns:
        True si el esquema es correcto, False si hay campos faltantes.
    """
    campos_requeridos = [
        "id_activo",
        "plataforma",
        "texto_publicacion",
        "reacciones_totales",
        "seguidores_cuenta_origen",
        "tasa_interaccion",
        "is_valid",
        "is_anomaly",
        "_fuente",
        "_fecha_ingesta",
    ]
    faltantes = [c for c in campos_requeridos if c not in df.columns]
    if faltantes:
        logger.error(f"Campos faltantes en schema silver: {faltantes}")
        return False
    logger.info("Esquema silver validado correctamente.")
    return True
