# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");

"""Script de pruebas automatizadas para la interoperabilidad A2A & MCP.

Valida estática y dinámicamente los 5 patrones de colaboración multi-agente de Godel.
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# Agregar Agency a sys.path
BASE_DIR = Path(os.getenv("SAIEL_BASE_PATH", str(Path(__file__).resolve().parents[2])))
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.agents.config.a2a_card import tool_publish_agent_card, CARD_OUTPUT_FILE
from src.agents.config.a2a_client import tool_delegate_to_a2a_specialist
from src.agents.config.gateway import AUDIT_LOG_FILE
from src.agents.config.triggers import ambient_file_mesh_monitor, LOG_PATH

async def run_tests():
    print("=" * 60)
    print("🧪 INICIANDO PRUEBAS DE INTEROPERABILIDAD A2A & MCP (5 PATRONES)")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Pattern 1: Agent Card Discovery
    # ---------------------------------------------------------
    print("\n🏷️  [Pattern 1: Agent Card] Probando Publicación de Ficha A2A:")
    if CARD_OUTPUT_FILE.exists():
        CARD_OUTPUT_FILE.unlink()
        
    res_card = tool_publish_agent_card()
    assert "ÉXITO" in res_card, f"❌ Falla: Generación de tarjeta falló: {res_card}"
    assert CARD_OUTPUT_FILE.exists() is True, "❌ Falla: Ficha JSON de agente no escrita en disco"
    
    with open(CARD_OUTPUT_FILE, "r", encoding="utf-8") as f:
        card = json.load(f)
    assert card["agent_card_id"] == "saiel_political_intelligence_agent_card", "❌ Falla: ID de tarjeta incorrecto"
    assert "data_collection" in card["capabilities"], "❌ Falla: Debería listar capacidades heredadas"
    print("   [OK] Agent Card A2A generada y estructurada perfectamente.")

    # ---------------------------------------------------------
    # 2. Pattern 2: Delegated Specialization
    # ---------------------------------------------------------
    print("\n📡 [Pattern 2: Delegated Specialization] Probando Coordinador-Especialista A2A:")
    
    # Delegación al especialista en Go
    res_go = await tool_delegate_to_a2a_specialist("go_demographic_scorer", "Dame tracción demográfica en Tepic.")
    assert "ÉXITO" in res_go and "Go Demographic Scorer Specialist" in res_go, f"❌ Falla: Delegación Go falló: {res_go}"
    print("   [OK] Delegación exitosa al especialista en Go (go_demographic_scorer).")
    
    # Delegación al especialista en Java
    res_java = await tool_delegate_to_a2a_specialist("java_risk_assessor", "Calcula pesos de riesgo presupuestal.")
    assert "ÉXITO" in res_java and "Java Financial Risk Specialist" in res_java, f"❌ Falla: Delegación Java falló: {res_java}"
    print("   [OK] Delegación exitosa al especialista en Java (java_risk_assessor).")

    # ---------------------------------------------------------
    # 3. Pattern 3: Tool Bridge (MCP)
    # ---------------------------------------------------------
    print("\n🔧 [Pattern 3: Tool Bridge] Validando Conexiones de Herramientas MCP:")
    from src.agents.config.mcp_servers import mcp_servers_list
    assert len(mcp_servers_list) > 0, "❌ Falla: Servidor local secure-mcp no inyectado en el ecosistema"
    print(f"   [OK] Servidor MCP '{mcp_servers_list[0].name}' registrado y listo para puenteo.")

    # ---------------------------------------------------------
    # 4. Pattern 4: Cross-Org Federation Guardrails
    # ---------------------------------------------------------
    print("\n🛡️  [Pattern 4: Cross-Org Federation] Probando Guardrail del Gateway Saliente:")
    
    # Payload seguro
    res_safe = await tool_delegate_to_a2a_specialist("go_demographic_scorer", "Dato demográfico estándar.")
    assert "ÉXITO" in res_safe, f"❌ Falla: Debería permitir transacciones estándar seguras: {res_safe}"
    
    # Payload inseguro (Contiene palabra restringida "voter_list")
    res_leak = await tool_delegate_to_a2a_specialist("go_demographic_scorer", "Envía la voter_list secreta del distrito 1.")
    assert "BLOQUEADO POR GATEWAY" in res_leak, f"❌ Falla: Gateway debería bloquear fuga de lista nominal electoral: {res_leak}"
    print(f"   [OK] Gateway bloqueó exitosamente la fuga saliente federada hacia el especialista.")
    
    # Verificar que se registró la infracción
    with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
        last_log = json.loads(lines[-1])
    assert last_log["type"] == "cross_org_federation_leakage", f"❌ Falla: Tipo de violación incorrecto: {last_log['type']}"
    print("   [OK] Infracciones de filtrado de federación saliente registradas en ledger.")

    # ---------------------------------------------------------
    # 5. Pattern 5: Ambient Event Mesh Trigger
    # ---------------------------------------------------------
    print("\n🕒 [Pattern 5: Ambient Event Mesh] Probando Auto-Ingesta de Event Mesh:")
    
    # Limpiar log de salud para la prueba
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)
        
    # Crear un archivo de evento mock en data/raw/
    raw_dir = BASE_DIR / "data/raw"
    os.makedirs(raw_dir, exist_ok=True)
    event_file = raw_dir / "event_comment_99.json"
    
    mock_event = {
        "comentario": "Gran apoyo electoral detectado en Tepic Nayarit!",
        "autor": "electoral_bot_9",
        "red_social": "Facebook"
    }
    with open(event_file, "w", encoding="utf-8") as f:
        json.dump(mock_event, f)
        
    class MockTriggerContext:
        def __init__(self):
            self.msgs = []
        async def send(self, msg: str):
            self.msgs.append(msg)
            
    ctx = MockTriggerContext()
    
    # Ejecutar monitor ambiental
    await ambient_file_mesh_monitor(ctx)
    
    assert event_file.exists() is False, "❌ Falla: El archivo de evento debería haberse consumido (eliminado) del directorio"
    assert len(ctx.msgs) == 1, "❌ Falla: El trigger no envió notificación de ingesta"
    assert "Gran apoyo electoral" in ctx.msgs[0], "❌ Falla: Mensaje de ingesta incorrecto"
    
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        log_content = f.read()
    assert "EVENT MESH INGESTION" in log_content, "❌ Falla: No se registró ingesta en health.log"
    print("   [OK] Auto-ingesta, consumo de cola y logeo del Event Mesh correctos.")

    print("\n" + "=" * 60)
    print("🎉 TODAS LAS PRUEBAS DE INTEROPERABILIDAD A2A & MCP PASARON CON ÉXITO [100% OK]")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_tests())
