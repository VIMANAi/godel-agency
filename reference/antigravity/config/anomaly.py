# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");

"""Layer 4: Behavioral Anomaly Detection

Monitorea la coherencia y desviaciones del comportamiento operativo del agente.
Detecta bucles infinitos en llamadas a herramientas y razonamientos anormalmente extensos.
"""

import os
import json
import datetime
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
ANOMALY_LOG_FILE = BASE_DIR / "data/db/anomaly_alerts.jsonl"

class BehavioralAnomalyDetector:
    """Rastreador de métricas operacionales del agente y detector de anomalías."""
    
    def __init__(self):
        self.step_count = 0
        self.tool_call_history = []
        self.alerts_count = 0
        
    def reset_turn(self):
        """Reinicia las métricas al inicio de cada nuevo turno conversacional."""
        self.step_count = 0
        self.tool_call_history = []
        
    def record_step(self) -> tuple[bool, str | None]:
        """Registra un paso de razonamiento en la cadena actual y audita longitud."""
        self.step_count += 1
        if self.step_count > 10:
            msg = f"Desviación de razonamiento detectada: Longitud de cadena inusualmente alta ({self.step_count} pasos)."
            self._log_anomaly("excessive_reasoning_steps", msg)
            return True, msg
        return False, None
        
    def record_tool_call(self, tool_name: str) -> tuple[bool, str | None]:
        """Registra una llamada a herramienta y audita bucles repetitivos."""
        self.tool_call_history.append(tool_name)
        
        # Auditar si la misma herramienta se ha ejecutado de forma repetitiva consecutiva (>3 veces)
        if len(self.tool_call_history) >= 4:
            last_four = self.tool_call_history[-4:]
            if len(set(last_four)) == 1:
                msg = f"Bucle operativo potencial detectado: Invocación consecutiva repetida de la herramienta '{tool_name}' ({len(last_four)} veces)."
                self._log_anomaly("tool_looping_drift", msg)
                return True, msg
                
        return False, None
        
    def _log_anomaly(self, anomaly_type: str, message: str):
        """Guarda la alerta de anomalía en el log de auditoría."""
        self.alerts_count += 1
        timestamp = datetime.datetime.now().isoformat()
        
        os.makedirs(ANOMALY_LOG_FILE.parent, exist_ok=True)
        try:
            with open(ANOMALY_LOG_FILE, "a", encoding="utf-8") as f:
                alert_entry = {
                    "timestamp": timestamp,
                    "type": anomaly_type,
                    "message": message
                }
                f.write(json.dumps(alert_entry, ensure_ascii=False) + "\n")
        except Exception:
            pass

# Instancia global del detector de anomalías
anomaly_detector = BehavioralAnomalyDetector()
