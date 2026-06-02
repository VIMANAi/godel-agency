# src/ — Código Fuente Activo SAIEL

Este directorio contiene el código de producción del ecosistema SAIEL, organizado por **Separation of Concerns (SoC)**.

## Módulos

| Directorio      | Responsabilidad                                          | Scripts Clave                                              |
|-----------------|----------------------------------------------------------|------------------------------------------------------------|
| `core/`         | Motores analíticos ETL y pipeline PDIV                   | `data_ingestion.py`, `pdiv_pipeline.py`, `pdiv_calculator.py`, `local_sentiment.py`, `sensemaker_engine.py` |
| `agents/`       | Orquestador CLI con soporte LLM (Ollama) y modo reglas   | `saiel_agent.py`                                           |
| `collectors/`   | Scrapers OSINT (Apify, Instagram, Facebook, Nayarit)     | `social_collector.py`, `mass_collector.py`, `apify_client.py` |
| `tests/`        | Suite de pruebas de integración y validación E2E          | `test_pipeline.py`                                         |
| `deploy/`       | Infraestructura: Docker, Cloud Run, scripts bash, monitor | `Dockerfile`, `main_cloudrun.py`, `saiel_start.sh`, `windows_receiver.py` |

## Ejecutar el Agente

```bash
# Desde la raíz del proyecto con el venv activo:
PYTHONPATH=. python src/agents/saiel_agent.py
```

## Ejecutar Pruebas

```bash
PYTHONPATH=. python src/tests/test_pipeline.py
```

## Flujo de Datos (Capas SoC)

```
[collectors/] → data/raw/ → [core/data_ingestion] → data/processed/ → [core/pdiv_pipeline] → reports/
```

> **Regla de Escritura:** Solo los scripts en `collectors/` escriben en `data/raw/`. Solo `core/data_ingestion.py` escribe en `data/processed/`. Ningún módulo escribe directamente sobre otro módulo.
