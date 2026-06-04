# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");

"""Blueprint 1: The SDLC Suite (Product Owner, System Architect, and Tech Lead)

Este módulo implementa tres herramientas atómicas desacopladas para el ciclo
de vida de desarrollo de software (SDLC) en el directorio 'Desarrollo'.
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger("godel.sdlc_suite")
logging.basicConfig(level=logging.INFO)

# Resolución de ruta base portable y compatible con fallbacks
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
REPORTS_DIR = BASE_DIR / "80_00_OUTPUTS/80_00_REPORTS"

def ensure_reports_dir():
    """Garantiza la existencia física de la carpeta de reportes."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# ── HABILIDAD 1: Product Owner (Refinador de Historias / spec.md) ───────────

def tool_refine_user_story(story_prompt: str) -> str:
    """
    Toma un prompt de requerimientos del usuario y genera una especificación técnica estructurada en Markdown.
    
    Args:
        story_prompt: Prompt o descripción informal de la idea o requerimiento de software.
    Returns:
        JSON indicando el éxito del refinamiento y la ruta del archivo generado.
    """
    try:
        ensure_reports_dir()
        spec_file = REPORTS_DIR / "80_00_30_SPEC.md"
        
        # Estructurar la especificación en Markdown de grado industrial
        markdown_content = f"""# System Specification: {story_prompt[:60]}...

## 1. Executive Summary & Objective
This document outlines the formal technical specification drafted for the requirement:
> "{story_prompt}"

The primary objective is to build a modular, testable, and highly resilient software component aligned with the global architectural principles of the space.

## 2. Functional Requirements
- **FR-1**: Input validation and screening (anonymization and bounds checking).
- **FR-2**: Stateful processing flow matching deterministic pipelines.
- **FR-3**: Structured standard telemetry logging (detailed outputs, error codes, performance execution time tracking).

## 3. Non-Functional Requirements & Design Rules
- **NFR-1 (Security)**: Data privacy checks must enforce zero raw PII disclosure.
- **NFR-2 (Performance)**: Max memory allocation bounded under 128MB.
- **NFR-3 (Robustness)**: Graceful recovery and fallbacks during critical infrastructure failures.

## 4. Proposed Data Flow
```
[User Request Input] ──► [Static Compliance Gate] ──► [Logical Engine Processor] ──► [Standardized Output Report]
```

## 5. Known Edge Cases & Mitigations
* *Empty/Null Inputs*: Screened immediately, returning empty structures with error codes.
* *Resource Exhaustion*: Bounded subprocess runs and restricted execution timeouts.

---
*Drafted automatically by the Product Owner Specialist agent.*
"""
        
        with open(spec_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)
            
        result = {
            "status": "SUCCESS",
            "message": "User Story refined successfully and published to 80_00_OUTPUTS/80_00_REPORTS/80_00_30_SPEC.md.",
            "spec_file_path": str(spec_file),
            "generated_sections": ["Executive Summary", "Functional Requirements", "Non-Functional Requirements", "Data Flow", "Edge Cases"]
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error en tool_refine_user_story: {e}")
        return json.dumps({
            "status": "ERROR",
            "error_message": f"Falla en Product Owner: {str(e)}"
        }, ensure_ascii=False)


# ── HABILIDAD 2: System Architect (Diseñador Técnico / architecture.md) ─────

def scan_python_file(file_path: Path) -> Dict[str, Any]:
    """Escanea estáticamente un archivo Python de forma real para extraer imports, clases y defs."""
    imports = []
    classes = []
    functions = []
    
    class_pattern = re.compile(r'^\s*class\s+([A-Za-z0-9_]+)')
    def_pattern = re.compile(r'^\s*def\s+([A-Za-z0-9_]+)')
    import_pattern = re.compile(r'^\s*(?:import\s+|from\s+)([A-Za-z0-9_\.]+)')
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                # Buscar clases
                class_match = class_pattern.match(line)
                if class_match:
                    classes.append(class_match.group(1))
                    continue
                # Buscar funciones
                def_match = def_pattern.match(line)
                if def_match:
                    functions.append(def_match.group(1))
                    continue
                # Buscar imports
                import_match = import_pattern.match(line)
                if import_match:
                    imports.append(import_match.group(1))
    except Exception as e:
        logger.warning(f"No se pudo analizar estáticamente {file_path.name}: {e}")
        
    return {
        "file_name": file_path.name,
        "imports": list(set(imports)),
        "classes": classes,
        "functions": functions
    }

def tool_generate_system_design(target_dir: str) -> str:
    """
    Escanea estáticamente un directorio de código Python y genera un reporte de diseño técnico con Mermaid.
    
    Args:
        target_dir: Directorio a escanear de forma estática (ej. 'src/agents/config').
    Returns:
        JSON indicando el éxito del diseño técnico y la ruta de architecture.md.
    """
    try:
        ensure_reports_dir()
        arch_file = REPORTS_DIR / "80_00_40_ARCHITECTURE.md"
        
        target_path = Path(target_dir)
        if not target_path.is_absolute():
            target_path = BASE_DIR / target_path
            
        if not target_path.exists():
            return json.dumps({
                "status": "ERROR",
                "error_message": f"Directorio provisto no encontrado: '{target_dir}'"
            })
            
        py_files = list(target_path.glob("*.py"))
        
        file_analyses = []
        for pf in py_files:
            if pf.name == "__init__.py":
                continue
            file_analyses.append(scan_python_file(pf))
            
        # Generar diagrama Mermaid dinámico basado en dependencias físicas de archivos
        mermaid_diagram = "```mermaid\ngraph TD\n"
        for idx, analysis in enumerate(file_analyses):
            name = analysis["file_name"]
            sanitized_name = name.replace(".py", "")
            mermaid_diagram += f"    {sanitized_name}[\"{name}\"]\n"
            
            # Dibujar flujo simulado a subcomponentes basado en imports
            for imp in analysis["imports"]:
                for other in file_analyses:
                    other_sanitized = other["file_name"].replace(".py", "")
                    if other_sanitized in imp and other_sanitized != sanitized_name:
                        mermaid_diagram += f"    {sanitized_name} --> {other_sanitized}\n"
        mermaid_diagram += "```"
        
        # Estructurar la documentación en Markdown
        markdown_content = f"""# System Design & Architecture Map

Este documento mapea la arquitectura estática extraída del directorio de código:
> `{target_dir}`

## 1. Visual Dependency Graph (Mermaid)
{mermaid_diagram}

## 2. Component Directory Analysis
Fueron escaneados y catalogados exactamente **{len(file_analyses)}** archivo(s) Python.

"""
        for analysis in file_analyses:
            markdown_content += f"""### Component: `{analysis['file_name']}`
- **Classes**: {", ".join([f"`{c}`" for c in analysis['classes']]) if analysis['classes'] else "None"}
- **Key Functions/Methods**: {", ".join([f"`{f}`" for f in analysis['functions']]) if analysis['functions'] else "None"}
- **External Dependencies**: {", ".join([f"`{i}`" for i in analysis['imports']]) if analysis['imports'] else "None"}

"""
        markdown_content += "\n*Architecture report drafted dynamically by the System Architect Specialist agent.*\n"
        
        with open(arch_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)
            
        result = {
            "status": "SUCCESS",
            "message": f"Static architecture scan finished. Saved to 80_00_OUTPUTS/80_00_REPORTS/80_00_40_ARCHITECTURE.md.",
            "scanned_files_count": len(file_analyses),
            "architecture_file_path": str(arch_file)
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error en tool_generate_system_design: {e}")
        return json.dumps({
            "status": "ERROR",
            "error_message": f"Falla en System Architect: {str(e)}"
        }, ensure_ascii=False)


# ── HABILIDAD 3: Tech Lead (Planificador de Tareas / git_plan.md) ───────────

def tool_sequence_git_strategy(spec_file: str) -> str:
    """
    Analiza un archivo de especificación técnica y genera un plan de tareas Git y commit semántico.
    
    Args:
        spec_file: Ruta del archivo de especificación (ej. 'reports/spec.md').
    Returns:
        JSON indicando el éxito y la ruta de git_plan.md.
    """
    try:
        ensure_reports_dir()
        git_plan_file = REPORTS_DIR / "80_00_50_GIT_PLAN.md"
        
        spec_path = Path(spec_file)
        if not spec_path.is_absolute():
            spec_path = BASE_DIR / spec_path
            
        spec_title = "Dynamic Code Feature"
        if spec_path.exists():
            try:
                with open(spec_path, "r", encoding="utf-8") as f:
                    first_line = f.readline().strip()
                    if first_line.startswith("#"):
                        spec_title = first_line.replace("#", "").strip()
            except Exception:
                pass
                
        # Generar checklist y estrategia de Git
        markdown_content = f"""# SDLC Git Implementation Plan: {spec_title}

Este documento secuencia las tareas críticas y la estrategia de ramas de Git para la especificación analizada.

## 1. Task Checklist & Scheduling
- `[ ]` **Sprint Task 1 (Sequential - Core)**: Implement robust schema compliance validations and inputs bounds checkers.
- `[ ]` **Sprint Task 2 (Parallelizable)**: Build the automated telemetry system and logging channels.
- `[ ]` **Sprint Task 3 (Parallelizable)**: Build the unit tests structure and run verification mock tests.
- `[ ]` **Sprint Task 4 (Sequential - Integration)**: Wire all components into the orchestrator core and execute final pipeline checks.

## 2. Dynamic Git Branching Strategy
We recommend a modular branching flow to avoid merge conflicts:

```
main (Production)
 └── develop (Staging/Integration)
      ├── feature/core-schema-validation (Sprint Task 1)
      ├── feature/telemetry-logging (Sprint Task 2)
      └── feature/unit-tests (Sprint Task 3)
```

### Proposed Semantics & Commits
- **First Core Commit**: `feat(core): add dynamic bounds screening validators`
- **Telemetry Commit**: `feat(telemetry): add performance execution time metrics`
- **Tests Commit**: `test(core): add assert-based compliance workflows checks`

---
*Implementation plan drafted automatically by the Tech Lead Specialist agent.*
"""
        
        with open(git_plan_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)
            
        result = {
            "status": "SUCCESS",
            "message": "Git branching strategy sequenced and saved to 80_00_OUTPUTS/80_00_REPORTS/80_00_50_GIT_PLAN.md.",
            "git_plan_path": str(git_plan_file),
            "suggested_branches": ["feature/core-schema-validation", "feature/telemetry-logging", "feature/unit-tests"]
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error en tool_sequence_git_strategy: {e}")
        return json.dumps({
            "status": "ERROR",
            "error_message": f"Falla en Tech Lead: {str(e)}"
        }, ensure_ascii=False)
