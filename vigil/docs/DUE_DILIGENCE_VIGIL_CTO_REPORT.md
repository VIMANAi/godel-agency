# DUE DILIGENCE TÉCNICA — VIGIL / NAYARIT 2026
## Sistema de Inteligencia Electoral Local

**Fecha de análisis:** 2026-06-03  
**Analista:** CTO / Arquitecto de Datos / Auditor de Producto  
**Proyecto:** `/home/fnfrater/Escritorio/Dev/RndmStudio/vigil/`  
**Mandato:** Evaluación de madurez técnica, arquitectura de datos, riesgos de continuidad  

---

# 1. RESUMEN EJECUTIVO

## Qué es el sistema
**Vigil** es un sistema de análisis de datos electorales e inteligencia política para el ciclo electoral **Nayarit 2026**. Integra datos oficiales (INE, IEEN, INEGI), análisis de redes sociales (Facebook/Instagram vía Apify) y modelado de grafos (Neo4j + NetworkX/Louvain) para producir inteligencia accionable a nivel de sección electoral.

**Métrica central:** PDIV (Posicionamiento Digital de Intención de Voto)

## Grado de madurez
- **Estado actual:** MVP funcional con datos históricos cargados, pipeline ETL documentado
- **Madurez del código:** Beta técnica — arquitectura sólida, documentación extensa
- **Madurez de datos:** 72 archivos con provenance SHA-256, 1.7GB de datos estructurados (+663MB cartografía adicional +7MB ODS nacional migrados post-análisis)
- **Procedencia mixta:** Datos descargados por Windsurf vía web (httpx) + datos migrados desde SSD externo (`SERVER_TOOLBOX`)

## Completitud por componente
| Componente | Estado | Completitud |
|------------|--------|-------------|
| Ingesta INE/IEEN/INEGI | Funcional | 90% |
| Provenance SHA-256 | Implementado | 100% |
| Pipeline ETL | Documentado | 80% |
| NLP Clasificación | Configurado | 60% |
| SNA / Grafos | Diseñado | 40% |
| Dashboard | Plantillas | 50% |
| Neo4j Aura | Pendiente | 0% |
| Scraping continuo | Pendiente | 0% |

## Riesgos principales
1. **R-01:** Dependencia conocimiento tácito SAEIL para NLP avanzado
2. **R-02:** Ausencia de base de datos para producción
3. **R-03:** 67 de 69 fuentes identificadas no descargadas
4. **R-04:** Datos Facebook Feb 2026 en SSD externo sin integrar
5. **R-05:** Pipeline de orquestación no implementado
6. **R-06 (NUEVO):** Datos ODS nacional migrados sin curar (requiere filtrado para Nayarit)
7. **R-07 (NUEVO):** Doble procedencia no documentada en provenance (web vs SSD)

## Dictamen preliminar (Semáforo CTO)
🟡 **AMARILLO: Viable pero con riesgos importantes**

El proyecto tiene base técnica sólida pero requiere saneamiento antes de escalar.

---

# 2. LECTURA FUNCIONAL DEL PRODUCTO

## Problema que resuelve
Monitoreo manual de redes sociales de candidatos es ineficiente y no escalable. Falta integración entre datos electorales históricos y comportamiento digital actual.

## Actores identificados
- **Analistas electorales:** Consumen reportes semanales
- **Candidatos/Partidos:** Sujetos de análisis (entidades monitoreadas)
- **Electorado:** Referenciado vía secciones electorales INEGI
- **Agentes de IA (SAEIL):** Ejecutan NLP, construyen grafos

## Flujos principales
- FB-01: Ingesta semanal Apify → Validación Pandera → NLP Gemini
- FB-02: Electoral + Sociodemográfico + Redes → Grafo NetworkX → Reporte
- FB-03: Auditoría continua con verificación SHA-256

---

# 3. ARQUITECTURA TÉCNICA

## Stack detectado
| Capa | Tecnología | Propósito |
|------|------------|-----------|
| Runtime | Python 3.11 + venv | Entorno aislado |
| DataFrames | Polars + PyArrow | ETL de alto rendimiento |
| LLM | Gemini 2.5-flash | Clasificación NLP, OCR |
| Grafos local | NetworkX + Louvain | Análisis comunidades |
| Grafos prod | Neo4j Aura (planificado) | Grafo conocimiento |
| Scraping | Apify | Datos redes sociales |
| Geoespacial | GeoPandas + Folium | Mapas electorales |
| Validación | Pandera | Schemas de datos |

