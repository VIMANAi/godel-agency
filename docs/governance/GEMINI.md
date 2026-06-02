# Workspace: SAIEL (Aislamiento de Proyecto)

## 🛡️ Protocolo de Integridad
- **RAÍZ/REPOS:** Solo lectura. Contiene el núcleo del proyecto SAIEL. NO modificar directamente.
- **PLAYGROUNDS/SANDBOX:** Única zona permitida para escritura de pruebas, scripts temporales y experimentos.
- **KNOWLEDGE_BASE:** Almacenamiento de esquemas, documentación técnica y metadatos de procesos ETL.

## ⚙️ Estándares de Ingeniería (Senior ETL)
1. **Idempotencia:** Todo script de transformación debe ser capaz de ejecutarse múltiples veces sin corromper el estado o duplicar datos.
2. **Validación de Esquema:** Los cambios en estructuras de datos deben probarse primero en `Playgrounds/sandbox/`.
3. **Trazabilidad:** Cada proceso ETL debe generar un log en `Knowledge_Base/logs/`.
4. **Clean Code:** Priorizar legibilidad y modularidad. Evitar el "hardcoding" de rutas; usar variables de entorno relativas al proyecto.
