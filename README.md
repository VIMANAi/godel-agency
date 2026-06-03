# Godel — Sistema de Análisis de Inteligencia Electoral Local

**Versión Activa:** `2.0` | **Estado:** Producción | **Última Refactorización:** 2026-05-31  
**Compliance:** LGPDPPSO · GDPR · Berkeley Protocol · EU AI Act

Sistema de war room digital de análisis político multicanal con motor de orquestación dual y soporte para agentes autónomos seguros. El flujo principal se basa en la **Recolección (Scrapers OSINT)**, **Análisis (ETL, Sentimiento, PDIV)**, y **Generación de Reportes**.

---

## 📐 Arquitectura del Proyecto

```text
Agency/
├── src/
│   ├── core/          # Motores analíticos ETL (pipeline PDIV, sentimiento, sensemaker)
│   │   └── agent.md   # Manual Cognitivo: Módulos de datos y análisis para IA
│   ├── agents/        # Capa agéntica y orquestadores asíncronos del sistema
│   │   ├── agent.md   # Manual Cognitivo: Orquestación del SDK y seguridad para IA
│   │   ├── config/    # Configuraciones modulares (Seguridad, MCP y Triggers)
│   │   └── godel_agent.py # Orquestador (Modo Clásico + Modo SDK Avanzado)
│   ├── collectors/    # Scrapers OSINT (Apify, Instagram, Facebook)
│   │   └── agent.md   # Manual Cognitivo: Recolector Apify para IA
│   ├── tests/         # Suite de pruebas de integración
│   └── deploy/        # Docker, Cloud Run, scripts de inicio
├── data/
│   ├── raw/           # Datasets crudos (.jsonl / .json)
│   ├── processed/     # Datos anonimizados y validados
│   └── db/            # SQLite local + schema + guía BigQuery
├── docs/
│   ├── governance/    # Estándares, auditoría, guías de IA
│   ├── manuals/       # Manuales operativos de ingeniería
│   └── research/      # Estrategia, flujos, investigación política
├── reports/           # Dashboards HTML y reportes ejecutivos
├── archive/           # Legado histórico + PROVENANCE.md
├── .env.example       # Plantilla de configuración (copiar como .env)
└── requirements.txt   # Dependencias del ecosistema completo
```

---

## 🤖 Manuales Cognitivos para Agentes de IA

Para acelerar el desarrollo colaborativo y guiar el comportamiento autónomo de los agentes inteligentes que operen en este repositorio, hemos desplegado una red de especificaciones declarativas:
1.  👉 **[Manual del Agente (Agents)](src/agents/agent.md)**: Directrices del ciclo de vida del SDK de Antigravity, MCP locales y hooks interactivos de seguridad.
2.  👉 **[Manual Analítico (Core)](src/core/agent.md)**: Guía de imports y funciones matemáticas deterministas (sentimiento, narrativas, PDIV).
3.  👉 **[Manual de Recolección (Collectors)](src/collectors/agent.md)**: API del social collector de Apify.

---

## 📋 Requisitos Previos (Prerequisites)

*   **Python**: 3.10 o superior.
*   **Gestor de paquetes**: Recomendamos usar `uv` o `pip`.
*   **Ollama**: (Opcional) Requerido si planeas usar el Modo Clásico localmente.
*   **Credenciales**: Es necesario contar con los tokens para herramientas externas (Ej: Apify para recolección de datos, API keys para LLMs).

---

## 🚀 Inicio Rápido

```bash
# 1. Clonar el repositorio y configurar el entorno
git clone <repo> && cd Agency
cp .env.example .env   # Editar con tus credenciales reales (API keys, etc.)

# 2. Crear entorno virtual e instalar dependencias
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt  # O usando uv: uv pip install -r requirements.txt

# 3. Ejecución del orquestador:

# 3a. Modo SDK Avanzado (Google Antigravity + secure-mcp + Bucle Premium)
# Te da streaming en tiempo real del Thinking Process y políticas interactivas de seguridad.
python src/agents/godel_agent.py --sdk

# 3b. Modo Background Silencioso (Segundo plano sin interfaz de terminal)
# Útil para ejecuciones programadas o servicios que no requieren interacción humana.
python src/agents/godel_agent.py --background

# 3c. Modo Clásico (Ollama Local / Reglas Sincrónicas)
# Requiere que el servicio de Ollama esté ejecutándose.
python src/agents/godel_agent.py

# 4. Ejecutar suite de pruebas de seguridad
python src/agents/test_agent_security.py
```

---

## 🔒 Modos de Operación (Consola / SDK)

| Característica | Modo SDK Avanzado (`--sdk`) | Modo Background (`--background`) | Modo Clásico (Sin flags) |
|---|---|---|---|
| **Motor de Orquestación** | Google Antigravity SDK | Google Antigravity SDK | Reglas / Ollama (DeepSeek-R1) |
| **Bucle de Terminal** | REPL asíncrono premium con streaming de pensamiento | Ninguno (Ejecución silenciosa) | Bucle clásico de entrada de consola |
| **Herramientas Externas** | secure-mcp (Perplexity Search, HF, fetch) | secure-mcp | Solo herramientas locales de Python |
| **Seguridad Activa** | Hooks interactivos que detallan objetivos del agente | Políticas pre-aprobadas o logs de auditoría | Ejecución libre / restringida por reglas |
| **Consumo de RAM** | <65 MB de RAM (Conexión stdio ultra-ligera) | <65 MB de RAM | >150 MB de RAM + VRAM (Ollama local activo) |

---

## 🤝 Cómo Contribuir (Contributing)

Para nuevos desarrolladores y colaboradores, por favor sigue este flujo de trabajo:
1. Revisa los **Manuales Cognitivos** (`agent.md`) ubicados en cada subdirectorio (`src/agents`, `src/core`, `src/collectors`) para entender las reglas, estándares y arquitectura de esa sección específica.
2. Asegúrate de configurar correctamente tu entorno virtual y el archivo `.env`.
3. Ejecuta las pruebas de seguridad con `python src/agents/test_agent_security.py` antes de realizar un commit para asegurar el cumplimiento (compliance).
4. Consulta nuestra [Gobernanza Técnica y Auditoría](docs/governance/ESTANDAR_DUAL_LOCAL_CLOUD.md) para más detalles.

---

## 📚 Documentación Adicional

- [Estándar Dual Local/Cloud](docs/governance/ESTANDAR_DUAL_LOCAL_CLOUD.md)
- [Manual Técnico Operativo](docs/manuals/INSTRUCCIONES_TECNICAS.md)
- [Workflow y Metodología](docs/research/WORKFLOW_ADOPTED.md)
- [Documentación Técnica PDIV](docs/research/PDIV_TECHNICAL_DOCS.md)
- [Guía de Base de Datos](data/db/README.md)
- [Registro de Procedencia (Provenance)](archive/PROVENANCE.md)

---

*Sistema desarrollado con metodología MCP Sequential Thinking · Gobernanza Técnica Godel*
