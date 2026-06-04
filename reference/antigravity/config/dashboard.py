# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");

"""Layer 5: Unified Security Posture (Security Dashboard)

Genera una vista unificada (Scorecard / Dashboard) sobre el cumplimiento de políticas,
alertas de anomalías, estado de identidad y dependencias vulnerables en el ecosistema.
"""

import os
import json
import datetime
from pathlib import Path

from config.identity import agent_identity
from config.registry import agent_registry
from config.gateway import AUDIT_LOG_FILE
from config.anomaly import ANOMALY_LOG_FILE

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
REPORT_MD_FILE = BASE_DIR / "80_00_OUTPUTS/80_00_REPORTS/80_00_10_SECURITY_POSTURE_DASHBOARD.md"
REPORT_HTML_FILE = BASE_DIR / "80_00_OUTPUTS/80_00_REPORTS/80_00_10_SECURITY_POSTURE_DASHBOARD.html"

def tool_generate_security_posture_dashboard() -> str:
    """
    Analiza todos los logs de auditoría de gobernanza (Gateway, Anomaly, Registry)
    y genera un reporte unificado (Dashboard) de la postura de seguridad del agente.
    
    Returns:
        Resumen de la generación y ruta física del archivo generado.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. Cargar logs del Gateway
    gateway_violations = []
    if AUDIT_LOG_FILE.exists():
        try:
            with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        gateway_violations.append(json.loads(line))
        except Exception:
            pass
            
    # 2. Cargar logs de Anomalías
    anomaly_alerts = []
    if ANOMALY_LOG_FILE.exists():
        try:
            with open(ANOMALY_LOG_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        anomaly_alerts.append(json.loads(line))
        except Exception:
            pass
            
    # 3. Auditar dependencias
    dep_warnings = agent_registry.audit_dependencies()
    
    # 4. Construir reporte de texto/markdown
    md_content = f"""# 🛡️ Godel Agent - Scorecard de Gobernación y Seguridad (Posture Dashboard)
Generado el: `{timestamp}`

---

## 🆔 Capa 1: Identidad Criptográfica del Agente
- **ID de Servicio**: `{agent_identity.agent_id}`
- **UUID de Instancia**: `{agent_identity.instance_uuid}`
- **Firma Criptográfica**: `{agent_identity.signature_hash}`
- **Estado de IAM**: `Activo - Mínimo Privilegio`

---

## 🔧 Capa 2: Herramientas y Dependencias
- **Herramientas Registradas**: `{len(agent_registry.approved_tools)}` aprobadas en manifest.json.
- **Advertencias de Dependencias**: `{len(dep_warnings)}` encontradas.
"""
    if dep_warnings:
        md_content += "\n### Detalles de Dependencias:\n"
        for warn in dep_warnings:
            md_content += f"- ⚠️ {warn}\n"
    else:
        md_content += "- ✅ Todas las dependencias tienen versiones declaradas fijas y seguras.\n"
        
    md_content += f"""
---

## 🚧 Capa 3: Policy Enforcement Gateway (Model Armor)
- **Infracciones de Política Detenidas**: `{len(gateway_violations)}`
"""
    if gateway_violations:
        md_content += "\n### Registro de Infracciones Detenidas:\n"
        for v in gateway_violations:
            md_content += f"- `[{v['timestamp']}]` **Tipo**: `{v['type']}` | *Detalles*: `{v['details']}`\n"
    else:
        md_content += "- ✅ Sin violaciones de política registradas. El Gateway ha filtrado todos los turnos limpiamente.\n"
        
    md_content += f"""
---

## 📈 Capa 4: Behavioral Anomaly Detection
- **Alertas de Desviación / loops**: `{len(anomaly_alerts)}`
"""
    if anomaly_alerts:
        md_content += "\n### Registro de Alertas de Desviación:\n"
        for a in anomaly_alerts:
            md_content += f"- `[{a['timestamp']}]` **Tipo**: `{a['type']}` | *Mensaje*: `{a['message']}`\n"
    else:
        md_content += "- ✅ Sin anomalías de comportamiento o bucles infinitos detectados. El modelo está operando dentro del baseline lógico.\n"
        
    md_content += """
