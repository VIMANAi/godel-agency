"""
Security Layer — Módulo de seguridad y protección de datos
Exporta hooks, gateway y utilidades de seguridad.
"""

from .hooks import (
    SecurityHook,
    CommandContext,
    CommandRisk,
    check_command,
)

from .gateway import (
    SecurityGateway,
    PIICategory,
    PIIFilterResult,
    validate_payload,
    redact_pii,
)

__all__ = [
    "SecurityHook",
    "CommandContext",
    "CommandRisk",
    "check_command",
    "SecurityGateway",
    "PIICategory",
    "PIIFilterResult",
    "validate_payload",
    "redact_pii",
]