## Estructura de directorios
```
vigil/
├── config/              # Configuración maestra
├── data/
│   ├── raw/NAYARIT_DB_RAW/  # 111 archivos, 1.7GB (INMUTABLE)
│   ├── silver/          # Datos limpios (vacío)
│   └── gold/            # Datasets reporte (vacío)
├── notebooks/           # 3 notebooks (auditoría, descarga, setup)
├── src/                 # Código Python (parcialmente vacío)
└── docs/                # 8 documentos técnicos
```

## Integraciones externas configuradas
- Google Gemini API ✅
- Apify ✅
- Neo4j Aura ✅ (configurado, no implementado)
- Meta Ad Library ✅ (configurado)
- NotebookLM MCP ✅

## Deuda técnica
| Item | Severidad |
|------|-----------|
| Directorios src/ vacíos | 🔴 Alta |
| Silver/Gold vacíos | 🔴 Alta |
| Tests ausentes | 🟡 Media |
| Anomalías conocidas sin mitigación automática | 🟡 Media |

---

# 4. INVENTARIO DE DATOS

## Resumen provenance (72 entradas SHA-256)

### INE Federal — 16 archivos
- PREP 2017 (4 archivos): Ayuntamientos, Dip Locales, Gobernatura, Regidurías
- PREP 2018 (3 archivos): Dip Federales, Presidente, Senadores
- Cómputos 2021 (1 archivo): Dip Federales
- Cómputos 2024 (1 archivo): Dip Federales
- Archivos candidatos (5 archivos): 28-3,021 filas cada uno
- Zips originales (4 archivos): 38.8-5.8 MB

### IEEN Estatal — 17 archivos
- Elecciones 2021: Dip Locales, Gobernatura, Presidentes Mun, Regidurías
- Elecciones 2024: Dip Locales, Presidentes Mun, Regidurías, Candidaturas Electas
- Ganadores y extraordinarias 2021
- Zips originales

### INEGI — 5 archivos
- Censo 2020: Diccionario, Localidades (2,850 filas, 286 cols), Municipios (20 filas), ITER

### Geoespacial — 10 archivos
- CEM nov 2023 (1.4 MB)
- Marco Geoestadístico INE shapefiles (12.1 MB)
- Casillas Nayarit 2024 (1,821 registros)
- WKT, KMZ, TXT georreferenciados

### Trabajo/Análisis previo — 19 archivos
- Votos por casilla completos (1,829 filas)
- Candidatos electos 2024 (540 filas)
- Datos hogares por sección (878 filas)
- Análisis SAEIL previo (Andrea Navarro, Instagram)

---

# 5. MODELO DE DOMINIO INFERIDO

## Entidades principales
```
CANDIDATO (id, nombre, partido, cargo, aliases)
├── 1:N → ACTIVO_DIGITAL (plataforma, tipo, seguidores)
├── 1:N → RESULTADO_ELECTORAL (votos, sección, elección)
└── N:M → TEMA (vía contenido analizado)

SECCION_ELECTORAL (id, distrito_fed, distrito_loc, municipio, geometria)
├── 1:N → CASILLA (clave, tipo, ubicación, lista_nominal)
├── 1:1 → DATOS_INEGI (población, vivienda, escolaridad)
└── 1:N → RESULTADO_ELECTORAL

CONTENIDO_DIGITAL (id, texto, fecha, engagement, plataforma)
├── N:1 → ACTIVO_DIGITAL
├── 1:N → CLASIFICACION_NLP (sentimiento, framing, keywords)
└── N:M → TEMA (tema electoral, prioridad)
```

## Relaciones clave
- Candidato ↔ Activo Digital: Un candidato tiene múltiples presencias digitales
- Sección Electoral ↔ Casilla: Una sección tiene múltiples casillas físicas
- Contenido ↔ Clasificación NLP: Un contenido tiene múltiples clasificaciones (temas)
- Sección Electoral ↔ Datos INEGI: Enriquecimiento sociodemográfico por territorio

---

# 6. GAPS CRÍTICOS Y DATOS FALTANTES

## Gaps de datos identificados (del DATA_INVENTORY.md)

