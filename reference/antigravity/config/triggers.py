# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");

"""Módulo de disparadores (Triggers) autónomos del proyecto Agency.

Este módulo proporciona una plantilla inactiva por defecto de un disparador
de diagnóstico (Heartbeat) asíncrono para monitoreo de estado.
"""

import os
import json
import datetime
from google.antigravity.triggers import every, TriggerContext

# Bandera de activación: FASE INICIAL ACTIVADA
# Cambiar a True para habilitar el Heartbeat asíncrono y los monitores ambientales.
ENABLED = True

# Ruta física para escribir el log de diagnóstico
LOG_PATH = "/home/fratfn/Desarrollo/Agency/health.log"

async def log_health(ctx: TriggerContext) -> None:
    """Callback de diagnóstico que registra el estado de salud del agente.
    
    Se ejecuta asíncronamente en segundo plano.
    """
    from config.identity import agent_identity
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"{agent_identity.get_identity_string()} [{timestamp}] HEARTBEAT: El agente de Agency se encuentra activo y saludable. Estado: OK.\n"
    
    try:
        # Asegurarse de que el directorio padre existe
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a") as f:
            f.write(log_line)
    except Exception as e:
        # Falla silenciosa de diagnóstico para no interrumpir el flujo principal
        pass

async def check_data_for_crisis(ctx: TriggerContext) -> None:
    """Monitorea el reporte en busca de crisis electorales de forma ambiental (segundo plano).
    
    Si se detectan crisis, escala registrando el evento e informando al agente.
    """
    from config.identity import agent_identity
    report_path = "/home/fratfn/Desarrollo/Agency/data/processed/reporte_industrial_narrativas.json"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if os.path.exists(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                report = json.load(f)
            
            # Formato compatible con diccionario
            alertas = report.get('alertas_crisis', [])
            if alertas:
                severidades = ", ".join([a.get('severidad', 'N/A') for a in alertas])
                escalation_msg = f"{agent_identity.get_identity_string()} [{timestamp}] AMBIENT MONITOR ALERT: Crisis detectada. Alertas activas: {len(alertas)} ({severidades})\n"
                
                os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
                with open(LOG_PATH, "a") as f:
                    f.write(escalation_msg)
                
                # Enviar una notificación proactiva al contexto de la conversación
                await ctx.send(
                    f"[Monitoreo Ambiental] ¡ATENCIÓN! Se han detectado {len(alertas)} alertas de crisis "
                    f"activas en el reporte electoral con severidades: {severidades}. Se recomienda actuar de inmediato."
                )
        except Exception:
            pass

async def ambient_file_mesh_monitor(ctx: TriggerContext) -> None:
    """Monitorea data/raw/ de forma ambiental en busca de eventos de datos electorales.
    
    Si se detecta un nuevo archivo JSON, lo procesa y auto-ingesta asíncronamente en el sistema.
    """
    from config.identity import agent_identity
    from pathlib import Path
    raw_dir = Path("/home/fratfn/Desarrollo/Agency/data/raw")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if raw_dir.exists():
        event_files = list(raw_dir.glob("event_*.json"))
        for f in event_files:
            try:
                with open(f, "r", encoding="utf-8") as file_data:
                    payload = json.load(file_data)
                
                log_line = (
                    f"{agent_identity.get_identity_string()} [{timestamp}] "
                    f"EVENT MESH INGESTION: Auto-ingestado archivo de evento '{f.name}'. "
                    f"Contenido: {json.dumps(payload)}\n"
                )
                
                os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
                with open(LOG_PATH, "a") as health_file:
                    health_file.write(log_line)
                    
                # Enviar una notificación proactiva al agente
                await ctx.send(
                    f"[Ambient Event Mesh] Evento de datos auto-ingestado: '{f.name}'. "
                    f"Comentario: {payload.get('comentario', 'N/A')}."
                )
                
                # Eliminar el archivo procesado para simular consumo de cola
                f.unlink()
            except Exception:
                pass

# Lista global de triggers activos que se inyectarán en el Agente.
# Se ejecutan periódicamente de forma asíncrona en segundo plano.
triggers_list = [
    every(10, log_health),           # Heartbeat cada 10 segundos
    every(15, check_data_for_crisis), # Chequeo ambiental de crisis cada 15 segundos
    every(12, ambient_file_mesh_monitor) # Ambient Event Mesh cada 12 segundos
] if ENABLED else []
