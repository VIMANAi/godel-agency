# Standard Operating Procedure (SOP): Architecture, Governance & MLOps Standards

Este documento formal establece el plano de cumplimiento oficial (Source of Truth) y los estándares de ingeniería aplicados en el ecosistema global de agentes `Agency` dentro del espacio de trabajo `/home/fratfn/Desarrollo/`.

---

## 🏛️ Pilar 1: Separation of Concerns (SoC) en Arquitectura de Agentes

El principio de **Separación de Responsabilidades (Separation of Concerns - SoC)** es la base estructural del Core Engine. Prohíbe de forma estricta el acoplamiento monolítico y el desvío de responsabilidades en la flota de agentes:

```
                  ┌───────────────────────────────────────────────┐
                  │                 USER / CLI                    │
                  └───────────────────────┬───────────────────────┘
                                          │
                                          ▼
                  ┌───────────────────────────────────────────────┐
                  │       Core Engine (godel_agent.py)            │
                  └───────────────────────┬───────────────────────┘
                                          │ (Inyección de Manifiesto)
                                          ▼
     ┌────────────────────────────────────┼────────────────────────────────────┐
     │                                    │                                    │
     ▼                                    ▼                                    ▼
┌────────────────────────┐          ┌────────────────────────┐          ┌────────────────────────┐
│     Security Hooks     │          │   Specialist Workers   │          │   Dynamic Workflows    │
│  (security.py/gateway) │          │    (sdlc_suite.py)     │          │ (workflow/composer.py) │
└────────────────────────┘          └────────────────────────┘          └────────────────────────┘
```

1. **Core Engine (`godel_agent.py`)**: 
   * **Responsabilidad**: Orquestar el ciclo de vida de la sesión (Checkpoint-and-Resume), interactuar con el SDK de Google Antigravity, y servir de router agnóstico.
   * **Regla de Diseño**: No debe contener lógica de negocio específica de ningún dominio (ej. sin palabras clave de política mexicana, sin CURP/INE hardcodeados). Se alimenta dinámicamente de dependencias externas.
2. **Security & Governance Layer (`security.py`, `gateway.py`, `registry.py`)**:
   * **Responsabilidad**: Interceptar, auditar e interceptar las llamadas a herramientas.
   * **Regla de Diseño**: Las capas automáticas y silenciosas (bloqueo horacio, shadow AI) se ejecutan de manera aislada antes de delegar en el hook descriptivo interactivo del operador.
3. **Specialist Workers (`sdlc_suite.py`, `social_collector.py`)**:
   * **Responsabilidad**: Ejecutar acciones técnicas acotadas e independientes.
   * **Regla de Diseño**: Cada especialista opera como una "unidad atómica" aislada. Ningún worker puede acceder directamente a herramientas o memoria fuera de su alcance aprobado en `agent_manifest.json`.

---

## 🧬 Pilar 2: The 12-Factor App Compliance Matrix

Alineamos nuestra infraestructura portable a la metodología Cloud-Native de los **12 Factores**, adaptando cada pilar a los sistemas agénticos modernos:

