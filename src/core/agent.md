# 🧠 Manual Cognitivo para IA: Núcleo Analítico y Procesamiento (Core)

Este manual te enseña, como agente inteligente, cuáles son las funciones, módulos e importaciones de la capa matemática y de procesamiento de datos en `src/core/`.

---

## 🏛️ Filosofía del Núcleo Determinista

Todos los scripts en esta carpeta **DEBEN** ser Python puro y determinista. No importes librerías de agentes del SDK de Antigravity en esta sección. Toda la lógica dura de datos debe funcionar de forma estable y aislada de forma que sea fácilmente testeable desde scripts normales de Python.

---

## 📋 Módulos de Cálculo y Análisis Disponibles

Cuando necesites realizar tareas matemáticas, de clasificación o persistencia, debes importar y ejecutar los siguientes módulos específicos:

### 1. 📊 Procesamiento de Sentimientos y Opinión Local
*   **Modulo**: [`local_sentiment.py`](file:///home/fratfn/Desarrollo/Agency/src/core/local_sentiment.py)
*   **Función**: Procesa el sentimiento local del texto de comentarios utilizando clasificadores empotrados.
*   **Cuándo usar**: Para categorizar la opinión de comentarios individuales antes de agruparlos en narrativas.

### 2. 🧬 Motor de Descubrimiento de Narrativas (Sensemaker)
*   **Módulo**: [`sensemaker_engine.py`](file:///home/fratfn/Desarrollo/Agency/src/core/sensemaker_engine.py)
*   **Función**: Analiza colecciones de comentarios procesados para descubrir temas comunes, calcular el Índice de Diversidad de Shannon y alertar sobre crisis reputacionales.
*   **Salida**: Genera un archivo estructurado en `data/processed/reporte_industrial_narrativas.json`.

### 3. 📈 Pipeline y Calculadoras de Variables PDIV
*   **Módulos**:
    - [`pdiv_calculator.py`](file:///home/fratfn/Desarrollo/Agency/src/core/pdiv_calculator.py): Orquestador y consolidación del índice PDIV global.
    - [`pdiv_p_sentiment.py`](file:///home/fratfn/Desarrollo/Agency/src/core/pdiv_p_sentiment.py): Cálculo del pilar de Sentimiento (Polaridad).
    - [`pdiv_d_volume.py`](file:///home/fratfn/Desarrollo/Agency/src/core/pdiv_d_volume.py): Cálculo del pilar de Volumen de Diálogo.
    - [`pdiv_i_engagement.py`](file:///home/fratfn/Desarrollo/Agency/src/core/pdiv_i_engagement.py): Cálculo del pilar de Engagement/Interacción.
    - [`pdiv_v_growth.py`](file:///home/fratfn/Desarrollo/Agency/src/core/pdiv_v_growth.py): Cálculo del pilar de Crecimiento y Velocidad.
    - [`pdiv_pipeline.py`](file:///home/fratfn/Desarrollo/Agency/src/core/pdiv_pipeline.py): Pipeline secuencial automatizado para recalcular todo el índice.
*   **Cuándo usar**: Importa `pdiv_pipeline` para recalcular todas las variables analíticas de un candidato o partido político de forma automática sobre los datos raw indexados.

---

## 🗄️ Conexión Compartida de Base de Datos para RAG
*   **Módulo**: [`db_connector.py`](file:///home/fratfn/Desarrollo/Agency/src/core/db_connector.py) *(En desarrollo)*
*   **Función**: Proveedor unificado de conexiones empotradas a ChromaDB persistente en `/home/fratfn/Desarrollo/Databases/chromadb_store/`.
*   **Uso en RAG**: Úsalo para indexar resúmenes en la base de datos o realizar búsquedas semánticas para responder preguntas basadas en las narrativas y reportes del proyecto de forma local.
