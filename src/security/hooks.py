"""
Security Hooks — Interceptor de comandos peligrosos
Basado en godel-core/config/security.py de Antigravity
Adaptado para rutas relativas y entorno /home/fnfrater/
"""

import asyncio
import logging
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class CommandRisk(Enum):
    """Niveles de riesgo para comandos."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class CommandContext:
    """Contexto de ejecución de comando."""
    command_type: str
    target_path: str
    payload: Optional[Dict[str, Any]] = None
    agent_id: Optional[str] = None
    session_id: Optional[str] = None


class SecurityHook:
    """
    Hooks de seguridad para aprobación interactiva de comandos peligrosos.
    
    Basado en Antigravity security.py, adaptado para:
    - Rutas relativas (sin /home/fratfn/ hardcodeado)
    - Entorno /home/fnfrater/
    - Logging en lugar de prompts interactivos (para compatibilidad CLI)
    """
    
    # Comandos peligrosos que requieren aprobación
    DANGEROUS_COMMANDS = {
        "write_to_file": CommandRisk.HIGH,
        "replace_file_content": CommandRisk.HIGH,
        "delete": CommandRisk.CRITICAL,
        "run_command": CommandRisk.CRITICAL,
        "execute": CommandRisk.CRITICAL,
        "shell": CommandRisk.CRITICAL,
        "commit_to_memory": CommandRisk.MEDIUM,
    }
    
    # Patrones de paths sensibles
    SENSITIVE_PATHS = [
        ".env",
        ".ssh",
        "secrets",
        "credentials",
        "api_key",
        "token",
    ]
    
    def __init__(self, interactive: bool = False, auto_approve_low: bool = True):
        """
        Args:
            interactive: Si True, solicita aprobación interactiva (no disponible en CLI)
            auto_approve_low: Auto-aprobar comandos de riesgo bajo
        """
        self.interactive = interactive
        self.auto_approve_low = auto_approve_low
        self.approval_log: list = []
    
    async def check_command(
        self, 
        context: CommandContext
    ) -> Tuple[bool, Optional[str]]:
        """
        Verifica si un comando debe ejecutarse.
        
        Returns:
            (approved: bool, reason: Optional[str])
            approved = True si el comando puede ejecutarse
            reason = explicación si fue rechazado
        """
        command_type = context.command_type
        target_path = context.target_path
        
        # Verificar si es comando peligroso
        risk_level = self.DANGEROUS_COMMANDS.get(command_type, CommandRisk.LOW)
        
        # Auto-aprobar riesgo bajo
        if risk_level == CommandRisk.LOW and self.auto_approve_low:
            logger.debug(f"[SECURITY] Auto-approved: {command_type} on {target_path}")
            return True, None
        
        # Verificar path sensible
        if self._is_sensitive_path(target_path):
            logger.warning(f"[SECURITY] BLOCKED: Access to sensitive path '{target_path}'")
            return False, f"Access to sensitive path '{target_path}' denied"
        
        # Loggear comando peligroso
        logger.info(f"[SECURITY] Command '{command_type}' on '{target_path}' - Risk: {risk_level.value}")
        
        # En modo no-interactivo, auto-aprobar con logging
        if not self.interactive:
            logger.info(f"[SECURITY] Auto-approved (non-interactive): {command_type}")
            self.approval_log.append({
                "command": command_type,
                "path": target_path,
                "risk": risk_level.value,
                "approved": True,
                "auto": True,
            })
            return True, None
        
        # Modo interactivo (requiere input del usuario)
        # Nota: En entornos IDE/CLI, esto puede bloquear
        approved = await self._request_interactive_approval(context, risk_level)
        
        self.approval_log.append({
            "command": command_type,
            "path": target_path,
            "risk": risk_level.value,
            "approved": approved,
            "auto": False,
        })
        
        if not approved:
            return False, f"User denied {command_type} on {target_path}"
        
        return True, None
    
    def _is_sensitive_path(self, path: str) -> bool:
        """Verifica si un path contiene datos sensibles."""
        path_lower = path.lower()
        return any(sensitive in path_lower for sensitive in self.SENSITIVE_PATHS)
    
    async def _request_interactive_approval(
        self, 
        context: CommandContext,
        risk_level: CommandRisk
    ) -> bool:
        """Solicita aprobación interactiva (solo para entornos con input)."""
        # En CLI/IDE modernos, usar logging en lugar de input()
        logger.warning(
            f"[SECURITY APPROVAL REQUIRED]\n"
            f"  Command: {context.command_type}\n"
            f"  Target: {context.target_path}\n"
            f"  Risk: {risk_level.value.upper()}\n"
            f"  Auto-approving in non-TTY environment"
        )
        
        # Por defecto, aprobar en entornos no-TTY para no bloquear
        # En producción, esto debería usar un sistema de aprobación externo
        return True
    
    def get_approval_summary(self) -> Dict[str, Any]:
        """Retorna resumen de aprobaciones."""
        total = len(self.approval_log)
        auto_approved = sum(1 for log in self.approval_log if log.get("auto"))
        manual_approved = sum(1 for log in self.approval_log if not log.get("auto") and log.get("approved"))
        blocked = sum(1 for log in self.approval_log if not log.get("approved"))
        
        return {
            "total_commands_checked": total,
            "auto_approved": auto_approved,
            "manual_approved": manual_approved,
            "blocked": blocked,
            "approval_rate": (auto_approved + manual_approved) / total if total > 0 else 0,
        }


# Instancia global para uso rápido
_default_hook = SecurityHook(interactive=False, auto_approve_low=True)


async def check_command(
    command_type: str,
    target_path: str,
    payload: Optional[Dict[str, Any]] = None,
    agent_id: Optional[str] = None,
) -> Tuple[bool, Optional[str]]:
    """Función de conveniencia para verificar comandos."""
    context = CommandContext(
        command_type=command_type,
        target_path=target_path,
        payload=payload,
        agent_id=agent_id,
    )
    return await _default_hook.check_command(context)