| Factor | Concepto | Cumplimiento Físico en `Desarrollo/Agency` |
| :--- | :--- | :--- |
| **1. Codebase** | Un repositorio, múltiples despliegues | El código reside en un repositorio Git portable con base relativa. Se despliega idénticamente de local a Vertex AI. |
| **2. Dependencies** | Declaración y aislamiento explícito | Entorno virtual ultra-hermético (`vertex_env`) y control en `requirements.txt`. El Registry (`registry.py`) escanea y advierte dependencias no fijadas. |
| **3. Config** | Configuración en el entorno | Bóveda segura de variables de entorno en `/home/fratfn/vertex_env/.env` y carga dinámica portable de rutas. |
| **4. Backing Services** | Recursos de apoyo desacoplados | La base de datos SQLite y ChromaDB se tratan como recursos externos vinculados dinámicamente vía config sin dependencias de red rígidas. |
| **5. Build, Release, Run** | Separación estricta de fases | El MLOps pipeline separa la compilación del manifiesto (Build), el empaquetado del agente con variables (Release), y la ejecución asíncrona en daemon (Run). |
| **6. Processes** | Ejecución sin estado (Stateless) | El Core asume procesos sin estado. La persistencia se delega en backing stores externos (SQLite / JSON Bank). |
| **7. Port Binding** | Exportación de servicios vía puertos | N/A para scripts de consola, pero compatible en despliegues API de Vertex AI que exponen endpoints REST seguros. |
| **8. Concurrency** | Escalabilidad vía modelo de procesos | Ejecución asíncrona nativa (`asyncio`) y subprocesos aislados en Sandboxes paralelos sin colisiones de memoria. |
| **9. Disposability** | Robustez vía despegues rápidos | El inicio y parada rápidos son inmediatos. Checkpoint-and-Resume recupera la cadena de razonamiento exacta tras apagados abruptos. |
| **10. Dev/Prod Parity** | Paridad desarrollo/producción | Los adaptadores de Vertex AI garantizan que el mismo modelo e inferencia local en SDK corran de forma idéntica en GCP. |
| **11. Logs** | Logs como streams de eventos | El motor vuelca telemetría en tiempo real (`background.log`, `health.log`, `gateway_audit.jsonl`), tratando la salida estándar como streams para colectores externos. |
| **12. Admin Processes** | Tareas de administración puntuales | Scripts de verificación aislados (`test_governance.py`, `test_sdlc_suite.py`) que corren de forma independiente en el mismo entorno virtual. |

---

## 🚀 Pilar 3: MLOps vs. DevOps CI/CD/CD Pipelines

El ecosistema de agentes se rige por un pipeline de **Integración Continua, Entrega Continua y Despliegue Continuo (CI/CD/CD)** que separa la automatización de infraestructura clásica (DevOps) de la validación cognitiva de los datos (MLOps):

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           DevOps Pipeline (CI/CD)                       │
│  [Code Push] ──► [Static Lint/Checks] ──► [Registry Approved Scan] ──►   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           MLOps Pipeline (CD)                           │
│  ──► [Impact Assessment in SQLite] ──► [Deploy to Vertex AI Engine GCP] │
└─────────────────────────────────────────────────────────────────────────┘
```

### A. DevOps (Integración de Software)
1. **Auditoría Estática**: Todo commit activa el escáner del System Architect (`tool_generate_system_design`) para verificar dependencias de componentes físicos.
2. **Validación de Gobernabilidad**: El `AgentRegistry` bloquea despliegues si se detecta uso de capacidades de "Shadow AI" no registradas en `manifest.json`.

### B. MLOps (Evaluación de Impacto Lógico)
1. **Impact Assessment Protocol**:
   * Cualquier cambio en prompts, pesos del LLM o reglas de comportamiento político/ETL se prueba localmente de forma obligatoria contra una base de datos SQLite de control con datos históricos.
   * Si la deriva del tópico o el sentimiento difiere en más de un $10\%$ del baseline establecido, el pipeline interrumpe el despliegue automático y alerta de **daños colaterales cognitivos**.
2. **Continuous Deployment a la Nube (GCP)**:
   * Superadas las pruebas estáticas y cognitivas, la CLI `gemini-api` en el entorno virtual empaqueta y despliega el Core Engine al motor **Vertex AI Agent Engine** de GCP de forma transparente.

---

## 📈 Pilar 4: DORA Metrics Optimization for Agent Fleets

Monitoreamos el éxito operacional de la flota de agentes utilizando las 4 métricas estándar de **DORA (DevOps Research and Assessment)**, adaptadas a sistemas autónomos de Inteligencia Artificial:

1. **Deployment Frequency (Frecuencia de Despliegue)**:
   * *Métrica*: Cuántas versiones estables de manifiestos y herramientas se liberan a producción.
   * *Optimización*: La inyección de dependencias dynamic-manifest permite actualizaciones en caliente en segundos sin reiniciar el servicio del agente.
2. **Lead Time for Changes (Tiempo de Espera para Cambios)**:
   * *Métrica*: El tiempo que toma desde el commit en local hasta la ejecución en Vertex AI.
   * *Optimización*: Automatizado con despliegue de comando único vía `adk-python` y `gemini-api` CLI.
3. **Change Failure Rate (Tasa de Fallos de Cambios)**:
   * *Métrica*: Porcentaje de despliegues que causan regresiones cognitivas o caídas físicas.
   * *Optimización*: Mitigado drásticamente mediante el **Impact Assessment Protocol** en SQLite y los límites físicos herméticos de memoria a nivel de Sandbox (128MB).
4. **Time to Restore Service (Tiempo de Recuperación - MTTR)**:
   * *Métrica*: Tiempo promedio de recuperación ante caídas imprevistas.
   * *Optimización*: Reducido a prácticamente cero segundos gracias al mecanismo de **Checkpoint-and-Resume** que restaura el Reasoning Chain exacto al instante de la interrupción física.

---

## 🧠 Pilar 5: TASK Structured Checklists & Workflows

Toda tarea compleja o plan de sprint orquestado por el **Tech Lead (`tool_sequence_git_strategy`)** y refinado por el **Product Owner (`tool_refine_user_story`)** debe seguir estrictamente la metodología **TASK**:

* **Estructura Atómica**: Las tareas complejas se descomponen en micro-tareas atómicas individuales en Markdown.
* **Marcado de Estado Expreso**:
  - `[ ]` Tarea sin iniciar (Uncompleted).
  - `[/]` Tarea en progreso activo de ejecución (In Progress).
  - `[x]` Tarea completamente terminada y verificada (Completed).
* **Branching Semántico**: Las tareas marcadas como paralelizadas deben sugerir de forma obligatoria nombres de ramas limpios (ej. `feature/modulo-seguridad`) y commits semánticos estructurados (ej. `feat(core): ...`, `test(sandbox): ...`, `fix(gateway): ...`) para maximizar la legibilidad y evitar colisiones de Git.

---

## 🔍 Pilar 6: Data, Code & Execution Provenance (Linaje y Procedencia)

El estándar de **Procedencia (Provenance / Linaje)** garantiza la trazabilidad absoluta y la inmutabilidad de la cadena de decisiones de la flota de agentes, asegurando que cada salida, recomendación o código ejecutado pueda auditarse hacia atrás hasta su origen exacto:

```
[Output / Report] 
      │
      ▼ (Audit / Traceback)
