# 🧠 Manual Cognitivo para IA: Orquestación de Agentes y SDK

Este manual está diseñado exclusivamente para que tú, agente inteligente, asimiles las reglas, estructura y flujos de trabajo de la capa agéntica de este subproyecto.

---

## 🏛️ Filosofía y Reglas de la Capa de Agentes (`src/agents/`)

1.  **Aislamiento del SDK de Antigravity**:
    Toda dependencia o código relacionado con el SDK de Google Antigravity (hooks, REPL interactivo, orquestadores `Agent` y configuraciones MCP) **DEBE** permanecer en esta subcarpeta. No importes el SDK en `/src/core/` ni en `/src/collectors/` para mantener el determinismo y la ligereza matemática.
2.  **Modo Dual del Agente (`godel_agent.py`)**:
    Godel tiene dos modos principales de ejecución que los agentes inteligentes pueden invocar:
    *   **Modo Interactivo (`--sdk`)**: Inicia el bucle REPL de terminal asíncrono con streaming en tiempo real del *Thinking Process* y bitácoras visuales.
    *   **Modo Silencioso de Fondo (`--background`)**: Se ejecuta en segundo plano para procesar tareas programadas o asíncronas de base de datos sin interactuar con el teclado del usuario, volcando el razonamiento paso a paso en `background.log`.

---

## 🛡️ Políticas de Seguridad de Menor Privilegio (`config/security.py`)

Como agente inteligente, estás obligado a respetar las siguientes restricciones en tu flujo de pensamiento:
*   **Zona Permisiva Segura**: Tienes permitido leer, crear y editar archivos de forma transparente y automática dentro de:
    - `/home/fratfn/Desarrollo/Agency/`
    - `/home/fratfn/Desarrollo/Databases/`
*   **Hook Informativo Interactivo (`ask_user`)**: Si necesitas modificar un archivo fuera de estas zonas o ejecutar un comando en terminal con `run_command`, debes planificar tu prompt de forma que expliques en lenguaje amigable e interactivo:
    1.  *Cuál es tu comando o archivo objetivo.*
    2.  *Qué pretendes lograr (tu intención semántica).*
    El hook interceptará la llamada y le presentará este objetivo al usuario en consola pidiendo su autorización `y/n`.

---

## 🔌 Servidor de Herramientas MCP (`config/mcp_servers.py`)

Tu servidor local de herramientas se conecta mediante `stdio` y se define como `secure-mcp` en Python. Te proporciona herramientas de red para consultas a internet que debes priorizar si tu conocimiento local está desactualizado:
*   `perplexity_search(query)`: Búsqueda web avanzada para contexto político y noticias recientes.
*   `fetch_web_page(url)`: Extractor y limpiador de texto de páginas web.
*   `search_huggingface(query)`: Buscador de modelos de IA y datasets políticos.

---

## ⏱️ Diagnóstico Heartbeat (`config/triggers.py`)

Contiene una plantilla inactiva por defecto para una tarea en segundo plano que escribe un log de salud cada 2 horas en `health.log`. Solo habilítalo si es requerido explícitamente por el usuario para monitorear ejecuciones largas de Godel en background.
