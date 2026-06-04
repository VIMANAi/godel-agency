"""
SAIEL Orchestrator - Coordinador Principal
Recibe datos de Parrot y ejecuta el pipeline completo de análisis.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Determinar ruta base dinámicamente
BASE_DIR = Path(__file__).resolve().parent
DATA_RAW = BASE_DIR / "data" / "raw"
DATA_PROCESSED = BASE_DIR / "data" / "processed"


def check_new_data():
    """Detecta archivos nuevos en data/raw/ enviados desde Parrot."""
    ndjson_files = list(DATA_RAW.glob("*.ndjson"))
    json_files = list(DATA_RAW.glob("zeeschuimer_*.json"))
    new_files = ndjson_files + json_files

    if new_files:
        print(f"[OK] {len(new_files)} archivo(s) nuevo(s) detectado(s):")
        for f in new_files:
            print(f"     - {f.name}")
    else:
        print("[INFO] No hay archivos nuevos de Parrot.")

    return new_files


def convert_zeeschuimer(input_file):
    """Convierte formato Zeeschuimer a formato SAIEL."""
    print(f"[CONVIRTIENDO] {input_file.name}...")

    converted = []

    with open(input_file, "r", encoding="utf-8") as f:
        # Zeeschuimer exporta NDJSON (una linea = un objeto JSON)
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)

                # Extraer campos segun el formato de Zeeschuimer
                # Instagram posts
                if "caption" in item:
                    text = (
                        item.get("caption", {}).get("text", "")
                        if isinstance(item.get("caption"), dict)
                        else item.get("caption", "")
                    )
                    converted.append(
                        {
                            "source": "instagram",
                            "type": "post",
                            "user": item.get("owner", {}).get("username", "unknown"),
                            "text": text,
                            "date": item.get("taken_at", ""),
                            "likes": item.get("like_count", 0),
                            "comments": item.get("comment_count", 0),
                            "collected_at": datetime.now().isoformat(),
                        }
                    )
                # Instagram comments
                elif "text" in item and "ownerUsername" in item:
                    converted.append(
                        {
                            "source": "instagram",
                            "type": "comment",
                            "user": item.get("ownerUsername", "unknown"),
                            "text": item.get("text", ""),
                            "date": item.get("timestamp", ""),
                            "likes": item.get("likesCount", 0),
                            "collected_at": datetime.now().isoformat(),
                        }
                    )
                # Facebook posts/comments
                elif "message" in item:
                    converted.append(
                        {
                            "source": "facebook",
                            "type": "post",
                            "user": item.get("from", {}).get("name", "unknown"),
                            "text": item.get("message", ""),
                            "date": item.get("created_time", ""),
                            "likes": item.get("likes", {}).get("summary", {}).get("total_count", 0),
                            "collected_at": datetime.now().isoformat(),
                        }
                    )
            except json.JSONDecodeError:
                continue

    # Guardar convertido
    output_name = input_file.stem + "_converted.json"
    output_path = DATA_RAW / output_name

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(converted, f, indent=2, ensure_ascii=False)

    print(f"[OK] {len(converted)} registros convertidos -> {output_name}")
    return output_path


def run_sensemaker(data_files):
    """Ejecuta el Sensemaker con los datos nuevos."""
    print("\n[SENSEMAKER] Iniciando analisis de narrativas...")
    result = subprocess.run(
        [sys.executable, str(BASE_DIR / "engine" / "sensemaker_engine.py")],
        capture_output=True,
        text=True,
        cwd=str(BASE_DIR),
    )
    if result.returncode == 0:
        print("[OK] Sensemaker completado")
    else:
        print(f"[ERROR] Sensemaker: {result.stderr[:200]}")


def run_sentiment(data_files):
    """Ejecuta analisis de sentimiento."""
    print("\n[SENTIMIENTO] Analizando sentimiento...")
    result = subprocess.run(
        [sys.executable, str(BASE_DIR / "engine" / "local_sentiment.py")],
        capture_output=True,
        text=True,
        cwd=str(BASE_DIR),
    )
    if result.returncode == 0:
        print("[OK] Analisis de sentimiento completado")
    else:
        print(f"[ERROR] Sentimiento: {result.stderr[:200]}")


def generate_matrix():
    """Genera la Matriz de 4 Cuadrantes."""
    print("\n[MATRIZ] Generando Matriz de Posicionamiento...")

    # Leer datos procesados
    matrix_data = []
    processed_files = list(DATA_PROCESSED.glob("*.json"))

    for f in processed_files:
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
            matrix_data.append(data)

    if matrix_data:
        # Guardar para el dashboard
        matrix_path = DATA_PROCESSED / "matrix_latest.json"
        with open(matrix_path, "w", encoding="utf-8") as f:
            json.dump(matrix_data, f, indent=2, ensure_ascii=False)
        print(f"[OK] Matriz generada: {matrix_path}")
    else:
        print("[INFO] No hay datos procesados aun. Ejecuta primero el Sensemaker.")


def full_pipeline():
    """Pipeline completo: detectar -> convertir -> analizar -> matriz."""
    print("=" * 60)
    print("SAIEL ORCHESTRATOR - Pipeline Completo")
    print(f"Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. Detectar nuevos archivos
    new_files = check_new_data()

    if not new_files:
        print("\n[INFO] No hay archivos 'nuevos', pero ejecutaremos el pipeline con los datos existentes.")
        # return

    # 2. Convertir formato Zeeschuimer
    converted_files = []
    for f in new_files:
        if f.suffix == ".ndjson":
            converted = convert_zeeschuimer(f)
            converted_files.append(converted)

    # 3. Ejecutar Sensemaker
    run_sensemaker(converted_files)

    # 4. Ejecutar analisis de sentimiento
    run_sentiment(converted_files)

    # 5. Generar matriz
    generate_matrix()

    print("\n" + "=" * 60)
    print("[COMPLETADO] Pipeline finalizado.")
    print("Dashboard listo para revision.")
    print("=" * 60)


if __name__ == "__main__":
    full_pipeline()
