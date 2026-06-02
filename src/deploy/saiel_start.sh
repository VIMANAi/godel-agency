#!/bin/bash

# SAIEL Start Script
# Autodetectar ruta del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Activar entorno virtual
if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
else
    echo "[ERROR] No se pudo encontrar el entorno virtual en $PROJECT_ROOT/venv"
    exit 1
fi

# Ejecutar el agente con todos los argumentos pasados al script
python "$PROJECT_ROOT/src/agents/saiel_agent.py" "$@"
