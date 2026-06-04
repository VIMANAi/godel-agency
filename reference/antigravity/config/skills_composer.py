# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");

"""Pattern 3: Skill Composition (Declarative Toolset Chaining)

Este módulo implementa el patrón de Composición de Habilidades de ADK 2.0.
Carga habilidades acotadas de forma declarativa e implementa encadenamiento dinámico 
de herramientas bajo el principio de revelación progresiva (progressive disclosure),
donde los inputs y permisos de los pasos siguientes se revelan solo si los pasos previos
se completan exitosamente.
"""

import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger("godel.orchestration.skills_composer")
logging.basicConfig(level=logging.INFO)

# Declaración declarativa de Habilidades (Skills) y sus contratos de entrada/salida
SKILLS_DECLARATION = {
    "data-extractor": {
        "name": "Social Data Extractor Skill",
        "version": "1.0",
        "description": "Extrae campos clave, elimina ruido analítico y normaliza comentarios.",
        "required_inputs": ["raw_text"],
        "outputs": ["clean_text", "word_count"],
        "security_level": "Bajo"
    },
    "trend-analyzer": {
        "name": "Electoral Trend Analyzer Skill",
        "version": "1.2",
        "description": "Evalúa frecuencias, identifica tópicos emergentes y calcula desviación estándar.",
        "required_inputs": ["clean_text"],
        "outputs": ["primary_topic", "trend_signals"],
        "security_level": "Medio" # Se revela y habilita de forma progresiva
    },
    "executive-summary": {
        "name": "Executive Strategy Summary Skill",
        "version": "2.0",
        "description": "Sintetiza tendencias en una directiva ejecutiva compacta y legible.",
        "required_inputs": ["primary_topic", "trend_signals"],
        "outputs": ["executive_directive", "summary_bullet_points"],
        "security_level": "Alto" # Máxima revelación progresiva
    }
}

class SkillsComposer:
    """Motor de orquestación y composición de habilidades declarativas."""
    
    def __init__(self):
        self.active_skills = {}
        self.execution_ledger = []

    def load_declarative_skill(self, skill_id: str) -> Dict[str, Any]:
        """Carga dinámicamente la especificación de una habilidad."""
        if skill_id not in SKILLS_DECLARATION:
            raise ValueError(f"Habilidad declarativa '{skill_id}' no registrada en la biblioteca corporativa.")
        return SKILLS_DECLARATION[skill_id]

    def execute_composed_chain(self, raw_input_text: str) -> Dict[str, Any]:
        """Ejecuta una cadena compuesta de habilidades utilizando revelación progresiva.
        
        Cada paso valida estrictamente sus inputs y habilita el acceso a la siguiente habilidad 
        solo si se satisface el contrato de salida del paso anterior.
        """
        logger.info("[Skills Composer] Iniciando composición dinámica de la cadena analítica.")
        
        context_state = {"raw_text": raw_input_text}
        
        # --- PASO 1: data-extractor (Bajo) ---
        skill_1 = self.load_declarative_skill("data-extractor")
        self.execution_ledger.append({"skill": "data-extractor", "status": "LOADED", "access_granted": True})
        
        # Simulación de ejecución del extractor
        clean_text = raw_input_text.strip().replace("  ", " ")
        words = clean_text.split()
        context_state["clean_text"] = clean_text
        context_state["word_count"] = len(words)
        
        self.execution_ledger.append({
            "skill": "data-extractor",
            "status": "COMPLETED",
            "provided_outputs": ["clean_text", "word_count"]
        })
        
        # --- PASO 2: trend-analyzer (Medio - Revelado Progresivamente) ---
        # Solo se permite cargar y ejecutar trend-analyzer si clean_text está en el contexto
        if "clean_text" in context_state:
            skill_2 = self.load_declarative_skill("trend-analyzer")
            self.execution_ledger.append({"skill": "trend-analyzer", "status": "LOADED", "access_granted": True})
            
            # Evaluar tópicos emergentes (simulado con lógica de coincidencia de palabras)
            clean_lower = context_state["clean_text"].lower()
            if "agua" in clean_lower or "servicios" in clean_lower:
                topic = "Demanda de Servicios Públicos y Agua Potable"
            elif "tepic" in clean_lower or "nayarit" in clean_lower:
                topic = "Estructura Electoral Local (Tepic/Nayarit)"
            else:
                topic = "Opinión General y Debate Político"
                
            context_state["primary_topic"] = topic
            context_state["trend_signals"] = ["Volumen Estable", "Engagement Moderado"]
            
            self.execution_ledger.append({
                "skill": "trend-analyzer",
                "status": "COMPLETED",
                "provided_outputs": ["primary_topic", "trend_signals"]
            })
        else:
            self.execution_ledger.append({"skill": "trend-analyzer", "status": "BLOCKED", "reason": "Falta input requerido 'clean_text'"})
            return {"status": "FAILED", "ledger": self.execution_ledger}

        # --- PASO 3: executive-summary (Alto - Revelado Progresivamente) ---
        # Solo se expone si primary_topic y trend_signals fueron calculados exitosamente
        if "primary_topic" in context_state and "trend_signals" in context_state:
            skill_3 = self.load_declarative_skill("executive-summary")
            self.execution_ledger.append({"skill": "executive-summary", "status": "LOADED", "access_granted": True})
            
            # Generar síntesis ejecutiva estructurada
            topic = context_state["primary_topic"]
            signals = ", ".join(context_state["trend_signals"])
            
            directive = f"DIRECTIVA: Concentrar esfuerzos de comunicación en la temática '{topic}' con base en señales de '{signals}'."
            bullets = [
                f"Tópico Dominante Identificado: {topic}",
                f"Número total de palabras analizadas: {context_state['word_count']}",
                f"Métrica de Tendencia: {signals}"
            ]
            
            context_state["executive_directive"] = directive
            context_state["summary_bullet_points"] = bullets
            
            self.execution_ledger.append({
                "skill": "executive-summary",
                "status": "COMPLETED",
                "provided_outputs": ["executive_directive", "summary_bullet_points"]
            })
        else:
            self.execution_ledger.append({"skill": "executive-summary", "status": "BLOCKED", "reason": "Contrato de trend-analyzer insatisfecho."})
            return {"status": "FAILED", "ledger": self.execution_ledger}
            
        return {
            "status": "SUCCESS",
            "final_outputs": {
                "directive": context_state["executive_directive"],
                "bullet_points": context_state["summary_bullet_points"],
                "clean_text_sample": context_state["clean_text"][:60]
            },
            "chain_ledger": self.execution_ledger
        }

def tool_execute_composed_skills(task: str) -> str:
    """Ejecuta una composición declarativa de habilidades en base a una tarea electoral.
    
    Args:
        task: Texto del comentario o descripción de la tarea a procesar por la cadena.
    Returns:
        JSON con la traza de ejecución de las habilidades y los reportes sintéticos finales.
    """
    try:
        composer = SkillsComposer()
        result = composer.execute_composed_chain(task)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error al ejecutar composición de habilidades: {e}")
        return json.dumps({
            "status": "ERROR",
            "error_message": f"Falla en la composición de habilidades: {str(e)}"
        }, ensure_ascii=False)
