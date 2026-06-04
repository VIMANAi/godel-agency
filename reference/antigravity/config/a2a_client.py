# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");

"""Pattern 2: Delegated Specialization (A2A Client Mesh)

Permite al coordinador delegar consultas analíticas fuera de su dominio a agentes
especialistas remotos que hablen A2A (Ej. scoring demográfico o análisis de riesgo).
"""

import os
import json
import asyncio
from pathlib import Path

# Catálogo local mock de tarjetas de agentes especialistas externos (A2A Mesh)
SPECIALIST_REGISTRY = {
    "java_risk_assessor": {
        "a2a_version": "1.0",
        "agent_card_id": "java_risk_assessor_card",
        "meta": {
            "name": "Java Financial Risk Specialist",
            "developer": "RISK_TEAM_ORLANDO",
            "description": "Calculates electoral and budget risk weights cross-referenced with local audits."
        },
        "capabilities": ["budget_risk", "voter_churn_risk"]
    },
    "go_demographic_scorer": {
        "a2a_version": "1.0",
        "agent_card_id": "go_demographic_scorer_card",
        "meta": {
            "name": "Go Demographic Scorer Specialist",
            "developer": "DEMO_CRAWLERS_GO",
            "description": "Analyzes census patterns and candidate traction indices at neighborhood/seccional granularity."
        },
        "capabilities": ["census_segmentation", "traction_index"]
    }
}

async def tool_delegate_to_a2a_specialist(specialist_name: str, query: str) -> str:
    """
    Delega de forma segura una tarea analítica compleja a un agente especialista remoto
    A2A (Microservicio de Agente). Todas las llamadas son evaluadas previamente por el
    Agent Gateway (Capa 3 de gobernación) para proteger los datos antes de cruzar fronteras.
    
    Args:
        specialist_name: El identificador del especialista ("java_risk_assessor" o "go_demographic_scorer").
        query: Consulta analítica o datos que se desean delegar.
    Returns:
        Respuesta analítica estructurada del especialista o bloqueo del Gateway.
    """
    clean_name = specialist_name.strip()
    
    # 1. Capa 3 Gateway: Validar seguridad de federación saliente (Pattern 4)
    from config.gateway import agent_gateway
    gateway_ok, gateway_msg = agent_gateway.enforce_federation_safety(clean_name, query)
    if not gateway_ok:
        return f"BLOQUEADO POR GATEWAY: Transacción A2A detenida por política de federación saliente. Razón: {gateway_msg}"
        
    # Verificar si el especialista existe en el Mesh
    if clean_name not in SPECIALIST_REGISTRY:
        return f"ERROR: El especialista A2A '{clean_name}' no se encuentra registrado en el Agent Registry mesh."
        
    card = SPECIALIST_REGISTRY[clean_name]
    print(f"\n📡 [A2A Client] Descubierta tarjeta del especialista '{clean_name}': ID Card: {card['agent_card_id']}")
    print(f"📡 [A2A Client] Serializando carga y enviando delegación a: {card['meta']['name']}...")
    
    # Simular latencia de red (sub-segundo cold start)
    await asyncio.sleep(0.3)
    
    # Respuestas estructuradas mock
    if clean_name == "java_risk_assessor":
        response = {
            "status": "COMPLETED",
            "provider": "Java Financial Risk Specialist",
            "risk_index": 0.28,
            "interpretation": "Riesgo presupuestal electoral BAJO en Nayarit. Cobertura financiera estable.",
            "audited_records": 1240
        }
    else: # go_demographic_scorer
        response = {
            "status": "COMPLETED",
            "provider": "Go Demographic Scorer Specialist",
            "census_traction": {
                "young_votes_percentage": 68.2,
                "traction_trend": "CRECIENTE",
                "seccionales_alertas": ["Tepic Seccional 12", "Tepic Seccional 14"]
            },
            "confidence_score": 0.94
        }
        
    print(f"📡 [A2A Client] Respuesta estructurada recibida de '{clean_name}' con éxito.\n")
    return f"ÉXITO: Respuesta del especialista A2A '{clean_name}':\n" + json.dumps(response, indent=2, ensure_ascii=False)