### 🔴 ALTA prioridad (19 fuentes)
| Fuente | Descripción | Impacto |
|--------|-------------|---------|
| AGEB INEGI manzana | Datos micro-urbanos Censo 2020 | Precisión territorial |
| Cartografía SIGE INE 2024 | Shapefiles secciones electorales | Cruce espacial votos-demografía |
| Lista Nominal 2026 | Electores por sección actualizada | Base del modelo |
| ENOE 2025 Nayarit | Empleo por municipio | Indicador económico |
| ENDUTIH 2024 | Brecha digital | Corrección sesgo PDIV |
| DENUE georreferenciado | Negocios por ubicación | Análisis económico local |

### 🟡 MEDIA prioridad (24 fuentes)
- ENIGH 2024 (ingresos/gastos hogares)
- ENVIPE 2025 (seguridad/victimización)
- Transparencia presupuestaria Nayarit
- Financiamiento partidos INE 2024

### 🟢 BAJA prioridad (8 fuentes)
- Histórico electoral 1988-2016
- Áreas protegidas IEEN Ecología
- Censos económicos 2018/2024

## Gaps de implementación
| Componente | Estado | Bloqueo |
|------------|--------|---------|
| Pipeline ETL silver/gold | ❌ No ejecutado | Dependencia datos faltantes |
| Neo4j Aura conexión | ❌ No implementado | Falta credenciales/instancia |
| Scraping Apify continuo | ❌ No implementado | Falta orquestador |
| NLP clasificación automática | ⚠️ Diseñado | Dependencia SAEIL |
| SNA detección CIB | ⚠️ Diseñado | Dependencia grafo Neo4j |

## Gaps de infraestructura
- No hay Docker/containerización
- No hay CI/CD (GitHub Actions, etc.)
- No hay orquestador de pipelines (Airflow/Prefect)
- No hay monitoreo/observabilidad
- No hay API REST para consumo de datos

---

# 7. EVALUACIÓN DE RIESGOS

## Riesgos operacionales
| ID | Riesgo | Probabilidad | Impacto | Mitigación sugerida |
|----|--------|--------------|---------|---------------------|
| OP-01 | Falta de persona clave (SAEIL) | Alta | Alto | Documentar NLP, crear runbooks |
| OP-02 | Datos en SSD externo se pierden | Media | Alto | Migrar inmediatamente a raw/ |
| OP-03 | API Apify no disponible | Baja | Medio | Implementar caché local, backoff |
| OP-04 | Límites cuota Gemini | Media | Medio | Implementar rate limiting, caché |

## Riesgos de datos
| ID | Riesgo | Probabilidad | Impacto |
|----|--------|--------------|---------|
| DAT-01 | 67 fuentes no descargadas | Cierta | Alto |
| DAT-02 | Datos electorales desactualizados | Media | Medio |
| DAT-03 | Sin integridad referencial Sección-INEGI | Media | Medio |
| DAT-04 | Datos redes sociales sin anonimización PII | Media | Alto (compliance) |

## Riesgos técnicos
| ID | Riesgo | Probabilidad | Impacto |
|----|--------|--------------|---------|
| TEC-01 | Directorios src/ vacíos bloquean avance | Cierta | Alto |
| TEC-02 | Neo4j Aura no probado en prod | Alta | Alto |
| TEC-03 | Pipeline ETL no probado con volumen real | Alta | Medio |
| TEC-04 | Sin tests automatizados | Cierta | Medio |

## Riesgos de continuidad del negocio [CTO]
- **Riesgo persona clave:** Conocimiento NLP/SNA parece residir en equipo SAEIL externo
- **Riesgo portabilidad:** Sin Docker, reproducción del entorno depende de manual de setup
- **Riesgo datos locales:** Provenance está en local, no en repositorio centralizado
- **Riesgo escalabilidad:** Arquitectura actual soporta un demarcación (Tepic), no múltiples

---

# 8. ROADMAP RECOMENDADO

## Fase 0: Validación e Inventario (1-2 semanas)
- [ ] Migrar datos SSD externo a `data/raw/`
- [ ] Ejecutar notebook 01_db_audit completamente
- [ ] Verificar SHA-256 de todos los archivos
- [ ] Documentar gaps restantes con prioridad

