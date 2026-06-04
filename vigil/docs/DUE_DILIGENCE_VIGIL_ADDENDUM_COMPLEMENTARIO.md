# ADDENDUM DE DUE DILIGENCE COMPLEMENTARIO
## Evaluación Industrial: Calidad, Seguridad, Operación y Madurez

**Proyecto:** Vigil / Nayarit 2026 | **Fecha:** 2026-06-03 | **Tipo:** Addendum técnico

---

## CONTROL METODOLÓGICO

**Leyenda:** ✅ Confirmado | 🔍 Inferido | ⚠️ Pendiente | ❓ No evaluable

---

# BLOQUE 1 — BLOQUEANTE PARA PRODUCCIÓN

## 45. Code Quality & Security Review

| Aspecto | Estado | Hallazgo | Severidad |
|---------|--------|----------|-----------|
| Tests automatizados | ❌ Ausentes | `pyproject.toml` configura pytest pero `tests/` vacío | 🔴 Bloqueante |
| Directorios src/ vacíos | 🔴 Crítico | `ingestion/`, `processing/`, `graph/` sin código | 🔴 Bloqueante |
| Notebooks como backend | ⚠️ Riesgo | `01_db_audit` con 84KB outputs, lógica de prod en notebooks | 🔴 Alto |
| Secrets hardcodeados | 🔍 No detectado | Búsqueda inicial negativa, requiere scan completo | 🟡 Media |
| Manejo de errores | ❌ No estructurado | Sin try/except consistente, sin logging | 🔴 Bloqueante |
| Cobertura de código | ❌ Inexistente | Solo `build_provenance.py` (~50 líneas) testeable | 🔴 Bloqueante |

**Acciones mínimas de remediación:**
- [ ] Tests unitarios para módulos existentes
- [ ] Mover lógica de notebooks a `src/` testeable
- [ ] Scan `pip-audit` en dependencias
- [ ] Revisar `yaml.load` vs `yaml.safe_load`

---

## 46. Data Quality Profiling

| Dataset | Profiling | Estado | Tareas Pendientes |
|---------|-----------|--------|-------------------|
| INE PREP 2017 | ✅ Parcial | Muestras leídas con Polars | Validar encoding completo |
| IEEN 2021/2024 | ❌ No ejecutado | Referenciado, no perfilado | Verificar duplicados, nulls |
| INEGI Censo 2020 | ❌ No ejecutado | 2,850 localidades | Validar vs catálogo oficial |
| Cartografía | ❌ No ejecutado | 12MB shapefiles | Validar proyecciones EPSG |
| PSI y PLRAD (nuevo) | ❌ No ejecutado | 663MB recién migrado | Explorar corte sept 2023 |
| ODS nacional (nuevo) | ❌ No ejecutado | 7MB recién migrado | Descomprimir, filtrar Nayarit |

**Anomalías conocidas sin mitigación:**
- A01: `ID_ENTIDAD` como string `"18"` — requiere cast
- A02: `EXT_CONTIGUA = "00"` — error de parseo
- A03: Duplicados `San Blas.txt` vs `SAN BLAS.txt` — sin deduplicación automática

---

## 47. Compliance & Legal Review

| Aspecto | Evaluación | Riesgo | Acción |
|---------|------------|--------|--------|
| PII en datasets | 🔍 Probable | Nombres de candidatos, posible CURP | Verificar contenido exacto |
| Scraping Apify | 🔍 Revisar TOS | Meta Ad Library, Facebook TOS | Confirmar uso research permitido |
| Gemini API | ✅ Aparente OK | TOS prohíbe predecir resultados electorales | Documentar uso no predictivo |
| Datos electorales INE | ✅ Públicos | Uso libre con atribución | Correcto |

**Recomendación:** Consultar especialista en protección de datos para PII electoral mexicano.

---

## 48. Reproducibility & Environment Audit

| Aspecto | Estado | Evidencia | Riesgo |
|---------|--------|-----------|--------|
| requirements.txt | ✅ Completo | 55 líneas, versiones especificadas | 🟢 Bajo |
| pyproject.toml | ✅ Completo | Metadata + herramientas | 🟢 Bajo |
| Docker | ❌ Ausente | Sin Dockerfile | 🔴 Bloqueante portabilidad |
| CI/CD | ❌ Ausente | Sin GitHub Actions | 🔴 Bloqueante automatización |
| Rutas hardcodeadas | 🔴 Presente | `02_download_ine.ipynb` usa `/run/media/fnfrater/SERVER_TOOLBOX/` | 🔴 Bloqueante: solo funciona en máquina específica |
| Datos externos | 🔴 Crítico | `SERVER_TOOLBOX/centralinfo/` contiene datos Facebook Feb 2026 | 🔴 Bloqueante reproducibilidad |

