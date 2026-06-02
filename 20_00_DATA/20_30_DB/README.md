# Gobernanza de Datos y Persistencia Relacional: SAIEL

Este directorio contiene el diseño y las instrucciones de operación para la persistencia relacional estructurada de **SAIEL** (Sistema de Análisis de Inteligencia Electoral Local).

Siguiendo principios de **Separation of Concerns (SoC)**, aislamos los datos del código activo y formalizamos la persistencia en dos modos (Dual Processing):

1. **🔒 Modo Bunker (Local Local)**: Almacenamiento en base de datos local SQLite (`saiel_local.db`).
2. **☁️ Modo Escalabilidad (Cloud)**: Sincronización masiva de resultados en **Google BigQuery** (Dataset `saiel_intel`, tabla `pdiv_results`).

---

## 📐 1. Modelo Conceptual Relacional

El esquema de base de datos definido en `schema.sql` organiza la información en cuatro tablas altamente indexadas:

```
                      +-------------------+
                      |    comentarios    | (Ingesta y Scraping Limpio)
                      +-------------------+
                      | PK | id           | <----+
                      |    | text         |      |
                      |    | candidate    |      |
                      |    | date         |      |
                      |    | ...          |      |
                      +-------------------+      |
                                |                |
                                | 1:1            |
                                v                |
                      +-------------------+      |
                      |   rs_sentimiento  | (Inferencia Analítica)
                      +-------------------+      |
                      | FK | comentario_id| -----+
                      |    | label        |
                      |    | score        |
                      |    | ...          |
                      +-------------------+

+-----------------------------------------+      +-------------------+
|               pdiv_scores               |      |   alertas_crisis  |
+-----------------------------------------+      +-------------------+
| PK | id                                 |      | PK | id           |
|    | candidato                          |      |    | severidad    |
|    | pdiv_score                         |      |    | mensaje      |
|    | fecha_calculo                      |      |    | status       |
+-----------------------------------------+      +-------------------+
```

---

## 🚀 2. Inicialización de la Base de Datos Local

Para inicializar la base de datos SQLite y aplicar el esquema definido, ejecute el siguiente comando desde la raíz del proyecto:

```bash
sqlite3 data/db/saiel_local.db < data/db/schema.sql
```

Alternativamente, el pipeline de SAIEL creará e inicializará automáticamente la base de datos en tiempo de ejecución si detecta que no existe.

---

## 📥 3. Script de Importación de Históricos JSON/JSONL

Para migrar sus conjuntos de datos planos existentes (ej. `dataset_facebook-comments-scraper...jsonl` o `docscrape.jsonl`) a la nueva base de datos relacional indexada, puede utilizar el siguiente script de utilidad en Python:

```python
# src/deploy/import_legacy_data.py
import sqlite3
import json
from pathlib import Path

DB_PATH = Path("data/db/saiel_local.db")
JSONL_PATH = Path("data/raw/dataset_facebook-comments-scraper_2026-02-20_18-34-36-980.jsonl")

def migrate_jsonl_to_sqlite():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Asegurar esquema
    with open("data/db/schema.sql", "r") as f:
        cursor.executescript(f.read())
        
    print(f"Migrando datos desde {JSONL_PATH.name}...")
    
    count = 0
    with open(JSONL_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line)
            
            # Estandarizar
            record_id = item.get("id", item.get("node_id", f"hash_{count}"))
            text = item.get("text", item.get("commentText", item.get("message", "")))
            if not text:
                continue
                
            cursor.execute("""
                INSERT OR IGNORE INTO comentarios (id, source, text, user, likes, date, collected_at, anonymized)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'), 0)
            """, (
                record_id,
                item.get("source", "facebook"),
                text,
                item.get("user", item.get("ownerUsername", "unknown")),
                item.get("likes", item.get("likesCount", 0)),
                item.get("date", item.get("timestamp", datetime.now().isoformat()))
            ))
            count += 1
            
    conn.commit()
    conn.close()
    print(f"✅ Migración completada. {count} registros importados.")

if __name__ == "__main__":
    migrate_jsonl_to_sqlite()
```

---

## ☁️ 4. Escalabilidad e Integración con BigQuery

Cuando la variable de entorno `SAIEL_ENGINE_MODE` se configura en `cloud`, el adaptador `src/core/bq_adapter.py` gestiona la persistencia de forma nativa en la nube.

Las métricas agregadas de PDIV calculadas de forma local o en Cloud Run se envían directamente a la tabla analítica en Google Cloud:
* **Gobernanza de Datos**: Cumple estrictamente con la anonimización de PII previa a la subida, garantizando cumplimiento regulatorio **LGPDPPSO** y **GDPR**.
* **Idempotencia**: Las cargas a BigQuery se realizan bajo el método `WRITE_APPEND`, pero con una clave única combinada de `fecha_calculo + region + candidato` para evitar colisiones semánticas.