## Fase 1: Definición del Modelo de Datos (2 semanas)
- [ ] Implementar schemas Pandera para silver/
- [ ] Definir modelo de grafo Neo4j (nodos, relaciones, propiedades)
- [ ] Crear scripts de validación de integridad referencial
- [ ] Documentar reglas de negocio de enriquecimiento

## Fase 2: Persistencia Mínima Viable (2-3 semanas)
- [ ] Implementar ingestores en `src/ingestion/`
- [ ] Crear pipeline raw → silver (Polars + Pandera)
- [ ] Probar con subset de datos INE/IEEN
- [ ] Implementar Neo4j Aura (capa gratuita)

## Fase 3: Integridad y Observabilidad (2 semanas)
- [ ] Tests unitarios con pytest
- [ ] Logging estructurado (JSON)
- [ ] Pipeline de provenance automático
- [ ] Dashboard de calidad de datos

## Fase 4: Analítica / IA (3-4 semanas)
- [ ] Implementar NLP con Gemini (módulo src/analysis/nlp/)
- [ ] Construir grafo NetworkX → Neo4j
- [ ] Implementar Louvain communities
- [ ] Generar reportes automáticos MD

## Fase 5: Endurecimiento Productivo (2 semanas)
- [ ] Dockerización del entorno
- [ ] Orquestador Prefect para pipelines
- [ ] Backup automatizado de provenance
- [ ] Documentación de operación (runbooks)

---

# 9. EVALUACIÓN EJECUTIVA CTO

## Estado de madurez
- **Código:** Beta técnica (70%) — arquitectura sólida, implementación parcial
- **Datos:** Alfa operativa (60%) — muchos datos disponibles, sin integración
- **Documentación:** Producción (85%) — extensa y bien estructurada
- **Operación:** Prototipo (40%) — manual, sin automatización

## Nivel de riesgo general: 🟡 MEDIO-ALTO

## Capacidades evaluadas
| Capacidad | Estado | Notas |
|-----------|--------|-------|
| Evolución | 🟡 Limitada | Requiere saneamiento primero |
| Operación | 🔴 Débil | Manual, dependiente de conocimiento tácito |
| Delegación | 🔴 Difícil | Sin documentación de NLP/SNA suficiente |
| Escalabilidad | 🟡 Posible | Arquitectura permite, implementación no |
| Observabilidad | ❌ Ausente | Sin logs estructurados, métricas |

## Deuda técnica acumulada
- **Estructural:** Directorios src/ vacíos (alto riesgo)
- **De datos:** Silver/gold sin poblar (medio riesgo)
- **Documental:** NLP/SNA depende de conocimiento externo (alto riesgo)
- **Operacional:** Sin orquestador ni monitoreo (medio riesgo)

## Juicio general sobre viabilidad
El proyecto es **técnicamente viable y valioso** pero requiere inversión significativa en saneamiento antes de poder operar de forma profesional. El stack tecnológico es moderno y apropiado; la arquitectura de datos está bien pensada; la documentación es sobresaliente. Los principales bloqueos son operacionales, no técnicos.

## Veredicto semáforo CTO
🟡 **AMARILLO — Viable con riesgos importantes**

Recomendación: **Continuar con saneamiento progresivo** (Fases 0-3 del roadmap antes de cualquier feature nuevo).

---

# 10. DICTAMEN EJECUTIVO FINAL

## Qué es rescatable (Preservar)
- ✅ Arquitectura Medallon (raw/silver/gold)
- ✅ Sistema de provenance SHA-256
- ✅ Documentación técnica (AGENTS.md, ARCHITECTURE.md, DATA_INVENTORY.md)
- ✅ Notebook de auditoría (01_db_audit_nayarit.ipynb)
- ✅ Stack tecnológico (Polars, Gemini, NetworkX, GeoPandas)
- ✅ Datos INE/IEEN/INEGI cargados (1.7GB)

## Qué es valioso (Estabilizar)
- ⚠️ Pipeline ETL diseñado pero no implementado
- ⚠️ Configuración MCP servers
- ⚠️ Esquemas Pandera planificados
- ⚠️ Integraciones API configuradas

## Qué es peligroso (Descartar/Aislar)
- ❌ Directorios vacíos que generan confusión (si no se implementan pronto)
- ❌ Dependencia de SSD externo para datos críticos
- ❌ Conocimiento NLP/SNA no documentado

