# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");

"""Layer 2: Centralized Tool Governance (Agent Registry)

Controla de forma estricta qué capacidades y herramientas externas/locales
tiene permitido ejecutar el agente, previniendo el surgimiento de "Shadow AI".
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
LOCAL_MANIFEST_FILE = BASE_DIR / "src/agents/agent_manifest.json"
GLOBAL_MANIFEST_FILE = Path("/home/fratfn/Desarrollo/agent_manifest.json")
LEGACY_MANIFEST_FILE = BASE_DIR / "src/agents/manifest.json"
REQUIREMENTS_FILE = BASE_DIR / "requirements.txt"

def deep_merge(dict1: dict, dict2: dict) -> dict:
    """Recursively merges dict2 into dict1. dict2 values override dict1 values."""
    merged = dict1.copy()
    for key, val in dict2.items():
        if isinstance(val, dict) and key in merged and isinstance(merged[key], dict):
            merged[key] = deep_merge(merged[key], val)
        else:
            merged[key] = val
    return merged

def load_merged_manifest() -> dict:
    """Loads and deeply merges global and local manifests."""
    merged = {}
    
    # 1. Cargar el manifiesto GLOBAL de la raíz de Desarrollo
    if GLOBAL_MANIFEST_FILE.exists():
        try:
            with open(GLOBAL_MANIFEST_FILE, "r", encoding="utf-8") as f:
                merged = json.load(f)
                print(f"[Agent Registry] Cargado manifiesto GLOBAL heredado de Desarrollo.")
        except Exception as e:
            print(f"[Agent Registry] Error cargando global manifest: {e}")
            
    # 2. Cargar y mezclar profundamente el manifiesto LOCAL del proyecto
    if LOCAL_MANIFEST_FILE.exists():
        try:
            with open(LOCAL_MANIFEST_FILE, "r", encoding="utf-8") as f:
                local_data = json.load(f)
            merged = deep_merge(merged, local_data)
            print(f"[Agent Registry] Cargado y fusionado manifiesto LOCAL desde: {LOCAL_MANIFEST_FILE.name}")
        except Exception as e:
            print(f"[Agent Registry] Error cargando local manifest: {e}")
            
    return merged

class AgentRegistry:
    """Catálogo centralizado de auditoría de herramientas aprobadas y auditoría de paquetes."""
    
    def __init__(self):
        self.approved_tools = self._load_approved_tools()
        
    def _load_approved_tools(self) -> set:
        """Carga el conjunto de nombres de herramientas aprobadas en cascada jerárquica (Local -> Global -> Legacy -> Fallback)."""
        names = set()
        
        # 1 & 2. Cargar manifiestos fusionados (Global + Local Overrides)
        merged_manifest = load_merged_manifest()
        specialists = merged_manifest.get("specialists", {})
        for spec in specialists.values():
            allowed = spec.get("allowed_tools", [])
            for t in allowed:
                names.add(t)
                # También agregar versión normalizada sin prefijo "tool_" si corresponde
                if t.startswith("tool_"):
                    names.add(t[5:])
                    
        # 3. Retroceder a la compatibilidad con el legado manifest.json si es necesario
        if not specialists and LEGACY_MANIFEST_FILE.exists():
            try:
                with open(LEGACY_MANIFEST_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                tools = data.get("tools", [])
                for t in tools:
                    name = t.get("name")
                    if name:
                        names.add(name)
                        # También agregar versión con prefijo "tool_"
                        names.add(f"tool_{name}")
                print(f"[Agent Registry] Cargado manifiesto de herramientas LEGACY desde: {LEGACY_MANIFEST_FILE.name}")
            except Exception as e:
                print(f"[Agent Registry] Error cargando legacy manifest: {e}")
                
        # Agregar herramientas del SDK nativas estándar que están autorizadas
        # (Ej. las de lectura/búsqueda básicas y las añadidas por nuestro sistema)
        names.update([
            "collect_data", "run_sensemaker", "read_report", "check_crisis",
            "run_sentiment", "list_data_files", "tool_request_executive_approval",
            "tool_query_memory", "tool_commit_to_memory",
            "tool_execute_electoral_workflow", "tool_coordinate_specialists",
            "tool_execute_composed_skills", "tool_run_sandboxed_code",
            "tool_refine_user_story", "tool_generate_system_design",
            "tool_sequence_git_strategy",
            "tool_collect_data", "tool_run_sensemaker", "tool_read_report",
            "tool_check_crisis", "tool_run_sentiment", "tool_list_data_files"
        ])
        
        return names
            
    def validate_tool_call(self, tool_name: str) -> tuple[bool, str]:
        """Audita si la llamada a la herramienta está autorizada en el registro corporativo."""
        # Normalizar
        clean_name = tool_name.strip()
        if clean_name in self.approved_tools:
            return True, f"Herramienta '{clean_name}' verificada y autorizada en el Agent Registry."
            
        print(f"\n🛡️ [Agent Registry] LLAMADA RECHAZADA: Intento de ejecutar herramienta no autorizada ('{clean_name}').")
        return False, f"RECHAZADO: La herramienta '{clean_name}' no está registrada en manifest.json (Shadow AI bloqueada)."

    def audit_dependencies(self) -> list:
        """Realiza un escaneo del archivo requirements.txt para verificar el cumplimiento de dependencias."""
        warnings = []
        if not REQUIREMENTS_FILE.exists():
            warnings.append("Requirements.txt no encontrado. No se puede auditar vulnerabilidades locales.")
            return warnings
            
        try:
            with open(REQUIREMENTS_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            for line in lines:
                line_clean = line.strip()
                if not line_clean or line_clean.startswith("#"):
                    continue
                # Advertir si hay dependencias sin fijar versión
                if "==" not in line_clean and not any(op in line_clean for op in (">=", "<=", "~=")):
                    warnings.append(f"Dependencia '{line_clean}' no tiene versión fija (Riesgo de inestabilidad y supply chain).")
        except Exception as e:
            warnings.append(f"Error al auditar dependencias: {e}")
            
        return warnings

# Instancia global del registro de herramientas
agent_registry = AgentRegistry()
