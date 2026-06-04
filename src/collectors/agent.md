# 🧠 Manual Cognitivo para IA: Recopilación de Datos (Collectors)

Este manual te enseña, como agente inteligente, cómo funciona la capa de recolección de datos en redes sociales en `src/collectors/`.

---

## 🏛️ Filosofía de la Recolección de Datos

Los recopiladores de datos se encargan de descargar y formatear comentarios y métricas públicas de redes sociales (Instagram, Facebook, etc.) en archivos estructurados JSON para su posterior procesamiento local en `/data/raw/`.

---

## 📋 Módulos de Recopilación Disponibles

### 1. 📳 Recopilador Social Apify
*   **Módulo**: [`social_collector.py`](file:///home/fratfn/Desarrollo/Agency/src/collectors/social_collector.py)
*   **Función**: Invoca actores de Apify en la nube de forma segura utilizando la API KEY centralizada en variables de entorno (`APIFY_API_TOKEN`, con fallback legado `APIFY_TOKEN`).
*   **Uso**: Descarga comentarios de un post o perfil específico y los almacena localmente en la carpeta de datos crudos separando capas `real` y `synthetic` (`data/raw/<plataforma>/<capa>/` y réplica en `20_00_DATA/20_10_RAW/<plataforma>/<capa>/`).
*   **Comando de Invocación desde Agentes**:
    Puedes llamarlo de forma directa en Python importando su función principal o ejecutando el script como un subproceso ligero:
    `python src/collectors/social_collector.py --target <target_url>`

---

## 🔒 Variables de Entorno Requeridas
Este componente requiere la clave de API activa de Apify. Dicha clave se encuentra configurada en el almacén global seguro `/home/fratfn/vertex_env/.env` y es cargada de forma transparente por el cargador `dotenv` en tiempo de ejecución. No expongas nunca esta clave públicamente en archivos de texto.
