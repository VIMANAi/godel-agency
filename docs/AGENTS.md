# Gobernanza de Agentes - SAIEL Agentic Layer

Este documento describe la especificación técnica de la capa de agentes de **SAIEL** (Sistema de Análisis de Inteligencia Electoral Local) en apego a los estándares del **Google Antigravity SDK** y los principios de modularidad y trazabilidad del proyecto.

---

## 🤖 El Agente SAIEL (`saiel_agent`)

El agente principal de SAIEL es un **Asistente de Inteligencia Política** diseñado específicamente para operar en contiendas electorales locales (municipio de Tepic, Nayarit). Su propósito es actuar como puente conversacional en lenguaje natural y orquestar el flujo de datos desde la recolección hasta la modelación probabilística de Monte Carlo.

### 🎭 Persona y Directrices
*   **Nombre:** SAIEL Intelligence Agent
*   **Rol:** Analista Político Senior y Consultor de Estrategia Electoral para Nayarit.
*   **Tono:** Profesional, técnico, objetivo, discreto y riguroso estadísticamente.
*   **Principio de Operación:** Nunca emite juicios de valor basados en intuiciones; todo reporte estratégico debe sustentarse sobre los scores normalizados del PDIV (Componentes P, D, I, V), la matriz de posicionamiento de cuadrantes, o las estimaciones de incertidumbre del simulador probabilístico.

---

## ⚙️ Especificación del Motor (Engines)

El agente está diseñado bajo un modelo **Dual-Engine** para garantizar resiliencia y flexibilidad:

```
                      ┌──────────────────────┐
                      │    Conversación CLI  │
                      └──────────┬───────────┘
                                 ▼
                 ┌───────────────────────────────┐
                 │     Orquestador Principal     │
                 └───────────────┬───────────────┘
                                 │
                ┌────────────────┴────────────────┐
                ▼                                 ▼
   ┌──────────────────────────┐      ┌──────────────────────────┐
   │     Bunker Local         │      │     Cloud Inferencia     │
   │  Ollama / DeepSeek-R1    │      │  OpenRouter / Gemma-2    │
   │  (100% Offline / Seguro) │      │  (Alta precisión/API)    │
   └──────────────────────────┘      └──────────────────────────┘
```

1. **Endpoint Inferencia (Por defecto - API):** Se conecta a **OpenRouter** para utilizar modelos altamente precisos como `google/gemma-2-9b-it:free` para análisis contextual profundo, extracción de temas semánticos de comentarios y respuestas analíticas.
2. **Bunker Local (Fallback):** Utiliza una instancia local de **Ollama** con el modelo `deepseek-r1:7b` para razonamiento avanzado y estructurado directamente en el entorno de cómputo del cliente (sin necesidad de internet).

---

## 🛠️ Catálogo de Herramientas (Tools)

El agente tiene a su disposición 5 herramientas modulares en `src/` asociadas al pipeline procedimental:

| Nombre de la Herramienta | Módulo del Código | Acción Técnica Realizada |
| :--- | :--- | :--- |
| `tool_collect_data` | `src/collectors/social_collector.py` | Llama al scraper Playwright/httpx para extraer comentarios de candidatos de Tepic. |
| `tool_run_data_ingestion` | `src/core/data_ingestion.py` | Ejecuta el pipeline ETL de curación, tokenización sklearn y redacción de CURP/INE. |
| `tool_run_pdiv_pipeline` | `src/core/pdiv_calculator.py` | Orquesta los scores P, D, I, V y genera la matriz de posicionamiento del candidato. |
| `tool_run_sensemaker` | `src/core/sensemaker_engine.py` | Ejecuta agrupamiento DBSCAN para identificar temas de debate y narrativas ciudadanas. |
| `tool_check_crisis` | `src/agents/saiel_agent.py` | Analiza picos repentinos de sentimiento negativo para lanzar alertas inmediatas. |

---

## 📋 Manifiesto de Configuración (`manifest.json`)

El agente se configura dinámicamente utilizando el manifiesto ubicado en [manifest.json](file:///home/fratfn/Desarrollo/Agency/src/agents/manifest.json). El manifiesto declara formalmente las dependencias de los módulos, las variables de entorno requeridas y las capacidades autorizadas del agente, sirviendo como contrato de integración para el sistema.

---

## 🔄 Orquestación de Tareas (TASK Flow)

En lugar de delegaciones caóticas o bucles de inferencia descontrolados que consumen recursos, el agente sigue un flujo secuencial asíncrono y procedimental:

1. **Recepción del Input:** El usuario introduce una consulta ("¿Cuál es la situación actual en Tepic?").
2. **Razonamiento y Selección de Herramienta:** El agente evalúa si cuenta con datos procesados recientes.
   *   Si los datos están obsoletos o no existen: Ejecuta secuencialmente `collect_data` -> `ingest_data` -> `calculate_pdiv`.
   *   Si existen datos frescos: Consulta la base de datos local SQLite para responder instantáneamente.
3. **Ejecución Asíncrona:** Las herramientas corren en procesos locales parametrizados, notificando al agente al finalizar y registrando la firma de tiempo en el log de procedencia.
4. **Generación del Entregable:** El agente compila la matriz de cuadrantes en HTML o markdown y la presenta al usuario final junto con el análisis de probabilidades del Simulador de Monte Carlo.