**Acciones para reproducibilidad:**
- [ ] Parametrizar rutas (config.yaml o env vars)
- [ ] Migrar datos Facebook desde SSD externo
- [ ] Crear Dockerfile Python 3.11
- [ ] Script de bootstrap `scripts/setup.sh`

---

## 49. Data Lineage & Governance

| Aspecto | Estado | Hallazgo |
|---------|--------|----------|
| SHA-256 provenance | ✅ Implementado | 72 entradas con hash, fecha, fuente |
| Procedencia web vs SSD | ❌ No distingue | Dato crítico: doble origen sin trazabilidad |
| Transformaciones registradas | ❌ No documentado | raw→silver→gold sin lineage |
| Versionado de datos | ❌ No implementado | Sin DVC o similar |
| Ownership de datasets | ❌ No definido | Sin metadatos de responsable |

**Procedencia confirmada post-análisis:**
- **Windsurf/Web:** PREP 2017 (8 CSVs), Cómputos 2021/2024 (4 ZIPs + 2 CSVs) — descargados 2026-06-01 19:27-20:22
- **SSD Externo:** IEEN (11 archivos), INEGI (5 archivos), Geo (10 archivos), Work (19 archivos) — migrados 2026-05-30 a 2026-06-01

---

## 50. Pipeline Reliability / ETL Review

| Pipeline | Estado | Implementación | Confiabilidad |
|----------|--------|----------------|---------------|
| Descarga INE/IEEN | ⚠️ Parcial | Notebook manual con httpx | Manual, no automatizado |
| Validación Pandera | ❌ No implementado | Schemas definidos conceptualmente | Sin validación automática |
| Transformación raw→silver | ❌ No implementado | Directorios vacíos | Inexistente |
| Carga Neo4j | ❌ No implementado | Configuración sin código | Sin conexión validada |
| Orquestación | ❌ No implementado | Sin Airflow/Prefect | Totalmente manual |

**Características de confiabilidad ausentes:**
- ❌ Idempotencia (reejecución duplica datos)
- ❌ Reintentos (fallos de red no manejados)
- ❌ Manejo de errores estructurado
- ❌ Scheduling o automatización
- ❌ Monitoreo de pipelines

---

## 51. Secrets & Supply Chain Security

| Aspecto | Estado | Evaluación |
|---------|--------|------------|
| .env.template | ✅ Correcto | Sin valores reales, bien documentado |
| Secrets en código | 🔍 No detectado | Requiere scan adicional completo |
| Dependencias vulnerables | ❌ No auditado | Pendiente: `pip-audit`, `safety check` |
| Lock file con hashes | ❌ No generado | Pendiente: `pip-compile --generate-hashes` |
| SBOM | ❌ No generado | Pendiente: `cyclonedx-bom` |

---

# BLOQUE 2 — NECESARIO PARA OPERACIÓN SERIA

## 52. Observability & Operational Readiness

| Aspecto | Estado | Prioridad |
|---------|--------|-----------|
| Logging estructurado | ❌ No implementado | 🔴 Alta |
| Métricas de pipeline | ❌ No implementado | 🔴 Alta |
| Health checks | ❌ No implementado | 🔴 Alta |
| Runbooks | ❌ No existe | 🔴 Alta |
| Procedimiento de rollback | ❌ No documentado | 🔴 Alta |

**MVP sugerido:**
```python
import structlog
logger = structlog.get_logger()
# logger.info("pipeline_stage", stage="extract", records=1000)
```

---

## 53. Integration & API Reliability

| Servicio | SLA Estimado | Fallback | Riesgo |
|----------|-------------|----------|--------|
| Google Gemini API | 99.9% | Cache local | 🟡 Medio (rate limits) |
| Apify | Variable | Datos SSD Feb 2026 | 🟡 Medio (dependencia tercero) |
| Neo4j Aura (gratuito) | 99.5% | NetworkX local | 🟡 Medio (límites de capa) |

**Resiliencia ausente:**
- ❌ Retry con backoff
- ❌ Circuit breaker
- ❌ Cache de respuestas

---

## 54. Performance & Scalability (Inferido)

