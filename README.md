# Godel — Sistema de Análisis de Inteligencia Electoral Local

**Versión Activa:** `2.0` | **Estado:** Producción | **Última Refactorización:** 2026-05-31
**Compliance:** LGPDPPSO · GDPR · Berkeley Protocol · EU AI Act

Sistema de war room digital de análisis político multicanal con motor de orquestación dual y soporte para agentes autónomos seguros.

---

## 📐 Arquitectura del Proyecto

```
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

## 🚀 Inicio Rápido

```bash
# 1. Clonar y configurar el entorno
git clone <repo> && cd Agency
cp .env.example .env   # Editar con tus credenciales reales

# 2. Configurar el entorno virtual e instalar dependencias con uv
/home/fratfn/.local/bin/uv pip install -r requirements.txt --python /home/fratfn/vertex_env

# 3a. Modo SDK Avanzado (Google Antigravity + secure-mcp + Bucle Premium)
# Te da streaming en tiempo real del Thinking Process y políticas interactivas de seguridad.
/home/fratfn/vertex_env/bin/python src/agents/godel_agent.py --sdk

# 3b. Modo Background Silencioso (Segunda plano sin interfaz de terminal)
/home/fratfn/vertex_env/bin/python src/agents/godel_agent.py --background

# 3c. Modo Clásico (Ollama Local / Reglas Sincrónicas)
/home/fratfn/vertex_env/bin/python src/agents/godel_agent.py

# 4. Ejecutar suite de pruebas de seguridad
/home/fratfn/vertex_env/bin/python src/agents/test_agent_security.py
```

---

## 🔒 Modos de Operación (Consola / SDK)

| Característica | Modo SDK Avanzado (`--sdk`) | Modo Clásico |
|---|---|---|
| **Motor de Orquestación** | Google Antigravity SDK | Reglas / Ollama (DeepSeek-R1) |
| **Bucle de Terminal** | REPL asíncrono premium con streaming de pensamiento | Bucle clásico de entrada de consola |
| **Herramientas Externas** | secure-mcp (Perplexity Search, HF, fetch) | Solo herramientas locales de Python |
| **Seguridad Activa** | Hooks interactivos que detallan objetivos del agente | Ejecución silenciosa libre |
| **Consumo de RAM** | <65 MB de RAM (Conexión stdio ultra-ligera) | >150 MB de RAM (Ollama local activo) |

---

## 📚 Documentación

- [Estándar Dual Local/Cloud](docs/governance/ESTANDAR_DUAL_LOCAL_CLOUD.md)
- [Manual Técnico Operativo](docs/manuals/INSTRUCCIONES_TECNICAS.md)
- [Workflow y Metodología](docs/research/WORKFLOW_ADOPTED.md)
- [Documentación Técnica PDIV](docs/research/PDIV_TECHNICAL_DOCS.md)
- [Guía de Base de Datos](data/db/README.md)
- [Registro de Procedencia (Provenance)](archive/PROVENANCE.md)

---

*Sistema desarrollado con metodología MCP Sequential Thinking · Gobernanza Técnica Godel*
