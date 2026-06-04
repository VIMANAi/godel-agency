# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");

"""Layer 1: Agent Identity (IAM for Agents)

Establece una identidad criptográfica única y trazable para el agente Godel,
derivada de su manifest.json de configuración y sus fuentes de código.
"""

import os
import json
import hashlib
import uuid
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
CODE_FILE = BASE_DIR / "src/agents/godel_agent.py"

class AgentIdentity:
    """Representa la credencial criptográfica e identidad única del agente."""
    
    def __init__(self):
        self.agent_id = "saiel_political_intelligence_agent"
        self.name = "SAIEL Agent"
        self.version = "2.5"
        self.instance_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, "godel.saiel.political.intelligence"))
        self.signature_hash = self._generate_cryptographic_signature()
        
    def _generate_cryptographic_signature(self) -> str:
        """Genera un hash SHA-256 único a partir del manifiesto de configuración y el código ejecutable."""
        sha256 = hashlib.sha256()
        
        # 1. Hashear el manifiesto declarativo
        if MANIFEST_FILE.exists():
            try:
                with open(MANIFEST_FILE, "rb") as f:
                    sha256.update(f.read())
            except Exception:
                sha256.update(b"manifest_error")
        else:
            sha256.update(b"no_manifest")
            
        # 2. Hashear el código base principal
        if CODE_FILE.exists():
            try:
                with open(CODE_FILE, "rb") as f:
                    sha256.update(f.read())
            except Exception:
                sha256.update(b"code_error")
        else:
            sha256.update(b"no_code")
            
        return sha256.hexdigest()[:16] # Retornamos los primeros 16 caracteres para legibilidad

    def get_identity_string(self) -> str:
        """Retorna la cadena estructurada de identidad para los logs de auditoría."""
        return f"[AgentID: {self.agent_id} | UUID: {self.instance_uuid} | Sig: {self.signature_hash}]"

# Instancia global única de identidad del agente
agent_identity = AgentIdentity()
