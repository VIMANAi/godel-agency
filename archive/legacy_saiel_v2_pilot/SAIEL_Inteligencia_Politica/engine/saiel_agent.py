"""
SAIEL Agent - Agente Local de Inteligencia Politica
Usa smolagents para orquestar el pipeline completo.
Funciona sin GPU dedicada (CPU only via Ollama).

Instalacion:
    pip install smolagents ollama

Uso:
    python engine/saiel_agent.py
    > "Analiza los datos de Geraldine Ponce y dame un resumen"
    > "Recolecta datos de Andrea Navarro y genera la matriz"
    > "Hay alguna crisis en las narrativas actuales?"
"""

import subprocess
import sys
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ── HERRAMIENTAS (Tools) que el agente puede usar ──────────────────────────

def tool_collect_data(target_url: str) -> str:
    """
    Recolecta comentarios de Instagram/Facebook via Apify.
    Args:
        target_url: URL del post o perfil a analizar
    Returns:
        Ruta del archivo JSON generado
    """
    result = subprocess.run(
        [sys.executable, str(BASE_DIR / "engine/social_collector.py"),
         "--target", target_url],
        capture_output=True, text=True, cwd=str(BASE_DIR)
    )
    if result.returncode == 0:
        return f"Datos recolectados exitosamente. {result.stdout}"
    return f"Error: {result.stderr[:200]}"


def tool_run_sensemaker() -> str:
    """
    Ejecuta el motor de Sensemaking para descubrir narrativas.
    Returns:
        Resumen de narrativas encontradas
    """
    result = subprocess.run(
        [sys.executable, str(BASE_DIR / "engine/sensemaker_engine.py")],
        capture_output=True, text=True, cwd=str(BASE_DIR)
    )
    
    # Leer el reporte generado
    report_path = BASE_DIR / "data/processed/reporte_industrial_narrativas.json"
    if report_path.exists():
        with open(report_path, "r", encoding="utf-8") as f:
            report = json.load(f)
        
        summary = f"Shannon Index: {report.get('shannon_diversity', 'N/A')} ({report.get('interpretacion_shannon', '')})\n"
        summary += f"Total comentarios: {report.get('total_comentarios', 0)}\n\n"
        
        for n in report.get('narrativas', []):
            summary += f"Narrativa #{n['id_narrativa']}: {n['porcentaje']}% del volumen, sentimiento {n['sentimiento_salud']}\n"
        
        alertas = report.get('alertas_crisis', [])
        if alertas:
            summary += f"\nALERTAS: {len(alertas)} narrativa(s) en estado critico"
        
        return summary
    
    return result.stdout or result.stderr


def tool_read_report() -> str:
    """
    Lee el ultimo reporte de narrativas generado.
    Returns:
        Contenido del reporte en formato legible
    """
    report_path = BASE_DIR / "data/processed/reporte_industrial_narrativas.json"
    if not report_path.exists():
        return "No hay reportes generados aun. Ejecuta primero el Sensemaker."
    
    with open(report_path, "r", encoding="utf-8") as f:
        return json.dumps(json.load(f), indent=2, ensure_ascii=False)


def tool_check_crisis() -> str:
    """
    Verifica si hay narrativas en estado de crisis.
    Returns:
        Lista de alertas activas
    """
    report_path = BASE_DIR / "data/processed/reporte_industrial_narrativas.json"
    if not report_path.exists():
        return "Sin datos. Ejecuta el Sensemaker primero."
    
    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)
    
    # Compatibilidad con formato antiguo (lista) y nuevo (dict)
    if isinstance(report, list):
        return "Reporte en formato antiguo. Ejecuta el Sensemaker actualizado para obtener alertas."
    
    alertas = report.get('alertas_crisis', [])
    if not alertas:
        return "Sin alertas de crisis activas. Todas las narrativas en zona normal."
    
    resultado = f"{len(alertas)} alerta(s) activa(s):\n"
    for a in alertas:
        resultado += f"  [{a['severidad']}] {a['mensaje']}\n"
    return resultado


def tool_run_sentiment(target_file: str = None) -> str:
    """
    Ejecuta el analisis de sentimiento local.
    Args:
        target_file: Archivo especifico a analizar (opcional)
    Returns:
        Estado del analisis
    """
    cmd = [sys.executable, str(BASE_DIR / "engine/local_sentiment.py")]
    if target_file:
        cmd.append(target_file)
        
    result = subprocess.run(
        cmd,
        capture_output=True, text=True, cwd=str(BASE_DIR)
    )
    if result.returncode == 0:
        return "Analisis de sentimiento completado exitosamente."
    return f"Error en sentimiento: {result.stderr[:200]}"


def tool_list_data_files() -> str:
    """
    Lista los archivos de datos disponibles para analizar.
    Returns:
        Lista de archivos en data/raw y data/processed
    """
    raw_files = list((BASE_DIR / "data/raw").glob("*.json"))
    processed_files = list((BASE_DIR / "data/processed").glob("*.json"))
    
    result = f"Datos raw ({len(raw_files)} archivos):\n"
    for f in raw_files:
        result += f"  - {f.name} ({f.stat().st_size} bytes)\n"
    
    result += f"\nDatos procesados ({len(processed_files)} archivos):\n"
    for f in processed_files:
        result += f"  - {f.name} ({f.stat().st_size} bytes)\n"
    
    return result


