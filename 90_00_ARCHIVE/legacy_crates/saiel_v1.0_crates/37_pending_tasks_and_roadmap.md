# PENDIENTES Y HOJA DE RUTA (ROADMAP) - PROYECTO SAIEL

Este documento registra las tareas pendientes y las expansiones futuras para el ecosistema SAIEL Inteligencia Política.

## 1. Tareas de Despliegue Inmediato
- [ ] **Script de Lanzamiento Rápido (`deploy_all.sh`):** Crear un script Bash que automatice el comando `gcloud builds submit` y `gcloud run deploy` para el extractor de Apify.
- [ ] **Autenticación ADC:** Realizar `gcloud auth application-default login` en la VM para activar Vertex AI y BigQuery.
- [ ] **Configuración de Secretos:** Mover el `APIFY_TOKEN` a Google Cloud Secret Manager para máxima seguridad.

## 2. Optimizaciones Algorítmicas (Capa Scikit-Learn)
- [ ] **Implementar Isolation Forest:** Integrar el Crate `sklearn.ensemble` para la detección automática de ataques de bots.
- [ ] **Calibración Ridge:** Usar regresión Ridge para ajustar dinámicamente los pesos de la fórmula PDIV basados en datos históricos.
- [ ] **LDA Topic Modeling:** Implementar el análisis de tópicos latentes para agrupar narrativas sin supervisión humana.

## 3. Capa de Conocimiento Personal
- [ ] **Expansión del Grafo Estratégico:** Seguir registrando intuiciones y notas de campo en `/personal_knowledge/strategy/`.
- [ ] **Conexión con Looker Studio:** Crear un tablero visual que consuma directamente los datos de la tabla `saiel_intel.pdiv_results` en BigQuery.

---
*Documento de Control de Proyecto - Fase 2 Completada*
