"""
open_interpreter_config.py — Configuración de Open Interpreter para SAIEL
Sistema de Análisis de Inteligencia Electoral Local

Cómo ejecutar (en Parrot OS):
    interpreter --config_file engine/open_interpreter_config.py

O directamente con Python:
    python engine/open_interpreter_config.py

Modelos disponibles (via Ollama local):
    - deepseek-r1:7b   → Razonamiento complejo, análisis estratégico
    - qwen2.5-coder:3b → Generación y modificación de código
    - bge-m3           → Embeddings para búsqueda semántica (no chat)
"""

import os
import sys
from pathlib import Path

# ─── RUTAS DEL PROYECTO ───────────────────────────────────────────────────────

# Detectar si estamos en Parrot o Windows automáticamente
if sys.platform.startswith("linux"):
    # Parrot OS - ajusta esta ruta según tu montaje de rclone/Drive
    PROYECTO_DIR = Path.home() / "GoogleDrive/Mi unidad/SAIEL_Inteligencia_Politica"
    if not PROYECTO_DIR.exists():
        # Ruta alternativa si usas montaje diferente
        PROYECTO_DIR = Path.home() / "Dev/Projects/SAIEL"
else:
    # Windows
    PROYECTO_DIR = Path("G:/Mi unidad/SAIEL_Inteligencia_Politica")

DATA_RAW       = PROYECTO_DIR / "data/raw"
DATA_PROCESSED = PROYECTO_DIR / "data/processed"
ENGINE_DIR     = PROYECTO_DIR / "engine"
REPORTS_DIR    = PROYECTO_DIR / "reports"

# ─── SYSTEM PROMPT PARA OPEN INTERPRETER ──────────────────────────────────────

SAIEL_SYSTEM_PROMPT = f"""
Eres el agente SAIEL (Sistema de Análisis de Inteligencia Electoral Local).
Trabajas para una consultoría de inteligencia política en México, específicamente en Nayarit.

## TU ENTORNO
- Sistema: {'Parrot OS (Linux)' if sys.platform.startswith('linux') else 'Windows'}
- Proyecto: {PROYECTO_DIR}
- Datos raw: {DATA_RAW}
- Datos procesados: {DATA_PROCESSED}
- Motor de análisis: {ENGINE_DIR}

## MODELOS DISPONIBLES (Ollama local)
- deepseek-r1:7b → Para razonamiento estratégico y análisis político profundo
- qwen2.5-coder:3b → Para generar/modificar scripts Python
- bge-m3 → Para búsqueda semántica en datos históricos

## HERRAMIENTAS QUE PUEDES EJECUTAR
1. **Sensemaker** → `python {ENGINE_DIR}/sensemaker_engine.py`
   - Descubre narrativas y clustering de temas en los datos
   
2. **Gemini Cleaner** → `python {ENGINE_DIR}/gemini_cleaner.py --input data/raw/ARCHIVO.json`
   - Limpia y clasifica comentarios con Gemini Flash
   
3. **Local Sentiment** → `python {ENGINE_DIR}/local_sentiment.py`  
   - Análisis de sentimiento sin API (100% local con Ollama)

4. **Datos disponibles** → `ls {DATA_RAW}` / `ls {DATA_PROCESSED}`
   - Para ver qué archivos hay para analizar

5. **Dashboard** → Los reportes HTML están en `{REPORTS_DIR}`

## PROTOCOLO OODA (tu ciclo de trabajo)
1. **OBSERVAR**: Listar datos disponibles y su estado
2. **ORIENTAR**: Identificar qué análisis es más urgente
3. **DECIDIR**: Elegir herramienta y parámetros correctos
4. **ACTUAR**: Ejecutar y reportar hallazgos en formato ejecutivo

## FORMATO DE RESPUESTA
- Habla en español, tono profesional pero directo
- Cuando hagas análisis, usa formato de reporte ejecutivo
- Si detectas crisis o alertas, RESÁLTALAS con 🚨
- Si hay oportunidades estratégicas, márcalas con ✅

## RESTRICCIONES
- NO compartas datos sensibles fuera del proyecto
- Siempre verifica que los archivos existen antes de procesarlos
- Si un script falla, inténtalo con parámetros diferentes antes de rendirte
"""

# ─── CONFIGURACIÓN DE OPEN INTERPRETER ───────────────────────────────────────

def get_interpreter_config():
    """
    Retorna la configuración para Open Interpreter.
    
    Uso:
        from engine.open_interpreter_config import get_interpreter_config
        import interpreter
        config = get_interpreter_config()
        interpreter.system_message = config["system_message"]
        interpreter.llm.model = config["model"]
        ...
    """
    return {
        # Modelo principal: DeepSeek para razonamiento
        "model": "ollama/deepseek-r1:7b",
        
        # Para tareas de código puro, usar Qwen
        "code_model": "ollama/qwen2.5-coder:3b",
        
        # Configuración de Ollama
        "api_base": "http://localhost:11434",
        
        # System prompt personalizado
        "system_message": SAIEL_SYSTEM_PROMPT,
        
        # Directorio de trabajo
        "cwd": str(PROYECTO_DIR),
        
        # Opciones de seguridad
        "safe_mode": "off",       # Permitir ejecución directa (confiamos en el entorno)
        "auto_run": False,        # Pedir confirmación antes de ejecutar código
        
        # Contexto
        "context_window": 8096,
        "max_tokens": 2048,
    }


# ─── MODO INTERACTIVO ─────────────────────────────────────────────────────────

def launch_saiel_interpreter():
    """Lanza Open Interpreter configurado para SAIEL."""
    try:
        import interpreter
    except ImportError:
        print("❌ Open Interpreter no instalado.")
        print("   Instálalo con: pip install open-interpreter")
        sys.exit(1)

    config = get_interpreter_config()
    
    # Aplicar configuración
    interpreter.llm.model          = config["model"]
    interpreter.llm.api_base       = config["api_base"]
    interpreter.system_message     = config["system_message"]
    interpreter.auto_run           = config["auto_run"]
    interpreter.llm.context_window = config["context_window"]
    interpreter.llm.max_tokens     = config["max_tokens"]
    
    # Cambiar al directorio del proyecto
    os.chdir(str(PROYECTO_DIR))
    
    print("=" * 65)
    print("  🧠 SAIEL AGENT — Inteligencia Política con IA Local")
    print("=" * 65)
    print(f"  📁 Proyecto : {PROYECTO_DIR}")
    print(f"  🤖 Modelo   : {config['model']}")
    print(f"  🌐 Ollama   : {config['api_base']}")
    print("=" * 65)
    print()
    print("  Ejemplos de consultas:")
    print("  › 'Lista los datos disponibles y dime cuáles analizar'")
    print("  › 'Ejecuta el sensemaker y dame un resumen ejecutivo'")
    print("  › 'Hay alguna narrativa en crisis? Detállame las alertas'")
    print("  › 'Genera un reporte comparativo de Geraldine vs sus rivales'")
    print()
    print("  Escribe 'salir' o Ctrl+C para terminar")
    print("-" * 65)
    print()

    # Iniciar chat interactivo
    interpreter.chat()


if __name__ == "__main__":
    launch_saiel_interpreter()