| Escenario | Viabilidad | Bloqueo Principal |
|-----------|------------|-------------------|
| Múltiples demarcaciones (10) | 🟡 Posible | Config.yaml solo Tepic |
| Múltiples estados (32) | 🔴 Difícil | Volumen, costo APIs, orquestación |
| Tiempo real (scraping continuo) | 🔴 No implementado | Sin orquestador, sin pipeline |

**Nota:** Evaluaciones inferidas de arquitectura, no benchmarks ejecutados.

---

## 55. Documentation & Knowledge Transfer

| Documento | Estado | Calidad |
|-----------|--------|---------|
| AGENTS.md | ✅ Completo | Alta (7.9KB) |
| ARCHITECTURE.md | ✅ Completo | Alta (11.6KB) |
| DATA_INVENTORY.md | ✅ Completo | Alta (17.5KB) |
| Runbooks | ❌ No existe | 🔴 Gap crítico |
| ADRs (decisiones de diseño) | ❌ No existe | 🟡 Pendiente |
| Onboarding técnico | 🟡 Parcial | AGENTS.md sirve, falta paso a paso |

**Conocimiento tribal:**
- 🔴 **SAEIL:** NLP, SNA, algoritmos PDIV — alto riesgo, requiere documentación urgente

---

## 56. Team & Organizational Readiness

| Competencia | Disponible | Gap |
|-------------|------------|-----|
| Python/Polars | ✅ Sí | Cubierto |
| Neo4j/Cypher | ❓ Desconocido | Sin evidencia |
| NLP/Gemini/LLMOps | ❓ SAEIL externo | Dependencia crítica |
| SNA/NetworkX | ❓ SAEIL externo | Dependencia crítica |
| ETL/Orchestration | ❌ No implementado | Sin experiencia visible |
| Testing/QA | ❌ No tests | Gap significativo |

---

## 57. Long-term Maintainability

| Deuda Técnica | Interés | Acción Preventiva |
|---------------|---------|-------------------|
| Directorios src/ vacíos | Bloqueante | Implementar ahora |
| Tests ausentes | Bloqueante | Suite mínima inmediata |
| Notebooks con lógica | Medio | Refactorizar a módulos |
| Sin Docker | Medio | Containerizar |
| Dependencias sin lock | Medio | Generar requirements.lock |

---

# BLOQUE 3 — CONDICIONADO POR ESTRATEGIA

## 58. Cost Analysis & Cloud Economics (Por evaluar)

| Componente | Costo Estimado Mensual | Supuestos |
|------------|----------------------|-----------|
| Neo4j Aura (gratuito → crecimiento) | $0 → $50-200 | Dependiendo de nodos/relaciones |
| Apify (scraping) | $0-100 | Créditos de cómputo |
| Gemini API | $0-50 | Tokens de procesamiento |
| Storage (local → cloud) | $0 → $20-50 | Si migra a S3/GCS |

**Nota:** Requiere estimación real basada en volumen de datos proyectado.

---

## 59. UX / Adoption Assessment (Aplicable si busca usuarios no técnicos)

| Aspecto | Estado | Evaluación |
|---------|--------|------------|
| Curva de aprendizaje | ⚠️ Pendiente | Notebooks técnicos requieren Python |
| Necesidad de interfaz gráfica | ⚠️ Pendiente | Streamlit/Gradio no evaluados |
| Adecuación a analistas electorales | ❓ No evaluado | Sin shadowing con usuario real |

---

## 60. Model / NLP / LLM Governance (Si aplica Gemini/NLP)

| Aspecto | Estado | Acción |
|---------|--------|--------|
| Datasets de evaluación | ❌ No definido | Crear ground truth para NLP |
| Versionado de prompts | ❌ No implementado | Pendiente si hay prompts productivos |
| Evaluación de sesgos | ❌ No realizada | Pendiente para NLP electoral |
| Trazabilidad de outputs | ❌ No implementada | Logging de clasificaciones Gemini |

---

# BLOQUE 4 — OPCIONAL / ESTRATÉGICO

## 61. Competitive / Strategic Context

No aplica al due diligence técnico central. Separar como "análisis estratégico complementario" si se requiere.

---

# MATRIZ DE PRIORIZACIÓN EJECUTIVA

## A. Bloqueantes para Producción (Nivel 1)

