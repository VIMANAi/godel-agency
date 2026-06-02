# SAIEL: Manual Operativo del Motor de Inteligencia

Este documento detalla cómo operar el motor de SAIEL cumpliendo con los protocolos de ingeniería senior.

## 🏗️ Arquitectura del Motor (`engine/core/`)
- `data_ingestion.py`: Punto de entrada para datos crudos (CSV/JSON).
- `local_sentiment.py`: Inferencia local vía Ollama. **Idempotente por diseño.**
- `pdiv_calculator.py`: Algoritmo matemático para el Posicionamiento Digital.
- `saiel_agent.py`: Orquestador principal del pipeline.

## 🛡️ Protocolo de Desarrollo
1. **Zonas de Escritura:** Queda terminantemente prohibido crear archivos en `Repos/`. Toda nueva lógica o script de prueba debe vivir en `Playgrounds/sandbox/`.
2. **Pruebas de Integración:** Antes de proponer un cambio al núcleo, se debe ejecutar:
   ```bash
   python3 Repos/test_pipeline.py
   ```
   (Ejecutar desde el sandbox apuntando a los módulos del Repo).
3. **Manejo de Datos:** Los datos crudos se depositan en `Repos/data/raw/` (solo para lectura). Los resultados se escriben en la carpeta de resultados del proyecto, fuera de este repositorio.

## ⚙️ Dependencias
Instalar antes de operar:
```bash
pip install -r Repos/requirements.txt
```

---
*Gobernanza SAIEL - 2 de mayo de 2026*