## Qué falta para tener control real
1. **Datos:** 67 fuentes pendientes, migración desde SSD
2. **Código:** Implementación de ingestion/, processing/, graph/
3. **Infraestructura:** Neo4j Aura activo, orquestador Prefect
4. **Operación:** Runbooks, tests, logging estructurado
5. **Equipo:** Transferencia de conocimiento SAEIL → Documentación

## Primera decisión de dirección técnica
**Decisión:** Implementar Fases 0-3 del roadmap antes de cualquier desarrollo de features NLP/SNA.

**Justificación:** Sin datos limpios en silver/gold y sin pipeline automatizado, no hay base sólida para analítica avanzada. El riesgo de construir sobre cimientos débiles es alto.

## Primera intervención concreta
**Acción inmediata:**
1. Copiar datos de `SERVER_TOOLBOX/centralinfo/` a `vigil/data/raw/social_media/`
2. Ejecutar `01_db_audit_nayarit.ipynb` y verificar integridad SHA-256
3. Crear issue tracker con los 67 gaps de datos priorizados
4. Asignar responsable para implementar `src/ingestion/` y `src/processing/`

---

## ANEXOS

### Anexo A: Inventario de Entidades Inferidas
| Entidad | Atributos clave | Relaciones |
|---------|-----------------|------------|
| Candidato | id, nombre, partido, cargo, aliases | 1:N Activo, 1:N Resultado |
| Activo Digital | id, plataforma, tipo, seguidores, url | N:1 Candidato, N:M Contenido |
| Sección Electoral | id, distrito_fed, distrito_loc, municipio, geo | 1:N Casilla, 1:1 INEGI |
| Casilla | clave, tipo, ubicación, lista_nominal | N:1 Sección, 1:N Resultado |
| Contenido Digital | id, texto, fecha, engagement | N:M Tema, N:1 Activo |
| Resultado Electoral | elección, votos, sección, candidato | N:1 Sección, N:1 Candidato |

### Anexo B: Datos Faltantes Prioritarios
1. AGEB INEGI manzana urbana 2020 (ALTA)
2. Cartografía SIGE INE 2024 secciones (ALTA)
3. Lista Nominal INE 2026 (ALTA)
4. Facebook posts/comments Feb 2026 en SSD (ALTA)
5. ENOE 2025 Nayarit (MEDIA)
6. ENDUTIH 2024 microdatos (MEDIA)
7. DENUE georreferenciado (MEDIA)
8. Meta Ad Library datos (MEDIA)

### Anexo C: Supuestos y Nivel de Confianza
| Conclusión | Tipo | Confianza | Evidencia |
|------------|------|-----------|-----------|
| Arquitectura sólida | Evidencia directa | Alta | ARCHITECTURE.md, pyproject.toml |
| Datos INE/IEEN cargados | Evidencia directa | Alta | provenance.jsonl (72 entradas) |
| Pipeline no ejecutado | Inferencia fuerte | Alta | silver/, gold/ vacíos |
| NLP depende de SAEIL | Inferencia fuerte | Media | AGENTS.md menciona SAEIL, src/analysis/ vacío |
| Neo4j no implementado | Evidencia directa | Alta | .env.example configura pero no hay código |
| Datos Facebook en SSD | Evidencia directa | Alta | DATA_INVENTORY.md lo documenta explícitamente |

### Anexo D: Activos Locales No Versionados
| Ubicación | Tipo | Tamaño | Prioridad de recuperación |
|-----------|------|--------|---------------------------|
| `SERVER_TOOLBOX/centralinfo/dataset_facebook-*-2026-02-20*.jsonl` | Datos sociales | ~MB desconocido | 🔴 CRÍTICA — migrar inmediatamente |
| `SERVER_TOOLBOX/SAIEL1/reports/` | Reportes previos | Desconocido | 🟡 Media — copiar como referencia |
| `SERVER_TOOLBOX/SAIEL1/engine/core/pdiv_calculator*` | Código SAEIL | Desconocido | 🟡 Media — evaluar reuso |

### Anexo E: Riesgos de Portabilidad
| Riesgo | Descripción | Mitigación |
|--------|-------------|------------|
| Entorno Python | Dependencia de .venv local | Crear requirements.txt preciso (✅ hecho) |
| Datos locales | 1.7GB en raw/ no versionado | Documentar reproducción (✅ DATA_DOWNLOAD_GUIDE.md) |
| Secrets | .env no compartido | .env.example completo (✅ hecho) |
| MCP Toolbox | Binario no versionado | Documentar descarga o eliminar dependencia |
| Neo4j Aura | Instancia cloud personal | Documentar creación de instancia gratuita |

