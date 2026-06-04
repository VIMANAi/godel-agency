"""
CRATE LOGIC: saiel.data_anonymizer
Pipeline de ingesta de datos con anonimización y validación robusta.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SocialMediaRecord(BaseModel):
    """Schema Pydantic para validación de datos (Cratizado)"""

    id: str = Field(..., description="ID único del registro")
    source: str = Field(..., description="Fuente de datos")
    text: str = Field(..., min_length=3, max_length=5000)
    date: str = Field(..., description="ISO 8601")
    user: Optional[str] = None
    candidate: Optional[str] = None
    anonymized: bool = Field(default=False)
    quality_score: float = Field(default=1.0, ge=0.0, le=1.0)


def anonymize_user(username: str) -> str:
    """Ejemplo de lógica de anonimización inyectada en el Crate"""
    import hashlib

    if not username:
        return "anonymous"
    return hashlib.sha256(username.encode()).hexdigest()[:12]