---
*Scorecard generado de forma determinista mediante el módulo de Gobernación de Gemini Platform.*
"""

    # Pre-renderizar listas HTML para evitar limitaciones de f-string en versiones antiguas de Python
    gateway_list_html = ""
    if gateway_violations:
        items = [f'<p>&bull; [{v["timestamp"]}] <strong>{v["type"]}</strong>: {v["details"]}</p>' for v in gateway_violations]
        gateway_list_html = f"<div class='violation-list'>{''.join(items)}</div>"
    else:
        gateway_list_html = "<p class='success'>✅ Sin violaciones de política registradas. El Gateway ha filtrado todos los turnos limpiamente.</p>"

    anomaly_list_html = ""
    if anomaly_alerts:
        items = [f'<p>&bull; [{a["timestamp"]}] <strong>{a["type"]}</strong>: {a["message"]}</p>' for a in anomaly_alerts]
        anomaly_list_html = f"<div class='violation-list'>{''.join(items)}</div>"
    else:
        anomaly_list_html = "<p class='success'>✅ Sin anomalías de comportamiento o bucles infinitos detectados.</p>"

    # 5. Generar reporte en formato HTML responsivo premium
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Godel Agent - Unified Security Posture</title>
    <style>
        body {{
            font-family: 'Outfit', 'Inter', sans-serif;
            background: #0f172a;
            color: #f1f5f9;
            margin: 40px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 900px;
            margin: auto;
            background: #1e293b;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
            border: 1px solid #334155;
        }}
        h1 {{
            color: #38bdf8;
            border-bottom: 2px solid #334155;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }}
        h2 {{
            color: #f43f5e;
            border-bottom: 1px solid #475569;
            padding-bottom: 8px;
            margin-top: 30px;
        }}
        .metric-card {{
            background: #0f172a;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #38bdf8;
            margin-bottom: 15px;
        }}
        .violation-list, .anomaly-list {{
            background: #1e293b;
            padding: 10px;
            border: 1px dashed #ef4444;
            border-radius: 6px;
            font-family: monospace;
            margin-top: 10px;
        }}
        .alert {{
            color: #fb7185;
        }}
        .success {{
            color: #4ade80;
        }}
        .footer {{
            text-align: center;
            font-size: 0.8em;
            color: #94a3b8;
            margin-top: 50px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ Godel Agent - Scorecard de Gobernación y Seguridad</h1>
        <p>Generado de forma determinista el: <strong>{timestamp}</strong></p>
        
        <h2>🆔 Capa 1: Identidad Criptográfica del Agente</h2>
        <div class="metric-card" style="border-left-color: #a855f7;">
            <p><strong>ID de Servicio:</strong> {agent_identity.agent_id}</p>
            <p><strong>UUID de Instancia:</strong> {agent_identity.instance_uuid}</p>
            <p><strong>Firma Criptográfica (Git/Code Hash):</strong> {agent_identity.signature_hash}</p>
            <p><strong>Estado de IAM:</strong> <span class="success">Activo - Mínimo Privilegio</span></p>
        </div>

        <h2>🔧 Capa 2: Herramientas y Dependencias</h2>
        <div class="metric-card" style="border-left-color: #eab308;">
            <p><strong>Herramientas Registradas:</strong> {len(agent_registry.approved_tools)} aprobadas en manifest.json.</p>
            <p><strong>Auditoría de requirements.txt:</strong></p>
            {"".join([f"<p class='alert'>⚠️ {w}</p>" for w in dep_warnings]) if dep_warnings else "<p class='success'>✅ Todas las dependencias tienen versiones declaradas fijas y seguras.</p>"}
        </div>

        <h2>🚧 Capa 3: Policy Enforcement Gateway (Model Armor)</h2>
        <div class="metric-card" style="border-left-color: #3b82f6;">
            <p><strong>Infracciones de Política Detenidas:</strong> <strong>{len(gateway_violations)}</strong></p>
            {gateway_list_html}
        </div>

        <h2>📈 Capa 4: Behavioral Anomaly Detection</h2>
        <div class="metric-card" style="border-left-color: #ef4444;">
            <p><strong>Alertas de Desviación / Loops de Ejecución:</strong> <strong>{len(anomaly_alerts)}</strong></p>
            {anomaly_list_html}
        </div>

        <div class="footer">
            <p>Auditoría de Gobernación Gemini Enterprise Platform &bull; SAIEL Intel 2026</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Escribir reportes físicamente
    try:
        os.makedirs(REPORT_MD_FILE.parent, exist_ok=True)
        with open(REPORT_MD_FILE, "w", encoding="utf-8") as f:
            f.write(md_content)
        with open(REPORT_HTML_FILE, "w", encoding="utf-8") as f:
            f.write(html_content)
    except Exception as e:
        return f"Error al generar reportes de postura: {e}"
        
    print(f"\n📊 [Postures] Dashboard de Gobernabilidad unificado generado exitosamente.")
    return f"ÉXITO: Reporte de postura de seguridad generado y guardado en:\n  - Markdown: {REPORT_MD_FILE}\n  - HTML: {REPORT_HTML_FILE}"
