# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");

"""Conector Unificado de Base de Datos para RAG (ChromaDB local).

Este módulo proporciona interfaces reutilizables y livianas de Python para
inicializar, indexar y realizar consultas vectoriales sobre la base de datos
local y persistente Databases sin levantar servicios externos en segundo plano.
"""

import os
import sys
from pathlib import Path

# Ruta física persistente centralizada para almacenar vectores
def _get_db_path():
    env_path = os.environ.get("RAG_DB_PATH")
    if env_path:
        return env_path
    current = Path(__file__).resolve()
    for parent in current.parents:
        if parent.name == "Agency":
            sibling = parent.parent / "Databases" / "chromadb_store"
            return str(sibling)
    return os.path.join(os.path.expanduser("~"), "Desarrollo", "Databases", "chromadb_store")

DB_PATH = _get_db_path()

try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False


class RAGDatabaseConnector:
    """Clase unificada para interactuar de forma empotrada con ChromaDB local."""

    def __init__(self, path: str = DB_PATH):
        self.db_path = path
        self.client = None
        
        if not CHROMA_AVAILABLE:
            raise ImportError(
                "❌ Error: 'chromadb' no está instalado en el entorno virtual.\n"
                "Para solucionarlo, ejecuta:\n"
                "  uv pip install chromadb\n"
            )
            
        # Inicializar el cliente persistente local en disco
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.db_path)

    def get_collection(self, name: str):
        """Obtiene o crea una colección vectorial de forma segura."""
        if not self.client:
            raise RuntimeError("Cliente de ChromaDB no inicializado.")
        return self.client.get_or_create_collection(name=name)

    def index_data(self, collection_name: str, documents: list[str], metadatas: list[dict], ids: list[str]) -> bool:
        """Indexa textos y metadatos en la base de datos local RAG."""
        try:
            collection = self.get_collection(collection_name)
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            return True
        except Exception as e:
            print(f"❌ Error al indexar datos en RAG: {e}", file=sys.stderr)
            return False

    def search_similarity(self, collection_name: str, query_text: str, n_results: int = 3) -> dict | None:
        """Realiza una consulta semántica (búsqueda vectorial) sobre la colección."""
        try:
            collection = self.get_collection(collection_name)
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results
        except Exception as e:
            print(f"❌ Error al realizar consulta semántica en RAG: {e}", file=sys.stderr)
            return None


# Helper global rápido para importaciones directas
def get_rag_connector() -> RAGDatabaseConnector:
    """Retorna una instancia inicializada del conector unificado."""
    return RAGDatabaseConnector()