| # | Hallazgo | Riesgo | Acción Inmediata |
|---|----------|--------|------------------|
| 1 | Tests automatizados ausentes | Cambios riesgosos | Suite mínima pytest |
| 2 | Directorios src/ vacíos | Arquitectura sin implementación | Implementar ingestion/processing |
| 3 | Pipeline ETL inexistente | Sin automatización de datos | Pipeline raw→silver→gold |
| 4 | Datos Facebook en SSD externo | Sin reproducibilidad | Migrar a repo |
| 5 | Rutas hardcodeadas | Portabilidad nula | Parametrizar configuración |
| 6 | Observabilidad inexistente | Sin diagnóstico | Logging estructurado |

## B. Necesario para Operación Seria (Nivel 2)

| # | Hallazgo | Impacto | Acción |
|---|----------|---------|--------|
| 7 | Data profiling incompleto | Calidad de datos desconocida | Profiling IEEN, INEGI, cartografía |
| 8 | Distinguir procedencia web/SSD | Trazabilidad incompleta | Mejorar provenance.jsonl |
| 9 | Docker/containerización | Sin portabilidad | Dockerfile + docker-compose |
| 10 | Runbooks operativos | Sin procedimientos incidentes | Documentar troubleshooting |
| 11 | Knowledge transfer SAEIL | Riesgo bus factor | Documentar NLP/SNA |
| 12 | CI/CD | Sin automatización | GitHub Actions |

## C. Importante pero Condicionado (Nivel 3)

| # | Hallazgo | Condición | Acción |
|---|----------|-----------|--------|
| 13 | Cost analysis | Si busca operación sostenida | Estimar costos mensuales |
| 14 | UX/Interfaz gráfica | Si usuarios no técnicos | Evaluar Streamlit |
| 15 | NLP Governance | Si Gemini en producción | Versionado de prompts |

## D. Opcional / Estratégico (Nivel 4)

| # | Hallazgo | Contexto |
|---|----------|----------|
| 16 | Competitive analysis | Solo si inversión/mercado |

---

# CHECKLIST DE REMEDIACIÓN INMEDIATA

## Prioridad P0 (Esta semana)
- [ ] Migrar datos Facebook desde `SERVER_TOOLBOX/centralinfo/` a `data/raw/social_media/`
- [ ] Ejecutar `pip-audit` en requirements.txt
- [ ] Verificar permisos 0600 en archivo `.env`
- [ ] Generar `requirements.lock` con hashes
- [ ] Crear tests unitarios para `build_provenance.py`

## Prioridad P1 (Este mes)
- [ ] Implementar `src/ingestion/ingest_ine.py` con descarga parametrizada
- [ ] Implementar `src/processing/clean_electoral.py` con Pandera
- [ ] Poblar `silver/electoral/` con datos INE/IEEN limpios
- [ ] Crear Dockerfile Python 3.11
- [ ] Implementar logging estructurado con structlog
- [ ] Profiling completo IEEN 2021/2024 con Polars

## Prioridad P2 (Próximo mes)
- [ ] Crear instancia Neo4j Aura y validar conexión
- [ ] Implementar pipeline ETL orquestado (Prefect)
- [ ] Documentar conocimiento SAEIL (NLP, SNA, PDIV)
- [ ] Curar datos ODS nacional (filtrar Nayarit)
- [ ] Implementar tests de integración para APIs

## Prioridad P3 (Trimestre)
- [ ] CI/CD con GitHub Actions
- [ ] Dashboard con Streamlit o Gradio
- [ ] Runbooks completos de operación
- [ ] Evaluación de costos cloud mensual

---

# REGISTRO DE HALLAZGOS CRÍTICOS POST-ANÁLISIS

| ID | Hallazgo | Tipo | Confianza | Fecha Descubrimiento |
|----|----------|------|-----------|---------------------|
| H-POST-01 | Doble procedencia: Windsurf/web vs SSD | Evidencia directa | Alta | 2026-06-03 |
| H-POST-02 | Cartografía PSI y PLRAD 663MB no incluida originalmente | Evidencia directa | Alta | 2026-06-03 |
| H-POST-03 | Datos ODS nacional 7MB requieren curación | Evidencia directa | Alta | 2026-06-03 |
| H-POST-04 | `02_download_ine.ipynb` destino hardcodeado a SSD | Evidencia directa | Alta | 2026-06-03 |
| H-POST-05 | Notebook 01_db_audit con rutas potencialmente rígidas | Inferencia | Media | 2026-06-03 |

---

**Fin del Addendum Complementario**
*Generado siguiendo marco industrial de due diligence técnico, datos y operativo*
*Actualizado: 2026-06-03 con hallazgos post-análisis*