┌────────────────────────────────────────────────────────┐
│ 1. Code Provenance: UUID / Code Cryptographic Stamp   │
├────────────────────────────────────────────────────────┤
│ 2. Context Provenance: Structured Handover History     │
├────────────────────────────────────────────────────────┤
│ 3. Data/Model Provenance: SQLite Baseline / GCP Logs   │
└────────────────────────────────────────────────────────┘
```

1. **Code Provenance (Procedencia de Código)**:
   * **Mecanismo**: Cada telemetría, log de depuración y archivo generado en `/reports/` se firma con la **Identidad Criptográfica** (`Sig`) y el **UUID de Instancia** generado en `identity.py`.
   * **Control de Seguridad**: Asegura que el código ejecutor no haya sido alterado en caliente y provenga de una compilación legítima y firmada.
2. **Execution & Context Provenance (Procedencia de Ejecución)**:
   * **Mecanismo**: El coordinador central (`orchestrator.py`) registra de forma obligatoria el `context_handover_history` (historial de entregas de contexto).
   * **Control de Seguridad**: Mapea la cadena exacta de "quién invocó a quién", cuándo, y qué inputs se transfirieron, permitiendo reconstruir paso a paso el árbol de razonamiento cognitivo (Reasoning Chain) del agente.
3. **Data Provenance (Procedencia de Datos)**:
   * **Mecanismo**: Las transformaciones de datos realizadas en procesos aislados (`sandbox.py`) capturan y registran de forma inmutable el código fuente ejecutado, su salida estándar (`stdout`) y errores (`stderr`) en el ledger analítico.
   * **Control de Seguridad**: Previene la inyección de datos "fantasma" y garantiza que cualquier cambio métrico de MLOps esté respaldado por un set de control histórico identificable en SQLite.

---
*Fin del Manual Estándar Operativo (SOP).*
