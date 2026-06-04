# Platform (Cloud-First Pipeline)

`platform/` define la ruta productiva de ejecución por capas para GCP, desacoplada de artefactos legacy.

## Capas

1. **acquisition/**: conectores y jobs de captura (social, documental, batch).
2. **normalization/**: estandarización, tipado, deduplicación y anonimización (silver).
3. **enrichment/**: calidad de datos, clasificación, extracción semántica y metadatos.
4. **embedding/**: chunking semántico y generación de embeddings en Vertex.
5. **serving/**: exposición API/consultas para consumo analítico y operacional.
6. **audit/**: observabilidad, lineage, cumplimiento y evidencia forense.

## Contrato de datos

Ver `/platform/contracts/raw_silver_gold_contract.yaml`.

## Principios operativos

- Landing raw inmutable y versionado en GCS.
- Transformaciones reproducibles con separación estricta `raw/silver/gold`.
- Quality gates obligatorios antes de promover datos entre capas.
- Metadatos trazables por `doc_id`, `source`, `jurisdiction`, `version`, `ingestion_run_id`.