### Anexo F: Checklist Próxima Intervención
- [ ] Migrar datos Facebook desde SSD externo
- [ ] Ejecutar auditoría completa (notebook 01)
- [ ] Crear instancia Neo4j Aura gratuita
- [ ] Implementar src/ingestion/ingest_ine.py
- [ ] Implementar src/processing/clean_electoral.py
- [ ] Poblar silver/electoral/ con datos INE/IEEN limpios
- [ ] Crear tests unitarios para validación Pandera
- [ ] Documentar en AGENTS.md el pipeline implementado

---

# ACTUALIZACIÓN POST-ANÁLISIS (2026-06-03)

Hallazgos descubiertos después de la generación inicial del reporte:

## 1. Doble Procedencia de Datos Confirmada [EVIDENCIA DIRECTA]

Análisis del notebook `02_download_ine.ipynb` y timestamps de filesystem confirman:

| Fuente | Archivos | Método | Timestamp |
|--------|----------|--------|-----------|
| **Windsurf/Web** | PREP 2017 (8 CSVs), Cómputos 2021/2024 (4 ZIPs + 2 CSVs extraídos) | `httpx.AsyncClient` | 2026-06-01 19:27-20:22 |
| **SSD Externo** | IEEN (11 archivos), INEGI (5 archivos), Geo (10 archivos), Work (19 archivos) | Migración manual/rsync | 2026-05-30 a 2026-06-01 |

**Impacto:** El provenance.jsonl no distingue entre datos descargados vía web vs migrados desde SSD, lo que limita la trazabilidad completa.

## 2. Activos Descubiertos en `/home/fnfrater/Escritorio/dbarchives/` [EVIDENCIA DIRECTA]

| Archivo | Tamaño | Estado | Acción Tomada |
|---------|--------|--------|---------------|
| `Cartografía Nayarit PSI y PLRAD (CORTE LOCAL)_Fecha de corte 14-Septiembre-2023` | 663MB | **NO INCLUIDO** en vigil original | ✅ MIGRADO a `data/raw/NAYARIT_DB_RAW/geo/` |
| `ods_masivo_*.zip` (4 archivos) | 7MB total | Datos ODS nacionales | ✅ MIGRADO a `data/raw/NAYARIT_DB_RAW/ods_nacional/` |
| `Naydatabases.txt` | 49KB | Duplicado en raíz Escritorio | ❌ NO MIGRADO (ya existe) |
| `DISTRITO_05-20260530T222545Z` | 50MB | Cartografía distrito específico | ❌ NO MIGRADO (según instrucción) |
| PDFs normativos (18 archivos) | Variable | Documentación legal | ❌ NO MIGRADO (según instrucción) |

## 3. Tareas Pendientes Identificadas

### Tarea CRÍTICA: Curación de Datos ODS Nacional
**Descripción:** Los 4 archivos `ods_masivo_*.zip` contienen datos de Objetivos de Desarrollo Sostenible a nivel **nacional**, no filtrados para Nayarit.

**Acciones requeridas:**
- [ ] Descomprimir ZIPs y explorar estructura
- [ ] Identificar campo de entidad/clave geográfica
- [ ] Filtrar registros para Nayarit (entidad 18)
- [ ] Transformar a formato consistente con INEGI
- [ ] Generar provenance para datos curados

**Prioridad:** 🟡 MEDIA — enriquecimiento valioso pero requiere trabajo de curación significativo

### Tarea MEDIA: Distinguir Procedencia en Provenance
**Descripción:** Agregar campo `source_type` a `provenance.jsonl` para distinguir:
- `web_download` — descargado por Windsurf vía HTTP
- `ssd_migration` — migrado desde SERVER_TOOLBOX
- `manual_import` — copiado manualmente

---

**Fin del Reporte de Due Diligence**  
*Documento generado por panel de expertos (CTO, Data Architect, Auditor de Producto)*  
*Mandato: Análisis exhaustivo para toma de decisiones de dirección técnica*  
*Actualizado: 2026-06-03 con hallazgos post-análisis*
