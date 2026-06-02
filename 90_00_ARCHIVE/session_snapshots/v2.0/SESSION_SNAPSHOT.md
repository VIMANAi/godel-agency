# SNAPSHOT: CONTINUIDAD DEL GRAFO DE GRAFOS v2.0

Este documento proporciona el contexto crítico necesario para que la próxima sesión de ingeniería continúe la expansión y operación del ecosistema.

## 1. Estado Actual (Ground Truth)
- **Ecosistema Técnico:** 422 Crates materializados (48 Scikit + 374 OpenAI).
- **Proyecto Piloto (SAIEL):** Cratizado bajo el estándar industrial, con pipeline Cloud-Native (Vertex AI + BigQuery) funcional en la VM.
- **Memoria Matemática:** Matrices de adyacencia duales e índices de centroides (768 dims) generados y sincronizados en GCS.

## 2. Insumos para Procesamiento de Nuevos Repositorios
Para incorporar un nuevo repositorio al Grafo Técnico, se requiere:
1.  **Etapa SoC:** Ejecutar `06_soc_code_splitter.py` sobre el nuevo repo para separar Lógica AST de Teoría.
2.  **Cratización:** Usar el `09_smart_crate_assembler_v2.py` para generar la estructura de carpetas físicas.
3.  **Anclaje al Grafo:** Ejecutar `27_inter_project_bridge.py` para calcular la similitud vectorial con los Crates existentes de Scikit y OpenAI.
4.  **Actualización de Centroides:** Recalcular `25_generate_crate_centroids.py` para incluir el nuevo repo en el mapa 3D.

## 3. Requerimientos de Entorno (VM)
- **Venv Activo:** `/home/persival/Dev/Playgrounds/ETL_Refinement_v1.1/venv/`
- **Credenciales:** Se requiere `gcloud auth application-default login` para activar la capa Cloud de Vertex AI.
- **Hugging Face:** Login activo en la VM para descarga de modelos SBERT (768 dims).

## 4. Directorio de Documentación (Snapshot)
Todos los reportes técnicos detallados y el manifiesto de la pipeline residen en:
`/home/persival/Dev/Knowledge_Base/session_snapshots/session_v2.0_closing/`

---
*Snapshot generado para garantizar latencia cero en la transición de conocimiento.*
