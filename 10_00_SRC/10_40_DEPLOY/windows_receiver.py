"""
windows_receiver.py — Monitor de sincronización Drive → Windows
SAIEL · Receptor automático de resultados generados en Parrot OS

Vigila la carpeta data/processed en Google Drive.
Cuando detecta archivos nuevos de Parrot, los procesa y genera:
  - Reporte ejecutivo Markdown
  - Dashboard HTML actualizado
  - Alerta de crisis si aplica

Uso:
    python engine/windows_receiver.py             # Modo monitor continuo
    python engine/windows_receiver.py --once      # Procesar lo que haya ahora
"""

import os
import json
import time
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# ─── RUTAS ────────────────────────────────────────────────────────────────────

from dotenv import load_dotenv
load_dotenv()

DRIVE_DIR      = Path(os.getenv("SAIEL_DRIVE_DIR", "G:/Mi unidad/SAIEL_Inteligencia_Politica"))
LOCAL_DIR      = Path(os.getenv("SAIEL_BASE_PATH", str(Path(__file__).resolve().parents[2])))

DRIVE_PROC     = DRIVE_DIR  / "data/processed"
DRIVE_REPORTS  = DRIVE_DIR  / "reports"

LOCAL_PROC     = LOCAL_DIR  / "data/processed"
LOCAL_REPORTS  = LOCAL_DIR  / "reports"
LOCAL_ENGINE   = LOCAL_DIR  / "src/core"

INTERVALO_SEG  = 30   # Revisar cada 30 segundos

# Archivos que monitoreamos (generados por Parrot)
ARCHIVOS_ESPERADOS = [
    "sentimiento_local.json",
    "resumen_estrategico.md",
    "reporte_industrial_narrativas.json",
]

# ─── ESTADO ───────────────────────────────────────────────────────────────────

archivos_procesados = set()

# ─── FUNCIONES ────────────────────────────────────────────────────────────────

