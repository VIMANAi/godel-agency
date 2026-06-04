# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");

"""Módulo de seguridad interactivo y descriptivo para el SDK de Google Antigravity.

Este módulo implementa políticas de menor privilegio combinando la permisividad
automática en directorios de trabajo seguros y la consulta interactiva con
explicación explícita de objetivos para comandos de consola y accesos externos.
"""

import os
from google.antigravity import types
from google.antigravity.hooks import policy
from google.antigravity.utils.interactive import async_input

# Directorios de trabajo locales seguros donde se permite lectura/escritura libre
ALLOWED_PREFIXES = [
    "/home/fratfn/Desarrollo/Agency",
    "/home/fratfn/Desarrollo/Databases"
]

def is_path_allowed(path: str) -> bool:
    """Verifica si la ruta solicitada está dentro de los directorios permitidos."""
    if not path:
        return False
    abs_path = os.path.abspath(path)
    return any(abs_path.startswith(prefix) for prefix in ALLOWED_PREFIXES)

def is_writing_outside(args: dict) -> bool:
    """Predicado para determinar si el agente intenta escribir fuera de las áreas autorizadas."""
    target_file = args.get("TargetFile")
    return not is_path_allowed(target_file)

async def interactive_confirm_handler(tc: types.ToolCall) -> bool:
    """Handler interactivo de seguridad.
    
    Intercepta llamadas a herramientas críticas, deduce el objetivo de la acción
    e interactúa con el usuario solicitando confirmación con una explicación clara.
    """
    print("\n" + "="*60)
    print("⚠️  SOLICITUD DE CONFIRMACIÓN DE SEGURIDAD (HOOK INTERACTIVO)")
    print("="*60)
    print(f"🔧 Herramienta Solicitada: {tc.name}")
    
    # 1. Deducir e informar el objetivo
    objetivo = "No especificado"
    detalles = ""
    
    if tc.name == "run_command":
        cmd = tc.arguments.get("CommandLine", "") if tc.arguments else ""
        detalles = f"Comando a ejecutar: {cmd}"
        # Deducir intención semántica
        if "git" in cmd:
            objetivo = "Control de versiones (Git) para registrar o publicar cambios de código."
        elif "uv" in cmd or "pip" in cmd:
            objetivo = "Instalación o actualización de dependencias en el entorno virtual local."
        elif "python" in cmd:
            objetivo = "Ejecución de un script local de Python para pruebas o pipelines."
        else:
            objetivo = "Ejecución de un comando en la consola del sistema (bash)."
            
    elif tc.name in ("write_to_file", "replace_file_content", "multi_replace_file_content"):
        target = tc.arguments.get("TargetFile", "") if tc.arguments else ""
        detalles = f"Ruta física del archivo: {target}"
        objetivo = "Modificación o creación de un archivo fuera de los directorios locales autorizados."
        
    print(f"🎯 Objetivo del Agente: {objetivo}")
    if detalles:
        print(f"📝 Detalles Técnicos : {detalles}")
    print("-"*60)
    
    # 2. Solicitar autorización interactiva
    try:
        ans = await async_input("¿Deseas permitir esta acción de forma excepcional? (y/n) [n]: ")
    except EOFError:
        ans = "n"
        
    print("="*60 + "\n")
    return ans.strip().lower() in ("y", "yes")

# Definición de políticas declarativas con cortocircuito por prioridad
policies = [
    # A. Permitir de forma nativa lecturas y búsquedas básicas
    policy.allow("view_file"),
    policy.allow("list_dir"),
    policy.allow("grep_search"),
    
    # B. Permitir escrituras libres y automáticas SOLO dentro del entorno seguro de Desarrollo
    policy.allow("write_to_file", when=lambda args: not is_writing_outside(args)),
    policy.allow("replace_file_content", when=lambda args: not is_writing_outside(args)),
    policy.allow("multi_replace_file_content", when=lambda args: not is_writing_outside(args)),
    
    # C. Si se intenta escribir fuera de la zona segura, solicitar confirmación con explicación del objetivo
    policy.ask_user("write_to_file", handler=interactive_confirm_handler, when=is_writing_outside),
    policy.ask_user("replace_file_content", handler=interactive_confirm_handler, when=is_writing_outside),
    policy.ask_user("multi_replace_file_content", handler=interactive_confirm_handler, when=is_writing_outside),
    
    # D. Exigir SIEMPRE confirmación con explicación del objetivo para ejecución de comandos bash
    policy.ask_user("run_command", handler=interactive_confirm_handler),
    
    # E. Bloquear por defecto cualquier otra herramienta destructiva o de escritura no declarada
    policy.deny("*")
]

# F. Inyectar dinámicamente herramientas legítimas del Agent Registry para evitar doble interceptación
try:
    from config.registry import agent_registry
    for tool in agent_registry.approved_tools:
        # No sobreescribir las que tienen reglas complejas específicas
        if tool not in ["write_to_file", "replace_file_content", "multi_replace_file_content", "run_command"]:
            policies.insert(0, policy.allow(tool))
            # También soportar el formato con prefijo "tool_" si aplica
            if not tool.startswith("tool_"):
                policies.insert(0, policy.allow(f"tool_{tool}"))
except Exception:
    pass

# Generación del Hook de decisión de seguridad principal
security_hook = policy.enforce(policies)
