"""
BIGQUERY ADAPTER: SAIEL INTELLIGENCE
Módulo para persistencia de datos analíticos en BigQuery.
"""

import pandas as pd
from google.cloud import bigquery


class BigQueryAdapter:
    def __init__(self, project_id=None):
        self.client = bigquery.Client(project=project_id)
        self.dataset_id = f"{self.client.project}.saiel_intel"
        self.table_id = f"{self.dataset_id}.pdiv_results"

    def setup_schema(self):
        """Crea el dataset y la tabla si no existen."""
        # 1. Dataset
        dataset = bigquery.Dataset(self.dataset_id)
        dataset.location = "us-central1"
        try:
            self.client.get_dataset(self.dataset_id)
            print(f"Dataset {self.dataset_id} ya existe.")
        except:
            self.client.create_dataset(dataset, timeout=30)
            print(f"Dataset {self.dataset_id} creado.")

        # 2. Tabla
        schema = [
            bigquery.SchemaField("candidato", "STRING"),
            bigquery.SchemaField("pdiv_score", "FLOAT"),
            bigquery.SchemaField("sentimiento_score", "FLOAT"),
            bigquery.SchemaField("volumen_score", "FLOAT"),
            bigquery.SchemaField("engagement_score", "FLOAT"),
            bigquery.SchemaField("crecimiento_score", "FLOAT"),
            bigquery.SchemaField("region", "STRING"),
            bigquery.SchemaField("fecha_calculo", "TIMESTAMP"),
        ]
        table = bigquery.Table(self.table_id, schema=schema)
        try:
            self.client.get_table(self.table_id)
            print(f"Tabla {self.table_id} ya existe.")
        except:
            self.client.create_table(table)
            print(f"Tabla {self.table_id} creada.")

    def upload_results(self, df: pd.DataFrame):
        """Sube un DataFrame a BigQuery."""
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND",
        )
        job = self.client.load_table_from_dataframe(df, self.table_id, job_config=job_config)
        job.result()
        print(f"Cargadas {len(df)} filas en {self.table_id}.")


if __name__ == "__main__":
    adapter = BigQueryAdapter()
    adapter.setup_schema()
