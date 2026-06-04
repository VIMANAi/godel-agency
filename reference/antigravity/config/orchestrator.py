# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");

"""Pattern 2: The Coordinator-Specialist (Task-Scoped Subagents)

Este módulo implementa el patrón de Coordinador-Especialista en ADK 2.0.
Un coordinador central enruta consultas y delega tareas a subagentes especialistas 
con privilegios y herramientas estrictamente acotados, implementando entrega
de contexto estructurada y auditoría de límites.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger("godel.orchestration.orchestrator")
logging.basicConfig(level=logging.INFO)

# Resolución de rutas portables y compatible con herencia en cascada
import sys
BASE_DIR = Path(os.getenv("AGENCY_BASE_PATH", os.getenv("SAIEL_BASE_PATH", "")))
if not BASE_DIR.parts:
    if sys.argv and sys.argv[0]:
        try:
            entry_path = Path(sys.argv[0]).resolve()
            for parent in [entry_path.parent] + list(entry_path.parents):
                if (parent / "src").exists() or (parent / "requirements.txt").exists():
                    BASE_DIR = parent
                    break
        except Exception:
            pass
if not BASE_DIR.parts:
    for parent in [Path(os.getcwd())] + list(Path(os.getcwd()).parents):
        if (parent / "src").exists() or (parent / "requirements.txt").exists():
            BASE_DIR = parent
            break
    else:
        BASE_DIR = Path(__file__).resolve().parents[2]
LOCAL_MANIFEST_FILE = BASE_DIR / "src/agents/agent_manifest.json"
GLOBAL_MANIFEST_FILE = Path("/home/fratfn/Desarrollo/agent_manifest.json")

def load_specialist_registry() -> dict:
    """Carga de forma dinámica y agnóstica el registro de especialistas mediante Deep Merge (Local + Global)."""
    try:
        from config.registry import load_merged_manifest
        merged = load_merged_manifest()
        specialists = merged.get("specialists", {})
        if specialists:
            logger.info(f"[Registry] Registro de especialistas cargado dinámicamente mediante Deep Merge.")
            return specialists
    except Exception as e:
        logger.warning(f"Error realizando Deep Merge de especialistas: {e}")
            
    # Fallback estático embebido del Core
    logger.info("[Registry] Usando fallback estático embebido en el Core Engine.")
    return {
        "social_scraper": {
            "description": "Especialista en recolección de redes sociales y CRM.",
            "allowed_tools": ["tool_collect_data", "tool_list_data_files"],
            "denied_tools": ["tool_run_sensemaker", "tool_read_report", "tool_check_crisis", "tool_query_memory", "tool_commit_to_memory"]
        },
        "narrative_analyst": {
            "description": "Especialista en clustering DBSCAN y descubrimiento de narrativas.",
            "allowed_tools": ["tool_run_sensemaker", "tool_read_report", "tool_run_sentiment"],
            "denied_tools": ["tool_collect_data", "tool_commit_to_memory", "tool_request_executive_approval"]
        },
        "compliance_officer": {
            "description": "Especialista en verificaciones legales, regulatorias y manejo de crisis.",
            "allowed_tools": ["tool_check_crisis", "tool_request_executive_approval", "tool_query_memory"],
            "denied_tools": ["tool_collect_data", "tool_run_sentiment", "tool_commit_to_memory"]
        }
    }

# Carga inicial del registro
SPECIALIST_REGISTRY = load_specialist_registry()

class CoordinatorOrchestrator:
    """Coordinador central que gestiona el ruteo de tareas, handover de contexto y validación de límites."""
    
    def __init__(self):
        self.context_store = {
            "session_id": "session_coord_2026",
            "handover_history": [],
            "specialist_states": {
                "social_scraper": {"status": "IDLE", "data": {}},
                "narrative_analyst": {"status": "IDLE", "data": {}},
                "compliance_officer": {"status": "IDLE", "data": {}}
            }
        }

    def route_query(self, domain: str, query: str) -> str:
        """Determina cuál subagente especialista es el idóneo para resolver la consulta."""
        domain_lower = domain.lower()
        query_lower = query.lower()
        
        # Lógica heurística de ruteo
        if "social" in domain_lower or "recolect" in query_lower or "scraper" in domain_lower:
            return "social_scraper"
        elif "narrativ" in domain_lower or "analiz" in query_lower or "cluster" in query_lower:
            return "narrative_analyst"
        elif "complian" in domain_lower or "crisis" in query_lower or "legal" in query_lower or "aprob" in query_lower:
            return "compliance_officer"
        else:
            # Ruteo por defecto basado en palabras clave generales
            if "datos" in query_lower:
                return "social_scraper"
            elif "sentimiento" in query_lower:
                return "narrative_analyst"
            return "compliance_officer"

    def validate_tool_access(self, specialist: str, tool_name: str) -> tuple[bool, str]:
        """Aplica la regla de menor privilegio en las boundaries de los especialistas.
        
        Asegura que un especialista no pueda ejecutar herramientas que estén fuera de su alcance.
        """
        # Recargar para reflejar cambios dinámicos
        registry = load_specialist_registry()
        
        if specialist not in registry:
            return False, f"Especialista '{specialist}' desconocido."
            
        spec_config = registry[specialist]
        
        if tool_name in spec_config["allowed_tools"]:
            return True, f"AUTORIZADO: El especialista '{specialist}' tiene acceso legítimo a '{tool_name}'."
            
        if tool_name in spec_config.get("denied_tools", []) or tool_name not in spec_config["allowed_tools"]:
            return False, f"RECHAZADO: Violación de límite en especialista. '{specialist}' intentó invocar '{tool_name}' (Herramienta fuera de alcance)."
            
        return False, f"Herramienta '{tool_name}' no mapeada para el especialista '{specialist}'."

    def execute_handover(self, from_agent: str, to_agent: str, context_payload: Dict[str, Any]):
        """Realiza una entrega de contexto estructurada (handover) entre subagentes."""
        transfer_record = {
            "from": from_agent,
            "to": to_agent,
            "payload_keys": list(context_payload.keys()),
            "timestamp": os.getenv("CURRENT_TIME", "2026-06-01T07:12:33")
        }
        self.context_store["handover_history"].append(transfer_record)
        self.context_store["specialist_states"][to_agent]["data"].update(context_payload)
        logger.info(f"[Context Handover] Transferencia exitosa de '{from_agent}' a '{to_agent}'. Keys: {list(context_payload.keys())}")

    def coordinate_task(self, domain: str, query: str) -> Dict[str, Any]:
        """Coordina la tarea completa, ruteando, validando y ejecutando la simulación del subagente."""
        registry = load_specialist_registry()
        specialist = self.route_query(domain, query)
        spec_config = registry[specialist]
        
        # Simular qué herramienta intentaría usar el especialista
        suggested_tool = ""
        if specialist == "social_scraper":
            suggested_tool = "tool_collect_data"
        elif specialist == "narrative_analyst":
            suggested_tool = "tool_run_sensemaker"
        elif specialist == "compliance_officer":
            suggested_tool = "tool_check_crisis"
            
        # Validar acceso a la herramienta
        allowed, auth_msg = self.validate_tool_access(specialist, suggested_tool)
        
        # Registrar estado de ejecución
        self.context_store["specialist_states"][specialist]["status"] = "ACTIVE"
        
        # Realizar handover inicial del coordinador al especialista
        self.execute_handover("coordinator", specialist, {"query": query, "domain": domain})
        
        response_payload = {
            "routed_specialist": specialist,
            "specialist_description": spec_config["description"],
            "suggested_tool": suggested_tool,
            "tool_authorization": {
                "allowed": allowed,
                "message": auth_msg
            },
            "context_handover_history": self.context_store["handover_history"],
            "specialist_state": self.context_store["specialist_states"][specialist]
        }
        
        # Si fue compliance officer y requiere escalación o verificación, simular handover adicional
        if specialist == "compliance_officer" and allowed:
            # Handover secundario: entregar a analyst para validación profunda
            self.execute_handover("compliance_officer", "narrative_analyst", {"crisis_detected": True, "escalation_required": True})
            response_payload["handover_triggered"] = "compliance_officer -> narrative_analyst"
            
        self.context_store["specialist_states"][specialist]["status"] = "COMPLETED"
        return response_payload

# Instancia global del Coordinador
coordinator_orchestrator = CoordinatorOrchestrator()

def tool_coordinate_specialists(domain: str, query: str) -> str:
    """Delega y coordina consultas utilizando el patrón Coordinador-Especialista de ADK 2.0.
    
    Args:
        domain: Dominio del problema (ej. 'social_media', 'narratives', 'legal_compliance').
        query: Consulta específica a resolver por la flota de especialistas.
    Returns:
        JSON con el reporte completo de la delegación, ruteo y verificación de políticas.
    """
    try:
        result = coordinator_orchestrator.coordinate_task(domain, query)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error al coordinar especialistas: {e}")
        return json.dumps({
            "status": "ERROR",
            "error_message": f"Falla en la orquestación: {str(e)}"
        }, ensure_ascii=False)