# ── AGENTE PRINCIPAL ────────────────────────────────────────────────────────

def run_agent_simple(query: str) -> str:
    """
    Agente simple basado en reglas (sin LLM).
    Interpreta comandos en lenguaje natural y ejecuta las herramientas.
    
    Funciona sin Ollama instalado.
    """
    query_lower = query.lower()
    
    # Detectar intención
    if any(word in query_lower for word in ["recolect", "collect", "scrape", "datos de"]):
        # Extraer URL o nombre del target
        words = query.split()
        target = next((w for w in words if "instagram.com" in w or "facebook.com" in w), None)
        if target:
            return tool_collect_data(target)
        return "Por favor especifica una URL de Instagram o Facebook."
    
    elif any(word in query_lower for word in ["analiz", "sensemaker", "narrativa", "tema"]):
        return tool_run_sensemaker()
    
    elif any(word in query_lower for word in ["sentimiento", "sentiment", "emocion"]):
        return tool_run_sentiment()
    
    elif any(word in query_lower for word in ["crisis", "alerta", "problema", "negativ"]):
        return tool_check_crisis()
    
    elif any(word in query_lower for word in ["reporte", "report", "resultado", "informe"]):
        return tool_read_report()
    
    elif any(word in query_lower for word in ["archivo", "datos", "file", "lista"]):
        return tool_list_data_files()
    
    else:
        return """Comandos disponibles:
- "Recolecta datos de [URL]" → Extrae comentarios via Apify
- "Analiza las narrativas" → Ejecuta el Sensemaker
- "Analiza el sentimiento" → Ejecuta el analisis de sentimiento
- "Hay alguna crisis?" → Verifica alertas activas
- "Muestra el reporte" → Lee el ultimo reporte
- "Lista los archivos" → Ver datos disponibles
"""


def run_agent_with_llm(query: str, model: str = "deepseek-r1:7b") -> str:
    """
    Agente avanzado usando LLM local via Ollama.
    Requiere: pip install ollama && ollama pull deepseek-r1:7b
    """
    try:
        import ollama
        
        # Contexto del sistema
        tools_description = """
Eres un analista de inteligencia politica. Tienes acceso a estas herramientas:
1. tool_collect_data(url) - Recolecta datos de redes sociales
2. tool_run_sensemaker() - Analiza narrativas con IA
3. tool_run_sentiment(file) - Analiza sentimiento local de un archivo
4. tool_check_crisis() - Verifica alertas de crisis
5. tool_read_report() - Lee el ultimo reporte
6. tool_list_data_files() - Lista archivos disponibles

Responde de forma concisa y profesional. Si necesitas ejecutar una herramienta, 
indica cual y por que.
"""
        
        # Leer contexto actual
        current_data = tool_list_data_files()
        
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": tools_description},
                {"role": "user", "content": f"Datos actuales:\n{current_data}\n\nConsulta: {query}"}
            ]
        )
        
        return response['message']['content']
    
    except ImportError:
        return "Ollama no instalado. Usando agente simple.\n\n" + run_agent_simple(query)
    except Exception as e:
        return f"Error con LLM: {e}\n\nUsando agente simple:\n" + run_agent_simple(query)


# ── INTERFAZ DE LINEA DE COMANDOS ───────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("SAIEL Agent - Asistente de Inteligencia Politica")
    print("Escribe 'salir' para terminar")
    print("=" * 60)
    
    # Detectar si Ollama esta disponible
    try:
        import ollama
        ollama.list()
        use_llm = True
        print("[OK] Ollama detectado. Usando modo LLM avanzado.")
    except Exception:
        use_llm = False
        print("[INFO] Ollama no disponible. Usando modo simple.")
    
    print()
    
    # Soporte para argumentos de linea de comandos (CLI)
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        is_direct_command = query.startswith("--")
        
        if is_direct_command: # Limpiar flags si se pasan como --sentimiento
            query = query.replace("--", "")
        
        print(f"\nEjecutando comando: {query}")
        
        # Si es un comando directo (--flag) o no queremos usar LLM para comandos CLI deterministas
        if is_direct_command or not use_llm:
            response = run_agent_simple(query)
        else:
            response = run_agent_with_llm(query)
            
        print(f"\nAgente: {response}\n")
        sys.exit(0)

    while True:
        try:
            query = input("Tu consulta > ").strip()
            if query.lower() in ["salir", "exit", "quit"]:
                break
            if not query:
                continue
            
            print("\nProcesando...")
            if use_llm:
                response = run_agent_with_llm(query)
            else:
                response = run_agent_simple(query)
            
            print(f"\nAgente: {response}\n")
            print("-" * 40)
        
        except KeyboardInterrupt:
            break
    
    print("\nAgente SAIEL cerrado.")
