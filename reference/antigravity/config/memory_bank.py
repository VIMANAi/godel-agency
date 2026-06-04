# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");

"""Módulo de Memoria de Largo Plazo (Memory Bank) con Auditoría de Gateway de Seguridad (PII).

Permite al agente persistir observaciones analíticas clave sobre tópicos específicos
de forma duradera a través de ejecuciones y sesiones, protegiendo los datos mediante
un filtro activo de PII (Agent Gateway).
"""

import os
import json
import re
import datetime
from pathlib import Path

MEMORY_FILE = Path("/home/fratfn/Desarrollo/Agency/data/db/memory_bank.json")

# Expresiones regulares para detección de PII y datos altamente sensibles (Agent Gateway)
PII_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
    "phone": re.compile(r"\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}"),
    "password_or_key": re.compile(r"(password|contraseña|pwd|api_key|secret|token|passwd|clave)\s*[:=]\s*['\"]?[a-zA-Z0-9_\-\.\@\!]{5,}['\"]?", re.IGNORECASE)
}

def check_pii_violation(text: str) -> tuple[bool, str | None]:
    """Valida si el texto contiene PII u otros datos sensibles, devolviendo el tipo de violación."""
    for pii_type, pattern in PII_PATTERNS.items():
        if pattern.search(text):
            return True, pii_type
    return False, None

def load_memory_bank() -> dict:
    """Carga la base de datos de memoria."""
    os.makedirs(MEMORY_FILE.parent, exist_ok=True)
    if MEMORY_FILE.exists():
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_memory_bank(data: dict):
    """Guarda la base de datos de memoria."""
    os.makedirs(MEMORY_FILE.parent, exist_ok=True)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def tool_query_memory(topic: str) -> str:
    """
    Consulta la Memoria de Largo Plazo (Memory Bank) del proyecto sobre un tema o tópico específico.
    
    Args:
        topic: El tema, entidad o concepto que se desea consultar.
    Returns:
        Registro de observaciones y recuerdos asociados al tema.
    """
    bank = load_memory_bank()
    topic_clean = topic.strip().lower()
    
    if topic_clean in bank:
        records = bank[topic_clean]
        result = f"🧠 Recuerdos encontrados sobre '{topic}':\n"
        for rec in records:
            result += f"  - [{rec['timestamp']}] {rec['observation']}\n"
        return result
    return f"🧠 Sin recuerdos previos registrados sobre el tema '{topic}'."

def tool_commit_to_memory(topic: str, observation: str) -> str:
    """
    Guarda y persiste una observación relevante en la Memoria de Largo Plazo (Memory Bank).
    Esta acción es auditada por la política de seguridad del Agent Gateway (PII Filter).
    
    Args:
        topic: El tema, entidad o concepto con el que asociar la observación.
        observation: La información, regla o dato clave que se desea recordar a largo plazo.
    Returns:
        Mensaje de éxito o de rechazo por violación de seguridad de menor privilegio.
    """
    # 1. Auditoría del Agent Gateway (PII Filter)
    has_pii, pii_type = check_pii_violation(observation)
    if has_pii:
        print(f"\n🛡️ [Agent Gateway] TRANSACCIÓN BLOQUEADA: Intento de guardar PII de tipo '{pii_type}'.")
        return f"RECHAZADO: Transacción bloqueada por el Agent Gateway. Razón: La observación contiene datos sensibles del tipo '{pii_type}' (PII detectado)."

    # 2. Registrar el recuerdo
    bank = load_memory_bank()
    topic_clean = topic.strip().lower()
    
    record = {
        "timestamp": datetime.datetime.now().isoformat(),
        "observation": observation.strip()
    }
    
    if topic_clean not in bank:
        bank[topic_clean] = []
        
    bank[topic_clean].append(record)
    save_memory_bank(bank)
    
    print(f"\n🧠 [Memory Bank] Recuerdo guardado exitosamente sobre '{topic}'.")
    return f"ÉXITO: Observación registrada en la memoria a largo plazo bajo el tema '{topic}'."
