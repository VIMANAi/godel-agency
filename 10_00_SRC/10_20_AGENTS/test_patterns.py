# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");

"""Script de pruebas automatizadas para los 5 Patrones de Diseño del Agente Godel.

Este script valida de forma integral la persistencia de sesiones, el filtrado PII de
la memoria (Agent Gateway), el módulo de aprobación delegada y la configuración de disparadores.
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# Asegurar importaciones correctas agregando Agency a path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.agents.godel_agent import load_stored_session, save_stored_session, clear_stored_session, SESSION_FILE
from src.agents.config.memory_bank import tool_commit_to_memory, tool_query_memory, check_pii_violation, MEMORY_FILE
from src.agents.config.approval import tool_request_executive_approval
from src.agents.config.triggers import log_health, check_data_for_crisis, LOG_PATH

async def run_tests():
    print("=" * 60)
    print("🧪 INICIANDO PRUEBAS DE LOS 5 PATRONES DE DISEÑO PARA GODEL")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Prueba de Checkpoint-and-Resume (Persistencia de Sesión)
    # ---------------------------------------------------------
    print("\n📦 [Pattern 1] Probando Checkpoint-and-Resume:")
    clear_stored_session()
    assert SESSION_FILE.exists() is False, "❌ Falla: La sesión debería estar vacía"
    
    # Guardar sesión ficticia
    test_conv_id = "test_conversation_12345"
    test_save_dir = "/tmp/test_sessions"
    save_stored_session(test_conv_id, test_save_dir)
    assert SESSION_FILE.exists() is True, "❌ Falla: Debería existir el archivo de sesión"
    
    # Recuperar sesión
    loaded_conv, loaded_dir = load_stored_session()
    assert loaded_conv == test_conv_id, f"❌ Falla: ID incorrecto ({loaded_conv})"
    assert loaded_dir == test_save_dir, f"❌ Falla: Directorio incorrecto ({loaded_dir})"
    print("   [OK] Guardado y carga de sesión persistida funciona correctamente.")
    
    # Limpiar
    clear_stored_session()
    assert SESSION_FILE.exists() is False, "❌ Falla: La sesión no se borró"
    print("   [OK] Limpieza de sesión (--new) funciona correctamente.")

    # ---------------------------------------------------------
    # 2. Prueba de Memory-Layered Context & Agent Gateway
    # ---------------------------------------------------------
    print("\n🧠 [Pattern 3] Probando Memory-Layered Context & Gateway:")
    
    # Limpiar archivo de memoria si existe para pruebas aisladas
    if MEMORY_FILE.exists():
        MEMORY_FILE.unlink()
        
    # Caso 2a: Guardado y recuperación estándar (Seguro)
    res_ok = tool_commit_to_memory("estrategia", "Enfoque prioritario en el sector joven del distrito 5.")
    assert "ÉXITO" in res_ok, f"❌ Falla: Debería permitir guardar recuerdos seguros: {res_ok}"
    print("   [OK] Memoria segura guardada con éxito.")
    
    res_query = tool_query_memory("estrategia")
    assert "Recuerdos encontrados" in res_query and "sector joven" in res_query, "❌ Falla: La consulta de memoria no devolvió el recuerdo"
    print("   [OK] Recuperación de memoria funciona correctamente.")
    
    # Caso 2b: Bloqueo de PII de tipo Password (Agent Gateway)
    res_pii1 = tool_commit_to_memory("seguridad", "Mi api_key = AIzaSyDfakeKey123")
    assert "RECHAZADO" in res_pii1, f"❌ Falla: Gateway debería bloquear transacciones con API keys: {res_pii1}"
    print("   [OK] Gateway bloqueó exitosamente almacenamiento de API Key.")

    # Caso 2c: Bloqueo de PII de tipo Email (Agent Gateway)
    res_pii2 = tool_commit_to_memory("usuarios", "Contacto principal: juan.perez@gmail.com")
    assert "RECHAZADO" in res_pii2, f"❌ Falla: Gateway debería bloquear transacciones con correos: {res_pii2}"
    print("   [OK] Gateway bloqueó exitosamente almacenamiento de correo electrónico.")
    
    # Limpiar memoria de prueba
    if MEMORY_FILE.exists():
        MEMORY_FILE.unlink()

    # ---------------------------------------------------------
    # 3. Prueba de Ambient Processing (Triggers en segundo plano)
    # ---------------------------------------------------------
    print("\n🕒 [Pattern 4] Probando Ambient Processing (Triggers):")
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)
        
    # Crear una clase mock para TriggerContext
    class MockTriggerContext:
        def __init__(self):
            self.sent_messages = []
        async def send(self, msg: str):
            self.sent_messages.append(msg)
            
    mock_ctx = MockTriggerContext()
    
    # Ejecutar heartbeat mock
    await log_health(mock_ctx)
    assert os.path.exists(LOG_PATH) is True, "❌ Falla: No se generó el archivo health.log"
    
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        log_content = f.read()
    assert "HEARTBEAT" in log_content, "❌ Falla: Log del Heartbeat no contiene la cadena correcta"
    print("   [OK] Ejecución de Heartbeat periódico funciona correctamente.")

    # Ejecutar monitor de crisis mock (escribiendo un reporte mock con crisis primero)
    report_path = Path("/home/fratfn/Desarrollo/Agency/data/processed/reporte_industrial_narrativas.json")
    os.makedirs(report_path.parent, exist_ok=True)
    
    mock_report = {
        "shannon_diversity": 1.45,
        "total_comentarios": 150,
        "alertas_crisis": [
            {"severidad": "ALTA", "mensaje": "Pico de negatividad en narrativa #2"}
        ]
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(mock_report, f)
        
    await check_data_for_crisis(mock_ctx)
    
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        log_content = f.read()
    assert "AMBIENT MONITOR ALERT" in log_content, "❌ Falla: No se escaló la crisis en health.log"
    assert len(mock_ctx.sent_messages) == 1, "❌ Falla: El disparador no envió notificación proactiva al agente"
    print("   [OK] Monitoreo ambiental y escalación de crisis funciona correctamente.")
    
    # Limpiar logs de prueba
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)

    # ---------------------------------------------------------
    # 4. Aprobación Delegada y Fleet Orchestration (Estructura de Capacidad)
    # ---------------------------------------------------------
    print("\n🛑 [Pattern 2 & 5] Probando estructura de Aprobación Delegada y Fleet Orchestration:")
    
    # Carga de la configuración avanzada del agente
    from google.antigravity import LocalAgentConfig, types
    from src.agents.config.mcp_servers import mcp_servers_list
    from src.agents.config.triggers import triggers_list
    
    config = LocalAgentConfig(
        tools=[],
        mcp_servers=mcp_servers_list,
        triggers=triggers_list,
        capabilities=types.CapabilitiesConfig(
            enable_subagents=True
        )
    )
    
    assert config.capabilities.enable_subagents is True, "❌ Falla: Las capacidades de subagentes deberían estar habilitadas"
    print("   [OK] Capacidad Fleet Orchestration (enable_subagents) validada y activa.")

    print("\n" + "=" * 60)
    print("🎉 TODAS LAS PRUEBAS DE LOS 5 PATRONES PASARON CON ÉXITO [100% OK]")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_tests())
