# 🧠 Manual Cognitivo Maestro: Sistema de Inteligencia Electoral Local (Godel/SAIEL)

Este manual sirve como punto de entrada de especificación declarativa para ti, el agente inteligente que opera en este repositorio. Su propósito es guiarte de forma autónoma en el desarrollo, mantenimiento y ejecución del sistema sin corromper el diseño arquitectónico ni las políticas de seguridad.

---

## 📐 Estructura del Repositorio y Manuales Secundarios

El repositorio se divide en tres capas bien definidas, cada una con su propio manual cognitivo detallado. Estás obligado a consultar el manual correspondiente antes de editar código en su respectiva sección:

1.  👉 **[Manual de Orquestación y Capa Agéntica](src/agents/agent.md)**:
    *   **Directorio**: `src/agents/`
    *   **Propósito**: Gestión del ciclo de vida del SDK de Google Antigravity, orquestación interactiva, REPL, triggers y hooks de seguridad.
2.  👉 **[Manual del Núcleo Analítico y Procesamiento](src/core/agent.md)**:
    *   **Directorio**: `src/core/`
    *   **Propósito**: Módulos ETL matemáticos y de procesamiento en Polars (cálculo de sentimiento, sensemaker y tubería PDIV). Es 100% determinista y aislado del SDK de agentes.
3.  👉 **[Manual de Recopilación de Datos](src/collectors/agent.md)**:
    *   **Directorio**: `src/collectors/`
    *   **Propósito**: Conectores para la API de Apify para descargar datos brutos de redes sociales públicos.

---

## 🛠️ Inicio Rápido para Agentes de IA

Si deseas ejecutar o probar componentes del sistema, utiliza los siguientes comandos estándar (asegurando el uso del entorno virtual configurado):

### 1. Ejecutar el Agente Godel en Modo SDK (Interactividad Completa)
```bash
/home/fratfn/vertex_env/bin/python src/agents/godel_agent.py --sdk
```

### 2. Ejecutar el Agente en Segundo Plano (Procesamiento Silencioso)
```bash
/home/fratfn/vertex_env/bin/python src/agents/godel_agent.py --background
```

### 3. Ejecutar Pruebas Automatizadas
*   **Pruebas de Seguridad**:
    ```bash
    /home/fratfn/vertex_env/bin/python src/agents/test_agent_security.py
    ```
*   **Pruebas de Patrones de Diseño**:
    ```bash
    /home/fratfn/vertex_env/bin/python src/agents/test_patterns.py
    ```

---

## 🛡️ Políticas Clave de Seguridad y Desarrollo

Como agente autónomo en este repositorio, debes cumplir estrictamente las siguientes reglas:
*   **Menor Privilegio**: Solo tienes permitido escribir y modificar archivos de forma automática dentro de la carpeta del proyecto `Agency/` y del directorio local `Databases/`. Para cualquier acción que involucre ejecutar comandos del sistema fuera de este ámbito, debes solicitar autorización explícita explicando tu objetivo semántico al usuario.
*   **Aislamiento del Entorno**: Nunca expongas claves de API (`GEMINI_API_KEY`, `APIFY_TOKEN`) en el código. Lee siempre la configuración utilizando `python-dotenv` y delega la gestión de secretos al entorno.
*   **Independencia de godel-core**: El repositorio utiliza adaptadores dinámicos que buscan la carpeta compartida hermana `godel-core` o la leen mediante la variable de entorno `GODEL_CORE_PATH`. No intentes hardcodear rutas físicas que apunten a `/home/fratfn/`.
