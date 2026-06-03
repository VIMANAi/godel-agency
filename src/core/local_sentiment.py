"""
local_sentiment.py — Análisis de sentimiento 100% local con Ollama
SAIEL · Sistema de Análisis de Inteligencia Electoral Local

Usa DeepSeek-R1:7b para clasificar y analizar comentarios políticos
sin enviar datos a ninguna API externa. Ideal para datos sensibles.

Uso:
    python engine/local_sentiment.py --input data/raw/comentarios.json
    python engine/local_sentiment.py --input data/raw/comentarios.json --model qwen2.5-coder:3b
"""

import os
import json
import time
import argparse
from pathlib import Path

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────

MODELOS_DISPONIBLES = {
    "deepseek":  "deepseek-r1:7b",      # Mejor razonamiento político
    "qwen":      "qwen2.5-coder:3b",    # Más rápido, menor contexto
    "bge":       "bge-m3",              # Solo embeddings, no chat
}

MODELO_DEFAULT = MODELOS_DISPONIBLES["deepseek"]
BATCH_SIZE = 10   # Menor que Gemini (LLM local es más lento)
DELAY_LOTES = 0.5

# Detectar ruta base
if os.name == "nt":  # Windows
    BASE_DIR = Path("G:/Mi unidad/SAIEL_Inteligencia_Politica")
else:  # Linux/Parrot
    BASE_DIR = Path.home() / "GoogleDrive/Mi unidad/SAIEL_Inteligencia_Politica"
    if not BASE_DIR.exists():
        BASE_DIR = Path.home() / "Dev/Projects/SAIEL"

# ─── PROMPT ───────────────────────────────────────────────────────────────────

PROMPT_SENTIMIENTO = """Eres un analista político experto en mexicano.
Analiza estos comentarios de redes sociales sobre candidatos de Nayarit, México.

Para cada comentario, devuelve EXACTAMENTE este JSON (sin texto extra):
[
  {{
    "texto": "comentario original",
    "sentimiento": "positivo|negativo|neutro|ironico",
    "intensidad": 1-5,
    "tema": "tema principal en 2-3 palabras",
    "categoria": "gestion|imagen|critica|apoyo|neutro|spam",
    "es_bot": false,
    "nota": "observación breve si aplica"
  }}
]

Comentarios:
{comentarios}

IMPORTANTE: Responde SOLO con el JSON. Sin explicaciones. Sin markdown."""

PROMPT_RESUMEN_ESTRATEGICO = """Eres un asesor político senior en México.
Analiza este conjunto de datos de sentimiento y dame un reporte ejecutivo BREVE:

Datos: {datos}

Dame exactamente:
1. **SALUD DIGITAL** (porcentaje positivo/negativo/neutro)
2. **TOP 3 TEMAS** que más preocupan a la ciudadanía
3. **ALERTA DE CRISIS** (si sentimiento negativo > 60%)
4. **RECOMENDACIÓN TÁCTICA** (1 acción concreta para esta semana)

Formato: Markdown. Máximo 200 palabras. En español."""

# ─── FUNCIONES ────────────────────────────────────────────────────────────────

def verificar_ollama(modelo: str) -> bool:
    """Verifica que Ollama esté corriendo y el modelo disponible."""
    try:
        import ollama
        modelos_disponibles = [m.model for m in ollama.list().models]
        if modelo not in modelos_disponibles:
            print(f"⚠️  Modelo '{modelo}' no encontrado.")
            print(f"   Descárgalo con: ollama pull {modelo}")
            print(f"   Modelos disponibles: {modelos_disponibles}")
            return False
        print(f"✅ Ollama OK — Modelo: {modelo}")
        return True
    except ImportError:
        print("❌ Librería 'ollama' no instalada. Ejecuta: pip install ollama")
        return False
    except Exception as e:
        print(f"❌ Ollama no está corriendo: {e}")
        print("   Inicia Ollama con: ollama serve")
        return False


