# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");

"""Pattern 1: The Hybrid Graph (Structured AI/Deterministic Workflow)

Este módulo implementa un flujo híbrido determinista/IA para el procesamiento 
y análisis de comentarios electorales, asegurando el cumplimiento normativo 
e indexando la diversidad de las narrativas.
"""

import os
import re
import math
import logging
import json
from pathlib import Path
from typing import Dict, Any

# Configurar logging estructurado básico
logger = logging.getLogger("godel.orchestration.workflow")
logging.basicConfig(level=logging.INFO)

# Patrones para screening de CURP e INE (México)
CURP_PATTERN = re.compile(r'\b[A-Z]{4}\d{6}[HM][A-Z]{5}\d{2}\b')
INE_PATTERN = re.compile(r'\b[A-Z]{6}\d{8}\b')

def node_deterministic_compliance(data_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Nodo 1 (Determinista): Screening de cumplimiento del votante y privacidad (CURP/INE).
    
    Verifica que la información del elector/comentario no filtre PII crítica sin anonimizar,
    y valida la estructura mínima de los campos del votante si están presentes.
    """
    logger.info("[Node 1: Compliance] Iniciando verificación de cumplimiento electoral y privacidad.")
    text = data_payload.get("text", "")
    curp = data_payload.get("curp", "")
    ine = data_payload.get("ine", "")
    
    issues = []
    
    # Validar CURP si está presente o si se detecta en el texto
    if curp:
        if not CURP_PATTERN.match(curp):
            issues.append(f"CURP provisto '{curp}' tiene un formato inválido.")
    elif CURP_PATTERN.search(text):
        issues.append("Se detectó un CURP sin anonimizar en el cuerpo del texto del comentario.")
        
    # Validar INE si está presente o si se detecta en el texto
    if ine:
        if not INE_PATTERN.match(ine):
            issues.append(f"Clave de elector INE provista '{ine}' tiene un formato inválido.")
    elif INE_PATTERN.search(text):
        issues.append("Se detectó una clave de elector INE sin anonimizar en el cuerpo del texto.")
        
    # Validar campos requeridos mínimos
    if not text or len(text.strip()) < 3:
        issues.append("El texto del comentario electoral es demasiado corto o está vacío.")
        
    compliance_passed = len(issues) == 0
    
    return {
        "compliance_passed": compliance_passed,
        "compliance_issues": issues,
        "screened_text": text,
        "voter_status": "Válido y Seguro" if compliance_passed else "No Apto / Riesgo de Privacidad"
    }

def node_ai_sentiment_quality(data_payload: Dict[str, Any], compliance_result: Dict[str, Any]) -> Dict[str, Any]:
    """Nodo 2 (AI-driven): Evaluación de sentimiento y calidad de legibilidad.
    
    Realiza una evaluación estructurada de sentimiento, tono, sofisticación del lenguaje
    y nivel de toxicidad o desinformación percibida en el comentario electoral.
    """
    logger.info("[Node 2: Sentiment/Quality] Iniciando evaluación estructurada del texto.")
    text = compliance_result.get("screened_text", "")
    
    if not compliance_result.get("compliance_passed", False):
        logger.warning("[Node 2] Saltando análisis de sentimiento completo debido a fallas de cumplimiento previo.")
        return {
            "sentiment": "NEUTRAL",
            "quality_score": 0.0,
            "readability_score": 0.0,
            "tone": "INCOMPLIANT",
            "analysis_skipped": True
        }
        
    # Análisis simulado del comportamiento lingüístico del comentario (AI-driven logic/Heuristics)
    text_lower = text.lower()
    
    # Determinar Sentimiento
    positive_words = ["apoyo", "voto", "ganar", "excelente", "propuesta", "mejor", "tepic", "nayarit", "bien"]
    negative_words = ["fraude", "malo", "corrupción", "peor", "mentira", "robo", "rechazo", "falso", "odio"]
    
    pos_count = sum(1 for w in positive_words if w in text_lower)
    neg_count = sum(1 for w in negative_words if w in text_lower)
    
    if pos_count > neg_count:
        sentiment = "POSITIVO"
        tone = "Esperanzador / Proactivo"
    elif neg_count > pos_count:
        sentiment = "NEGATIVO"
        tone = "Crítico / Antagónico"
    else:
        sentiment = "NEUTRAL"
        tone = "Informativo / Cauteloso"
        
    # Calcular métrica de legibilidad y sofisticación del texto
    word_count = len(text.split())
    char_count = len(text)
    avg_word_len = char_count / max(1, word_count)
    
    # Una buena legibilidad electoral se asocia a palabras de longitud media y oraciones coherentes
    readability_score = min(1.0, max(0.1, avg_word_len / 7.0))
    quality_score = min(1.0, max(0.2, word_count / 15.0))
    
    return {
        "sentiment": sentiment,
        "quality_score": round(quality_score, 2),
        "readability_score": round(readability_score, 2),
        "tone": tone,
        "analysis_skipped": False
    }

def node_deterministic_diversity(sentiment_result: Dict[str, Any]) -> Dict[str, Any]:
    """Nodo 3 (Determinista): Cálculo matemático de diversidad de información (Shannon Entropy).
    
    Calcula la entropía de diversidad basada en las puntuaciones de calidad y legibilidad 
    para evaluar la complejidad de la narrativa de opinión electoral.
    """
    logger.info("[Node 3: Diversity Math] Calculando Índice de Diversidad de Shannon.")
    
    if sentiment_result.get("analysis_skipped", False):
        return {
            "shannon_entropy": 0.0,
            "diversity_index": "Nulo",
            "complexity_level": "Bajo"
        }
        
    # Usar las puntuaciones continuas de calidad y legibilidad como distribución de probabilidad
    p1 = sentiment_result.get("quality_score", 0.5)
    p2 = sentiment_result.get("readability_score", 0.5)
    
    # Normalizar para obtener una distribución de probabilidad válida [p1, p2]
    total_p = p1 + p2
    if total_p == 0:
        p1, p2 = 0.5, 0.5
        total_p = 1.0
        
    p1_norm = p1 / total_p
    p2_norm = p2 / total_p
    
    # Calcular Entropía de Shannon H = -sum(p_i * log2(p_i))
    h = 0.0
    for p in [p1_norm, p2_norm]:
        if p > 0:
            h -= p * math.log2(p)
            
    complexity_level = "Alta" if h > 0.8 else "Media" if h > 0.5 else "Baja"
    
    return {
        "shannon_entropy": round(h, 4),
        "diversity_index": f"Shannon H={round(h, 4)}",
        "complexity_level": complexity_level
    }

def node_ai_recommendation(
    compliance: Dict[str, Any],
    sentiment: Dict[str, Any],
    diversity: Dict[str, Any]
) -> Dict[str, Any]:
    """Nodo 4 (AI-driven): Recomendación Estratégica Electoral de Campaña.
    
    Combina los resultados normativos, el sentimiento del votante y la diversidad
    de información matemática para generar una directiva analítica accionable.
    """
    logger.info("[Node 4: AI Recommendation] Generando directiva estratégica final.")
    
    if not compliance.get("compliance_passed", False):
        return {
            "recommendation": "BLOQUEAR / RECHAZAR: El registro no cumple con las directivas de seguridad PII o electorales. No procesar tácticamente.",
            "action_priority": "INMEDIATA - SEGURIDAD",
            "tactical_focus": "Mitigación de riesgos de fuga de datos"
        }
        
    sent_type = sentiment.get("sentiment")
    complexity = diversity.get("complexity_level")
    
    recommendation = ""
    action_priority = "Media"
    tactical_focus = "General"
    
    if sent_type == "POSITIVO":
        tactical_focus = "Amplificación y Fidelización"
        if complexity == "Alta":
            recommendation = "Fidelizar y promover como embajador de opinión compleja. Utilizar sus argumentos detallados para alimentar propuestas formales de campaña en Tepic."
            action_priority = "Alta"
        else:
            recommendation = "Responder con agradecimiento y amplificar el mensaje en redes. Es un comentario de apoyo simple pero valioso."
            action_priority = "Baja"
    elif sent_type == "NEGATIVO":
        tactical_focus = "Contención y Desactivación de Crisis"
        if complexity == "Alta":
            recommendation = "Atender con máxima prioridad. Crítica estructurada y compleja que puede desestabilizar la percepción pública. Preparar tarjeta informativa de aclaración."
            action_priority = "Alta"
        else:
            recommendation = "Monitorear volumen de críticas similares. Si se mantiene bajo, evitar confrontación directa para no generar tracción adicional."
            action_priority = "Baja"
    else:
        tactical_focus = "Clarificación Informativa"
        recommendation = "Proveer información neutral y clara sobre las plataformas políticas de Tepic para orientar al ciudadano indeciso."
        action_priority = "Media"
        
    return {
        "recommendation": recommendation,
        "action_priority": action_priority,
        "tactical_focus": tactical_focus
    }

def tool_execute_electoral_workflow(data_payload: dict) -> str:
    """
    Ejecuta el flujo electoral híbrido (Hybrid Graph) combinando pasos deterministas e IA.
    
    Args:
        data_payload: Diccionario con la información del comentario electoral a procesar.
                      Campos esperados: 'text', 'curp' (opcional), 'ine' (opcional).
    Returns:
        JSON con el reporte completo detallando la ejecución nodo por nodo y su veredicto.
    """
    try:
        # Node 1: Deterministic Compliance Check (CURP/INE Screening)
        compliance_res = node_deterministic_compliance(data_payload)
        
        # Node 2: AI-driven Sentiment & Readability Quality Assessment
        sentiment_res = node_ai_sentiment_quality(data_payload, compliance_res)
        
        # Node 3: Deterministic Diversity Math (Shannon Entropy Index)
        diversity_res = node_deterministic_diversity(sentiment_res)
        
        # Node 4: AI-driven Strategic Campaign Recommendation
        recommendation_res = node_ai_recommendation(compliance_res, sentiment_res, diversity_res)
        
        # Consolidar reporte de ejecución del Hybrid Graph
        report = {
            "status": "SUCCESS" if compliance_res["compliance_passed"] else "COMPLIANCE_FAILED",
            "nodes_executed": [
                "node_deterministic_compliance",
                "node_ai_sentiment_quality",
                "node_deterministic_diversity",
                "node_ai_recommendation"
            ],
            "node_outputs": {
                "compliance": compliance_res,
                "sentiment_quality": sentiment_res,
                "diversity_math": diversity_res,
                "strategic_recommendation": recommendation_res
            }
        }
        
        return json.dumps(report, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Falla catastrófica al ejecutar el Hybrid Graph electoral: {e}")
        return json.dumps({
            "status": "ERROR",
            "error_message": f"Falla en el flujo del grafo: {str(e)}"
        }, ensure_ascii=False)
