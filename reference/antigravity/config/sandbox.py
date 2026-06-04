# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");

"""Pattern 5: Hosted Sandbox Execution (Process-Level Isolation)

Este módulo implementa el patrón de Ejecución Aislada en Sandbox de ADK 2.0.
Provee un mecanismo seguro para ejecutar transformaciones de datos o cálculos 
personalizados en un entorno de proceso aislado, limitando el acceso a recursos del
sistema host (red, disco) y aplicando restricciones de tiempo de ejecución (timeout)
y consumo estricto de RAM.
"""

import sys
import os
import subprocess
import tempfile
import json
import logging
from pathlib import Path
from typing import Dict, Any

try:
    import resource
    HAS_RESOURCE = True
except ImportError:
    HAS_RESOURCE = False

logger = logging.getLogger("godel.orchestration.sandbox")
logging.basicConfig(level=logging.INFO)

# Restricciones operativas del sandbox
MAX_EXECUTION_TIMEOUT = 3.0 # Segundos máximos de ejecución
BLOCKED_KEYWORDS = ["import os", "import sys", "import subprocess", "socket", "urllib", "requests", "open(", "eval("]

def limit_resources():
    """Establece límites físicos a nivel de kernel para el proceso hijo en Linux."""
    if HAS_RESOURCE:
        # Límite estricto de memoria virtual (RLIMIT_AS) a 128MB
        max_mem = 128 * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (max_mem, max_mem))

class HostedSandboxExecutor:
    """Ejecutor de código Python aislado a nivel de subproceso y entorno acotado."""
    
    def __init__(self):
        # Confinamiento dinámico usando la ruta base de la plataforma si está configurada
        base_path_env = os.getenv("AGENCY_BASE_PATH", os.getenv("SAIEL_BASE_PATH"))
        if base_path_env:
            self.sandbox_dir = Path(base_path_env) / "tmp/godel_sandbox"
        else:
            self.sandbox_dir = Path(tempfile.gettempdir()) / "godel_sandbox"
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)

    def validate_safety(self, script: str) -> tuple[bool, str | None]:
        """Realiza análisis estático preliminar para mitigar inyecciones de código malicioso."""
        script_lower = script.lower()
        
        # Bloquear uso de palabras clave de intrusión física o red
        for kw in BLOCKED_KEYWORDS:
            if kw in script_lower:
                return False, f"Código RECHAZADO: Uso detectado de palabra clave bloqueada '{kw}' (Riesgo de intrusión o evasión)."
                
        return True, None

    def execute_script(self, script: str) -> Dict[str, Any]:
        """Ejecuta el código en un proceso de Python aislado con entorno (env) mínimo."""
        is_safe, error_msg = self.validate_safety(script)
        if not is_safe:
            logger.warning(f"[Sandbox Block] {error_msg}")
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": error_msg,
                "error_type": "StaticAnalysisViolation"
            }
            
        # Crear archivo temporal físico para el script dentro del directorio del sandbox
        temp_file = tempfile.NamedTemporaryFile(suffix=".py", dir=self.sandbox_dir, delete=False, mode="w", encoding="utf-8")
        temp_file.write(script)
        temp_file.close()
        
        temp_file_path = Path(temp_file.name)
        
        # Configurar un entorno heredando variables clave del MLOps host
        sandbox_env = {
            "PATH": os.getenv("PATH", ""),
            "PYTHONPATH": os.getenv("PYTHONPATH", ""),
            "LC_ALL": "C.UTF-8",
            "LANG": "C.UTF-8"
        }
        # Variables MLOps heredadas opcionalmente si están presentes en el host
        for key in ["AGENCY_BASE_PATH", "SAIEL_BASE_PATH", "NODE_OPTIONS", "VIRTUAL_ENV", "GOOGLE_APPLICATION_CREDENTIALS"]:
            if key in os.environ:
                sandbox_env[key] = os.environ[key]
        
        try:
            logger.info(f"[Sandbox] Ejecutando subproceso aislado para: {temp_file_path.name}")
            
            # Lanzar el subproceso con límites estrictos de CPU/tiempo y RAM
            result = subprocess.run(
                [sys.executable, "-I", "-S", str(temp_file_path)], # -I aisla el path de python, -S aisla imports
                capture_output=True,
                text=True,
                env=sandbox_env,
                timeout=MAX_EXECUTION_TIMEOUT,
                cwd=str(self.sandbox_dir),
                preexec_fn=limit_resources if HAS_RESOURCE else None
            )
            
            success = result.returncode == 0
            return {
                "success": success,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "error_type": None if success else "RuntimeError"
            }
            
        except subprocess.TimeoutExpired as e:
            logger.error("[Sandbox] Exceso de tiempo límite de ejecución detectado.")
            return {
                "success": False,
                "exit_code": -9,
                "stdout": "",
                "stderr": f"Error: Límite de tiempo excedido ({MAX_EXECUTION_TIMEOUT}s). Proceso finalizado.",
                "error_type": "TimeoutViolation"
            }
        except Exception as e:
            logger.error(f"[Sandbox] Error inesperado en el runner: {e}")
            return {
                "success": False,
                "exit_code": -99,
                "stdout": "",
                "stderr": f"Falla catastrófica del sandbox: {str(e)}",
                "error_type": "SystemFailure"
            }
        finally:
            # Garantizar la eliminación física del script temporal
            if temp_file_path.exists():
                try:
                    temp_file_path.unlink()
                except Exception:
                    pass

def tool_run_sandboxed_code(script: str) -> str:
    """Ejecuta un script de procesamiento de datos o lógica personalizada en un sandbox aislado a nivel proceso.
    
    Args:
        script: Cadena de código Python 3 legítimo a ejecutar.
    Returns:
        JSON con el estado de salida, la salida estándar (stdout) y los errores (stderr) si los hubiera.
    """
    try:
        executor = HostedSandboxExecutor()
        result = executor.execute_script(script)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error al invocar sandbox aislado: {e}")
        return json.dumps({
            "success": False,
            "exit_code": -500,
            "stdout": "",
            "stderr": f"Falla de inicialización: {str(e)}",
            "error_type": "InitializationFailure"
        }, ensure_ascii=False)
