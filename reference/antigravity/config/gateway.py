# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");

"""Layer 3: Policy Enforcement Gateway (Agent Gateway)

Actúa como punto central de filtrado de seguridad (Gateway/Model Armor) para
prevenir ataques de inyección de prompt (jailbreaks) y validar políticas corporativas
(Ej. restricciones horarias y filtrado de PII saliente).
"""

import os
import re
import datetime
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
AUDIT_LOG_FILE = BASE_DIR / "data/db/gateway_audit.jsonl"

# Firmas de inyección de prompt típicas (jailbreaks, override)
PROMPT_INJECTION_SIGNATURES = [
    re.compile(r"ignore\s+(all\s+)?(previous\s+)?instructions", re.IGNORECASE),
    re.compile(r"ignora\s+(las\s+)?instrucciones\s+(anteriores|del\s+sistema)", re.IGNORECASE),
    re.compile(r"system\s*override", re.IGNORECASE),
    re.compile(r"bypass\s+security", re.IGNORECASE),
    re.compile(r"burlar\s+(la\s+)?seguridad", re.IGNORECASE),
    re.compile(r"developer\s+mode", re.IGNORECASE),
    re.compile(r"modo\s+desarrollador", re.IGNORECASE)
]

class AgentGateway:
    """Gateway de seguridad e interceptor de políticas globales."""
    
    def __init__(self):
        self.policy_violations_count = 0
        
    def screen_prompt(self, user_prompt: str) -> tuple[bool, str | None]:
        """Analiza el prompt del usuario en busca de inyecciones o jailbreaks."""
        for pattern in PROMPT_INJECTION_SIGNATURES:
            if pattern.search(user_prompt):
                self._record_violation("prompt_injection", user_prompt)
                return False, "Inyección de prompt bloqueada por Agent Gateway (Model Armor)."
        return True, None
        
    def enforce_operational_policies(self, tool_name: str) -> tuple[bool, str | None]:
        """Enfuerza políticas organizacionales operativas (Ej. restricciones horarias)."""
        now = datetime.datetime.now()
        is_weekend = now.weekday() >= 5 # 5 = Sábado, 6 = Domingo
        
        # Política de Fin de Semana: No se permiten acciones destructivas o de recolección en fines de semana
        write_and_collect_tools = [
            "tool_collect_data", "tool_commit_to_memory", "run_command", "write_to_file",
            "replace_file_content", "multi_replace_file_content"
        ]
        
        if is_weekend and tool_name in write_and_collect_tools:
            self._record_violation("weekend_write_policy", f"Intento de ejecutar '{tool_name}' en fin de semana.")
            return False, f"Bloqueado por el Gateway: La política organizacional prohíbe acciones de modificación/recolección ('{tool_name}') durante el fin de semana para garantizar el monitoreo del staff."
            
        return True, None
        
    def enforce_federation_safety(self, specialist_name: str, payload: str) -> tuple[bool, str | None]:
        """
        Enfuerza las políticas de federación saliente (Capa 3 / Pattern 4).
        Bloquea el envío de credenciales, datos confidenciales o PII a especialistas externos.
        """
        restricted_keywords = [
            "contraseña", "password", "secreto", "voter_list", "lista_nominal",
            "ine_key", "curp", "api_key"
        ]
        
        payload_lower = payload.lower()
        for kw in restricted_keywords:
            if kw in payload_lower:
                self._record_violation("cross_org_federation_leakage", f"Filtro federación saliente: Bloqueado envío de '{kw}' a '{specialist_name}'.")
                return False, f"Bloqueado por Gateway: Se ha detectado la palabra restringida '{kw}' en el payload de delegación A2A para '{specialist_name}'. La política prohíbe la fuga de datos sensibles fuera de la organización."
                
        return True, None

    def _record_violation(self, violation_type: str, details: str):
        """Registra la infracción en el ledger físico de auditoría."""
        self.policy_violations_count += 1
        timestamp = datetime.datetime.now().isoformat()
        
        os.makedirs(AUDIT_LOG_FILE.parent, exist_ok=True)
        try:
            with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
                log_entry = {
                    "timestamp": timestamp,
                    "type": violation_type,
                    "details": details
                }
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception:
            pass

# Instancia global del Gateway de políticas
agent_gateway = AgentGateway()
