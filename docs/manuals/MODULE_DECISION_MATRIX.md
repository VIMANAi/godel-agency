# Matriz de Decisión de Módulos

Estado de referencia para consolidar una sola ruta productiva y separar histórico de operación activa.

| Módulo actual | Estado | Owner sugerido | Dependencias clave | Impacto en pipeline cloud |
|---|---|---|---|---|
| `/src/core` | Mantener | Data Platform | pandas, pydantic, Vertex/BigQuery adapters | Núcleo de normalización, anonimización y analítica PDIV |
| `/src/collectors/social_collector.py` | Mantener + refactor | Data Acquisition | Apify, httpx, BeautifulSoup | Entrada OSINT para capa raw |
| `/src/deploy/main_cloudrun.py` | Mantener + refactor | Platform Ops | Cloud Run, GCS, Apify | Orquestación serverless de ingesta |
| `/src/core/pdiv_pipeline.py` | Refactorizar | Data Platform | core adapters, local/vertex sentiment | Debe eliminar rutas legacy y consolidar ejecución por capas |
| `/src/collectors/apify_client.py` | Refactorizar (activar) | Data Acquisition | apify-client | Cliente común para evitar lógica duplicada |
| `/docs/research` | Mantener | Research/Ops | Markdown docs | Soporte metodológico y contexto analítico |
| `/vigil/docs` | Mantener | Governance | Markdown + notebooks | Auditoría, trazabilidad y cumplimiento |
| `/src` vs `/10_00_SRC` | Consolidar en `/src` | Platform Architecture | estructura de paquetes Python | Eliminar doble mantenimiento de código activo |
| `/docs` vs `/40_00_DOCS` | Consolidar en `/docs` | Documentation | guías técnicas | Fuente única de documentación operativa |
| `/vigil` vs `/50_00_VIGIL` | Consolidar en `/vigil` | Governance | artefactos de auditoría | Fuente única de auditoría activa |
| `/reports` vs `/80_00_OUTPUTS` | Consolidar en `/reports` | Analytics | generación de reportes | Evitar duplicados de salidas ejecutivas |
| `/archive` y `/90_00_ARCHIVE` | Archivar (solo lectura) | Repository Maintainers | históricos | Fuera del flujo productivo |

## Decisión operativa inmediata

1. Ruta canónica activa: `platform/`, `src/`, `docs/`, `vigil/`, `reports/`.
2. Rutas duplicadas numeradas: estado congelado, sin nuevos cambios funcionales.
3. Históricos: `archive/` y `90_00_ARCHIVE/` como referencia de solo lectura.
