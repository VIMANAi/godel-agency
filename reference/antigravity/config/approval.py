# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");

"""Módulo de aprobación delegada (Human-in-the-Loop) para el proyecto Agency.

Permite pausar el flujo del agente en acciones de alto impacto para requerir
la intervención y confirmación explícita de un operador humano.
"""

import sys
import asyncio

async def tool_request_executive_approval(action: str, reason: str) -> str:
    """
    Solicita aprobación ejecutiva explícita (Human-in-the-Loop) para una acción crítica.
    El agente pausará su ejecución en este punto y esperará una respuesta humana.
    
    Args:
        action: Descripción precisa de la acción que requiere aprobación.
        reason: Justificación técnica o analítica del agente para realizar la acción.
    Returns:
        Resultado de la decisión del aprobador ("Aprobado" o "Rechazado" con comentarios).
    """
    print("\n" + "🛑" * 30)
    print("📢 SOLICITUD DE APROBACIÓN EJECUTIVA (HUMAN-IN-THE-LOOP)")
    print("🛑" * 30)
    print(f"🔹 Acción Crítica : {action}")
    print(f"🔹 Razón del Agente: {reason}")
    print("-" * 60)
    print("Por favor, introduce tu decisión en la consola:")
    print("  Escribe 'y' / 'yes' para APROBAR.")
    print("  Escribe cualquier otra cosa o comentario para RECHAZAR.")
    print("-" * 60)
    
    try:
        # Usamos asyncio.to_thread para no bloquear el bucle de eventos asíncrono
        # al hacer una lectura síncrona en la consola.
        response = await asyncio.to_thread(input, "Decisión Ejecutiva > ")
        response_clean = response.strip().lower()
        
        if response_clean in ("y", "yes", "si", "sí", "aprobar"):
            print("✅ Acción Aprobada por el Ejecutivo. Continuando ejecución...\n")
            return "APROBADO: El usuario ha autorizado explícitamente realizar esta acción."
        else:
            reason_rejected = response if response.strip() else "Sin justificación adicional"
            print(f"❌ Acción Rechazada por el Ejecutivo. Motivo: {reason_rejected}\n")
            return f"RECHAZADO: El usuario ha denegado la autorización. Motivo: {reason_rejected}. Re-evalúa tu estrategia."
    except Exception as e:
        return f"ERROR al solicitar aprobación: {e}"