def cargar_comentarios(ruta: str) -> list:
    """
    Carga comentarios en múltiples formatos.
    Soporta JSON tradicional y NDJSON (línea por línea).

    Args:
        ruta (str): La ruta al archivo de comentarios.

    Returns:
        list: Lista de diccionarios con el texto original, fuente y fecha.
    """
    ruta_path = Path(ruta)
    if not ruta_path.is_absolute():
        ruta_path = BASE_DIR / ruta

    if not ruta_path.exists():
        print(f"❌ Archivo no encontrado: {ruta_path}")
        return []

    with open(ruta_path, "r", encoding="utf-8") as f:
        # Detectar NDJSON (Zeeschuimer) vs JSON normal
        contenido = f.read().strip()

    comentarios = []
    if contenido.startswith("[") or contenido.startswith("{"):
        datos = json.loads(contenido)
        if isinstance(datos, list):
            for item in datos:
                texto = (item.get("text") or item.get("comment") or
                         item.get("texto") or item.get("texto_limpio") or
                         item.get("caption") or str(item))
                if texto and len(texto.strip()) > 3:
                    comentarios.append({
                        "texto_original": texto.strip(),
                        "fuente": item.get("username", item.get("fuente", "?")),
                        "fecha": item.get("timestamp", item.get("fecha", ""))
                    })
        elif isinstance(datos, dict):
            # Formato reporte SAIEL
            for narrativa in datos.get("narrativas", []):
                for ejemplo in narrativa.get("ejemplos_clave", []):
                    comentarios.append({"texto_original": ejemplo, "fuente": "sensemaker", "fecha": ""})
    else:
        # NDJSON línea por línea
        for linea in contenido.split("\n"):
            linea = linea.strip()
            if not linea:
                continue
            try:
                item = json.loads(linea)
                texto = item.get("text") or item.get("comment") or str(item)
                if texto and len(texto.strip()) > 3:
                    comentarios.append({"texto_original": texto.strip(), "fuente": "ndjson", "fecha": ""})
            except json.JSONDecodeError:
                continue

    print(f"📥 {len(comentarios)} comentarios cargados desde {ruta_path.name}")
    return comentarios


def analizar_lote_local(modelo: str, lote: list) -> list:
    """
    Analiza un lote de comentarios con el LLM local.

    Args:
        modelo (str): Modelo en Ollama.
        lote (list): Lista de diccionarios de comentarios.

    Returns:
        list: Lista con el análisis estructurado.
    """
    try:
        import ollama
    except ImportError:
        print("❌ Librería 'ollama' no instalada. No se puede analizar.")
        return []

    textos = [f"{i+1}. {c['texto_original']}" for i, c in enumerate(lote)]
    prompt = PROMPT_SENTIMIENTO.format(comentarios="\n".join(textos))

    try:
        respuesta = ollama.chat(
            model=modelo,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.1, "top_p": 0.9}
        )
        texto_resp = respuesta["message"]["content"].strip()

        # Limpiar bloques markdown si los hay
        if "```" in texto_resp:
            partes = texto_resp.split("```")
            for p in partes:
                p_clean = p.strip()
                if p_clean.startswith("json"):
                    p_clean = p_clean[4:].strip()
                if p_clean.startswith("["):
                    texto_resp = p_clean
                    break

        # Extraer JSON si hay texto extra antes/después
        inicio = texto_resp.find("[")
        fin    = texto_resp.rfind("]") + 1
        if inicio != -1 and fin > inicio:
            texto_resp = texto_resp[inicio:fin]

        return json.loads(texto_resp)

    except json.JSONDecodeError as e:
        print(f"  ⚠️  Error parseando JSON: {e}")
        return [{"texto": c["texto_original"], "sentimiento": "neutro",
                 "intensidad": 2, "tema": "sin clasificar",
                 "categoria": "neutro", "es_bot": False, "nota": "error_parse"} for c in lote]
    except Exception as e:
        print(f"  ❌ Error Ollama: {e}")
        return []


def generar_resumen_estrategico(modelo: str, resultados: list) -> str:
    """Genera un resumen ejecutivo con análisis estratégico."""
    import ollama

    # Estadísticas básicas
    total = len(resultados)
    sentimientos = {}
    temas = {}
    for r in resultados:
        s = r.get("sentimiento", "neutro")
        t = r.get("tema", "sin clasificar")
        sentimientos[s] = sentimientos.get(s, 0) + 1
        temas[t] = temas.get(t, 0) + 1

    stats = {
        "total": total,
        "sentimientos": {k: f"{v} ({v/total*100:.0f}%)" for k, v in sentimientos.items()},
        "top_temas": sorted(temas.items(), key=lambda x: -x[1])[:5]
    }

    prompt = PROMPT_RESUMEN_ESTRATEGICO.format(datos=json.dumps(stats, ensure_ascii=False))

    try:
        respuesta = ollama.chat(
            model=modelo,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.3}
        )
        return respuesta["message"]["content"]
    except Exception as e:
        return f"Error generando resumen: {e}"


