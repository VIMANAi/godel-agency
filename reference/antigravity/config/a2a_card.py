# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");

"""Pattern 1: Agent Card Discovery

Declara y publica la credencial A2A de Godel (Agent Card) para permitir que otros
agentes de la organización o federados descubran y coordinen de forma declarativa.
"""

import os
import json
from pathlib import Path

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
MANIFEST_FILE = BASE_DIR / "src/agents/manifest.json"
CARD_OUTPUT_FILE = BASE_DIR / "80_00_OUTPUTS/80_00_REPORTS/80_00_20_AGENT_CARD.json"

def tool_publish_agent_card() -> str:
    """
    Genera y publica la especificación A2A del agente (Agent Card) para el service mesh de la organización.
    
    Returns:
        Ruta física del archivo JSON del Agent Card generado y resumen.
    """
    # 1. Cargar el manifiesto base para heredar capacidades
    capabilities = []
    if MANIFEST_FILE.exists():
        try:
            with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
                manifest = json.load(f)
                capabilities = manifest.get("capabilities", [])
        except Exception:
            pass
            
    # Si está vacío, cargar capacidades por defecto
    if not capabilities:
        capabilities = [
            "data_collection", "data_ingestion", "pdiv_calculation",
            "sensemaking", "crisis_detection"
        ]
        
    # 2. Estructurar el A2A Agent Card de acuerdo a especificaciones corporativas
    agent_card = {
        "a2a_version": "1.0",
        "agent_card_id": "saiel_political_intelligence_agent_card",
        "meta": {
            "name": "SAIEL Godel Political Intelligence Agent",
            "developer": "WAR_ROOM_DEV_TEAM",
            "version": "2.5",
            "description": "Exposes electoral sentiment analysis, strategic PDIV calculations and crisis escalations.",
            "organization": "SAIEL Electoral Intel"
        },
        "endpoints": {
            "a2a_endpoint": "https://godel-agent.tepic.nayarit.saiel.cloud/v1/a2a",
            "mcp_endpoint": "https://godel-agent.tepic.nayarit.saiel.cloud/v1/mcp"
        },
        "capabilities": capabilities,
        "auth": {
            "type": "OAuth2 / Bearer Token",
            "scopes": ["saiel:read", "saiel:analyze"],
            "restricted_domains": ["saiel.cloud", "nayarit.gob.mx"]
        },
        "rate_limits": {
            "max_requests_per_min": 100,
            "max_concurrency": 5
        }
    }
    
    # 3. Guardar el archivo físicamente
    try:
        os.makedirs(CARD_OUTPUT_FILE.parent, exist_ok=True)
        with open(CARD_OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(agent_card, f, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error al generar Agent Card: {e}"
        
    print(f"\n🏷️  [A2A] Agent Card generado y publicado en: {CARD_OUTPUT_FILE}")
    return f"ÉXITO: A2A Agent Card generado y expuesto para Service Mesh en:\n  - {CARD_OUTPUT_FILE}"