def log(msg: str, nivel: str = "INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    iconos = {"INFO": "ℹ️ ", "OK": "✅", "WARN": "⚠️ ", "ERROR": "❌", "NEW": "🆕"}
    icono = iconos.get(nivel, "  ")
    print(f"[{timestamp}] {icono} {msg}")


def sincronizar_de_drive(archivo_drive: Path) -> Path:
    """Copia un archivo de Drive a la carpeta local de procesados."""
    LOCAL_PROC.mkdir(parents=True, exist_ok=True)
    destino = LOCAL_PROC / archivo_drive.name
    shutil.copy2(str(archivo_drive), str(destino))
    log(f"Sincronizado: {archivo_drive.name} → {destino}", "OK")
    return destino


def verificar_crisis(ruta_json: Path) -> list:
    """Lee un JSON de resultados y detecta alertas de crisis."""
    alertas = []
    try:
        with open(ruta_json, "r", encoding="utf-8") as f:
            datos = json.load(f)

        # Formato reporte sensemaker
        if isinstance(datos, dict):
            alertas_raw = datos.get("alertas_crisis", [])
            alertas.extend(alertas_raw)

        # Formato sentimiento local: calcular % negativo
        elif isinstance(datos, list) and datos:
            total = len(datos)
            negativos = sum(1 for d in datos if d.get("sentimiento") == "negativo")
            pct_negativo = negativos / total * 100
            if pct_negativo > 60:
                alertas.append({
                    "severidad": "ALTA",
                    "mensaje": f"Sentimiento negativo crítico: {pct_negativo:.0f}% ({negativos}/{total} comentarios)"
                })

    except Exception as e:
        log(f"Error leyendo {ruta_json.name}: {e}", "ERROR")

    return alertas


def generar_reporte_express(archivo: Path) -> str:
    """Genera un resumen ejecutivo rápido del archivo recibido."""
    reporte = []
    reporte.append(f"\n{'='*60}")
    reporte.append(f"📊 REPORTE EXPRESS — {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    reporte.append(f"   Archivo: {archivo.name}")
    reporte.append(f"{'='*60}")

    try:
        with open(archivo, "r", encoding="utf-8") as f:
            datos = json.load(f)

        if isinstance(datos, list):
            total = len(datos)
            sentimientos = {}
            temas = {}
            for d in datos:
                s = d.get("sentimiento", "neutro")
                t = d.get("tema", "sin clasificar")
                sentimientos[s] = sentimientos.get(s, 0) + 1
                temas[t] = temas.get(t, 0) + 1

            reporte.append(f"\n  SALUD DIGITAL ({total} comentarios analizados):")
            for s, n in sorted(sentimientos.items(), key=lambda x: -x[1]):
                barra = "█" * int(n / total * 20)
                reporte.append(f"  {s:10} {barra} {n} ({n/total*100:.0f}%)")

            reporte.append(f"\n  TOP TEMAS:")
            for tema, n in sorted(temas.items(), key=lambda x: -x[1])[:5]:
                reporte.append(f"  • {tema:28} {n:3} menciones")

        elif isinstance(datos, dict):
            narrativas = datos.get("narrativas", [])
            reporte.append(f"\n  NARRATIVAS DETECTADAS: {len(narrativas)}")
            reporte.append(f"  Shannon Index: {datos.get('shannon_diversity', 'N/A')}")
            reporte.append(f"  Total comentarios: {datos.get('total_comentarios', 'N/A')}")
            for n in narrativas[:5]:
                pct = n.get("porcentaje", 0)
                sent = n.get("sentimiento_salud", "?")
                reporte.append(f"  #{n.get('id_narrativa', '?')} [{pct}%] {sent}")

    except Exception as e:
        reporte.append(f"  Error leyendo datos: {e}")

    return "\n".join(reporte)


def lanzar_sensemaker_local():
    """Lanza el sensemaker local de Windows si hay datos nuevos."""
    sm_path = LOCAL_ENGINE / "sensemaker_engine.py"
    if sm_path.exists():
        log("Lanzando Sensemaker en Windows...", "INFO")
        try:
            result = subprocess.run(
                ["python", str(sm_path)],
                cwd=str(LOCAL_DIR),
                capture_output=True, text=True,
                timeout=120
            )
            if result.returncode == 0:
                log("Sensemaker completado", "OK")
            else:
                log(f"Sensemaker error: {result.stderr[:100]}", "WARN")
        except subprocess.TimeoutExpired:
            log("Sensemaker timeout (>2 min)", "WARN")
        except Exception as e:
            log(f"Error lanzando sensemaker: {e}", "ERROR")


def procesar_archivo_nuevo(archivo_drive: Path):
    """Procesa un archivo nuevo recibido de Parrot."""
    log(f"Nuevo archivo detectado: {archivo_drive.name}", "NEW")

    # 1. Sincronizar localmente
    archivo_local = sincronizar_de_drive(archivo_drive)

    # 2. Verificar crisis
    if archivo_drive.suffix == ".json":
        alertas = verificar_crisis(archivo_local)
        if alertas:
            print()
            print("  🚨 " + "="*55)
            print("  🚨  ALERTAS DE CRISIS DETECTADAS")
            print("  🚨 " + "="*55)
            for a in alertas:
                print(f"  🚨  [{a.get('severidad', '?')}] {a.get('mensaje', '')}")
            print("  🚨 " + "="*55)
            print()
        else:
            log("Sin alertas de crisis", "OK")

        # 3. Reporte express en consola
        reporte = generar_reporte_express(archivo_local)
        print(reporte)

    # 4. Si es resumen estratégico de Parrot, mostrarlo directamente
    elif archivo_drive.suffix == ".md":
        contenido = archivo_local.read_text(encoding="utf-8")
        print("\n" + "─"*60)
        print("📝 RESUMEN ESTRATÉGICO (generado por SAIEL en Parrot):")
        print("─"*60)
        print(contenido)

    # 5. Copiar también a Drive/reports si aplica
    if "dashboard" in archivo_drive.name.lower() or archivo_drive.suffix == ".html":
        destino_local = LOCAL_REPORTS / archivo_drive.name
        shutil.copy2(str(archivo_drive), str(destino_local))
        log(f"Dashboard copiado a entregables: {destino_local}", "OK")


def escanear_drive() -> list:
    """Busca archivos nuevos en Drive que no hayamos procesado aún."""
    nuevos = []
    if not DRIVE_PROC.exists():
        return nuevos

    for archivo in sorted(DRIVE_PROC.glob("*.json")) + sorted(DRIVE_PROC.glob("*.md")):
        clave = f"{archivo.name}_{archivo.stat().st_mtime}"
        if clave not in archivos_procesados:
            nuevos.append(archivo)
            archivos_procesados.add(clave)

    # También buscar en reports de Drive
    if DRIVE_REPORTS.exists():
        for archivo in sorted(DRIVE_REPORTS.glob("*.html")):
            clave = f"{archivo.name}_{archivo.stat().st_mtime}"
            if clave not in archivos_procesados:
                nuevos.append(archivo)
                archivos_procesados.add(clave)

    return nuevos


def modo_monitor():
    """Modo continuo: vigila Drive y procesa cuando llegan archivos."""
    print("=" * 62)
    print("  🛰️  SAIEL RECEIVER — Monitor de sincronización Drive→Windows")
    print("=" * 62)
    print(f"  📡 Monitoreando: {DRIVE_PROC}")
    print(f"  📁 Local:        {LOCAL_PROC}")
    print(f"  🔄 Intervalo:    {INTERVALO_SEG}s")
    print("=" * 62)
    print()
    print("  Esperando archivos de Parrot... (Ctrl+C para salir)")
    print()

    # Marcar archivos existentes como ya conocidos (no reprocesar)
    for archivo in list(DRIVE_PROC.glob("*.*")) if DRIVE_PROC.exists() else []:
        clave = f"{archivo.name}_{archivo.stat().st_mtime}"
        archivos_procesados.add(clave)
    log(f"{len(archivos_procesados)} archivos existentes marcados (no se reprocesarán)", "INFO")

    ciclo = 0
    try:
        while True:
            ciclo += 1
            nuevos = escanear_drive()
            if nuevos:
                log(f"{len(nuevos)} archivo(s) nuevo(s) de Parrot!", "NEW")
                for archivo in nuevos:
                    procesar_archivo_nuevo(archivo)
            else:
                if ciclo % 4 == 0:  # Log cada 2 minutos
                    log(f"Sin cambios. Esperando... (ciclo #{ciclo})", "INFO")

            time.sleep(INTERVALO_SEG)

    except KeyboardInterrupt:
        print("\n\n  Monitor detenido.")


def modo_once():
    """Procesa todos los archivos disponibles ahora mismo."""
    print("=" * 62)
    print("  📊 SAIEL RECEIVER — Procesando archivos actuales")
    print("=" * 62)

    archivos = []
    if DRIVE_PROC.exists():
        archivos += list(DRIVE_PROC.glob("*.json"))
        archivos += list(DRIVE_PROC.glob("*.md"))

    if not archivos:
        log("No hay archivos en Drive todavía. Parrot aún no ha sincronizado.", "WARN")
        return

    log(f"{len(archivos)} archivos encontrados", "OK")
    for archivo in archivos:
        procesar_archivo_nuevo(archivo)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor de sincronización Drive→Windows")
    parser.add_argument("--once", action="store_true",
                        help="Procesar archivos actuales y salir (sin monitor continuo)")
    args = parser.parse_args()

    if args.once:
        modo_once()
    else:
        modo_monitor()