def guardar_resultados(resultados: list, ruta_output: Path):
    """Guarda resultados y genera estadísticas."""
    ruta_output.parent.mkdir(parents=True, exist_ok=True)

    with open(ruta_output, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    # Estadísticas de consola
    total = len(resultados)
    sentimientos = {}
    temas = {}
    bots = sum(1 for r in resultados if r.get("es_bot", False))

    for r in resultados:
        s = r.get("sentimiento", "neutro")
        t = r.get("tema", "?")
        sentimientos[s] = sentimientos.get(s, 0) + 1
        temas[t] = temas.get(t, 0) + 1

    print(f"\n{'='*55}")
    print(f"  ANÁLISIS LOCAL COMPLETADO")
    print(f"{'='*55}")
    print(f"  Total analizados : {total}")
    print(f"  Bots detectados  : {bots}")
    print(f"\n  Sentimiento:")
    for s, n in sorted(sentimientos.items(), key=lambda x: -x[1]):
        barra = "█" * int(n / total * 20)
        print(f"  {s:10} {barra} {n} ({n/total*100:.0f}%)")
    print(f"\n  Top temas:")
    for tema, n in sorted(temas.items(), key=lambda x: -x[1])[:6]:
        print(f"  {tema:25} {n:3}")
    print(f"\n  💾 Guardado en: {ruta_output}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Análisis de sentimiento local con Ollama")
    parser.add_argument("--input",  default="data/raw/comentarios.json",
                        help="Archivo JSON de entrada")
    parser.add_argument("--output", default="data/processed/sentimiento_local.json",
                        help="Archivo JSON de salida")
    parser.add_argument("--model",  default=MODELO_DEFAULT,
                        help=f"Modelo Ollama (default: {MODELO_DEFAULT})")
    parser.add_argument("--resumen", action="store_true",
                        help="Generar resumen estratégico al final")
    args = parser.parse_args()

    print("=" * 55)
    print("  🧠 SAIEL — Análisis Local con Ollama")
    print("=" * 55)

    # Verificar Ollama
    if not verificar_ollama(args.model):
        raise SystemExit(1)
    # Cargar datos
    comentarios = cargar_comentarios(args.input)
    if not comentarios:
        print("❌ Sin comentarios para procesar.")
        return

    # Procesar en lotes
    resultados_completos = []
    total_lotes = (len(comentarios) + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"\n🔄 Procesando {len(comentarios)} comentarios en {total_lotes} lotes...\n")

    for i in range(0, len(comentarios), BATCH_SIZE):
        lote = comentarios[i:i + BATCH_SIZE]
        num_lote = (i // BATCH_SIZE) + 1
        print(f"  Lote {num_lote}/{total_lotes}...", end=" ", flush=True)

        lote_resultado = analizar_lote_local(args.model, lote)

        # Combinar con datos originales
        for j, item_analizado in enumerate(lote_resultado):
            if j < len(lote):
                combinado = {**lote[j], **item_analizado}
                resultados_completos.append(combinado)

        print(f"✅ ({len(lote_resultado)} procesados)")
        if i + BATCH_SIZE < len(comentarios):
            time.sleep(DELAY_LOTES)

    # Guardar
    ruta_out = BASE_DIR / args.output
    guardar_resultados(resultados_completos, ruta_out)

    # Resumen estratégico opcional
    if args.resumen and resultados_completos:
        print(f"\n{'='*55}")
        print("  📊 RESUMEN ESTRATÉGICO (DeepSeek-R1)")
        print(f"{'='*55}\n")
        resumen = generar_resumen_estrategico(args.model, resultados_completos)
        print(resumen)

        # Guardar resumen también
        ruta_resumen = ruta_out.parent / "resumen_estrategico.md"
        ruta_resumen.write_text(resumen, encoding="utf-8")
        print(f"\n💾 Resumen guardado en: {ruta_resumen}")


if __name__ == "__main__":
    import sys
    main()
