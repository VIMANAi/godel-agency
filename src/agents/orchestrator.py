"""
Agent Orchestrator — Routing de especialistas y gestión de herramientas
Basado en godel-core/config/orchestrator.py de Antigravity
Adaptado para 3 especialistas Vigil: social_scraper, narrative_analyst, compliance_officer
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class SpecialistStatus(Enum):
    """Estados posibles de un especialista."""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class ToolType(Enum):
    """Tipos de herramientas disponibles."""
    # Colecta
    TOOL_COLLECT_DATA = "tool_collect_data"
    TOOL_LIST_DATA_FILES = "tool_list_data_files"
    
    # Análisis
    TOOL_RUN_SENSEMAKER = "tool_run_sensemaker"
    TOOL_RUN_SENTIMENT = "tool_run_sentiment"
    TOOL_READ_REPORT = "tool_read_report"
    
    # Compliance
    TOOL_CHECK_CRISIS = "tool_check_crisis"
    TOOL_REQUEST_EXECUTIVE_APPROVAL = "tool_request_executive_approval"
    
    # Memoria
    TOOL_QUERY_MEMORY = "tool_query_memory"
    TOOL_COMMIT_TO_MEMORY = "tool_commit_to_memory"


@dataclass
class SpecialistState:
    """Estado de un especialista."""
    name: str
    status: SpecialistStatus
    allowed_tools: List[ToolType]
    denied_tools: List[ToolType]
    last_activity: Optional[datetime] = None
    error_count: int = 0
    task_count: int = 0


@dataclass
class RoutingDecision:
    """Decisión de routing."""
    specialist: str
    confidence: float
    reasoning: str
    tools_allowed: List[ToolType]


class AgentOrchestrator:
    """
    Orquestador de agentes especialistas.
    
    Implementa routing inteligente y control de permisos de herramientas.
    Basado en Antigravity orchestrator.py, adaptaciones:
    - 3 especialistas principales para Vigil
    - Routing por keywords en español (dominio electoral mexicano)
    - Logging de decisiones
    """
    
    def __init__(self):
        """Inicializa el orquestador con 3 especialistas."""
        self.specialists: Dict[str, SpecialistState] = {
            "social_scraper": SpecialistState(
                name="social_scraper",
                status=SpecialistStatus.IDLE,
                allowed_tools=[
                    ToolType.TOOL_COLLECT_DATA,
                    ToolType.TOOL_LIST_DATA_FILES,
                ],
                denied_tools=[
                    ToolType.TOOL_RUN_SENSEMAKER,
                    ToolType.TOOL_READ_REPORT,
                    ToolType.TOOL_CHECK_CRISIS,
                    ToolType.TOOL_RUN_SENTIMENT,
                    ToolType.TOOL_COMMIT_TO_MEMORY,
                ],
            ),
            "narrative_analyst": SpecialistState(
                name="narrative_analyst",
                status=SpecialistStatus.IDLE,
                allowed_tools=[
                    ToolType.TOOL_RUN_SENSEMAKER,
                    ToolType.TOOL_READ_REPORT,
                    ToolType.TOOL_RUN_SENTIMENT,
                    ToolType.TOOL_QUERY_MEMORY,
                ],
                denied_tools=[
                    ToolType.TOOL_COLLECT_DATA,
                    ToolType.TOOL_COMMIT_TO_MEMORY,
                ],
            ),
            "compliance_officer": SpecialistState(
                name="compliance_officer",
                status=SpecialistStatus.IDLE,
                allowed_tools=[
                    ToolType.TOOL_CHECK_CRISIS,
                    ToolType.TOOL_REQUEST_EXECUTIVE_APPROVAL,
                    ToolType.TOOL_QUERY_MEMORY,
                ],
                denied_tools=[
                    ToolType.TOOL_COLLECT_DATA,
                    ToolType.TOOL_RUN_SENTIMENT,
                    ToolType.TOOL_RUN_SENSEMAKER,
                    ToolType.TOOL_COMMIT_TO_MEMORY,
                ],
            ),
        }
        
        self.routing_history: List[Dict[str, Any]] = []
        self._setup_routing_heuristics()
    
    def _setup_routing_heuristics(self):
        """Configura heurísticas de routing por dominio/query."""
        # Keywords para cada especialista (en español, contexto electoral)
        self.routing_keywords = {
            "social_scraper": {
                "domains": ["social", "media", "scraper", "colecta", "recoleccion", "scraping"],
                "actions": [
                    "recolectar", "colectar", "scrape", "descargar posts",
                    "obtener datos", "extraer informacion", "bajar datos",
                    "facebook", "instagram", "twitter", "redes sociales",
                ],
            },
            "narrative_analyst": {
                "domains": ["narrative", "analisis", "sentimiento", "narrativa"],
                "actions": [
                    "analizar", "sensemaker", "sentiment", "narrativa",
                    "tendencias", "temas", "discurso", "mensajes",
                    "opinion publica", "percepcion", "narrativas politicas",
                ],
            },
            "compliance_officer": {
                "domains": ["compliance", "crisis", "legal", "regulacion"],
                "actions": [
                    "revisar crisis", "check crisis", "validar", "aprobar",
                    "cumplimiento", "legal", "regulatorio", "riesgo",
                    "alerta", "incidente", "escandalo", "controversia",
                ],
            },
        }
    
    def route_query(self, domain: str, query: str) -> RoutingDecision:
        """
        Determina qué especialista debe manejar una consulta.
        
        Args:
            domain: Dominio de la consulta (e.g., "social", "narrative")
            query: Texto de la consulta
        
        Returns:
            RoutingDecision con especialista asignado y confianza
        """
        domain_lower = domain.lower()
        query_lower = query.lower()
        combined = f"{domain_lower} {query_lower}"
        
        scores = {}
        
        # Calcular score para cada especialista
        for specialist_name, keywords in self.routing_keywords.items():
            score = 0.0
            
            # Puntaje por dominio
            for domain_kw in keywords["domains"]:
                if domain_kw in domain_lower:
                    score += 0.4
            
            # Puntaje por acciones en query
            for action_kw in keywords["actions"]:
                if action_kw in query_lower:
                    score += 0.3
            
            # Bonus si hay múltiples matches
            if score > 0.5:
                score += 0.2
            
            scores[specialist_name] = min(score, 1.0)
        
        # Seleccionar mejor match
        best_specialist = max(scores, key=scores.get)
        best_score = scores[best_specialist]
        
        # Si ninguno tiene score decente, default a narrative_analyst
        if best_score < 0.2:
            best_specialist = "narrative_analyst"
            best_score = 0.5
            reasoning = "Default routing: no clear domain match"
        else:
            reasoning = f"Matched keywords for {best_specialist} (score: {best_score:.2f})"
        
        # Actualizar estado
        self.specialists[best_specialist].last_activity = datetime.now()
        self.specialists[best_specialist].task_count += 1
        
        decision = RoutingDecision(
            specialist=best_specialist,
            confidence=best_score,
            reasoning=reasoning,
            tools_allowed=self.specialists[best_specialist].allowed_tools,
        )
        
        # Loggear
        self.routing_history.append({
            "timestamp": datetime.now().isoformat(),
            "domain": domain,
            "query": query[:50],  # Truncado
            "decision": decision,
        })
        
        logger.info(f"[ORCHESTRATOR] Routed to '{best_specialist}' with confidence {best_score:.2f}")
        
        return decision
    
    def can_use_tool(self, specialist_name: str, tool_name: str) -> bool:
        """
        Verifica si un especialista puede usar una herramienta.
        
        Args:
            specialist_name: Nombre del especialista
            tool_name: Nombre de la herramienta (con o sin prefijo 'tool_')
        
        Returns:
            True si tiene permiso, False si está denegado
        """
        if specialist_name not in self.specialists:
            logger.warning(f"[ORCHESTRATOR] Unknown specialist: {specialist_name}")
            return False
        
        specialist = self.specialists[specialist_name]
        
        # Normalizar nombre de herramienta
        if not tool_name.startswith("tool_"):
            tool_name = f"tool_{tool_name}"
        
        try:
            tool_enum = ToolType(tool_name)
        except ValueError:
            logger.warning(f"[ORCHESTRATOR] Unknown tool: {tool_name}")
            return False
        
        # Verificar denied primero (más restrictivo)
        if tool_enum in specialist.denied_tools:
            logger.warning(
                f"[ORCHESTRATOR] DENIED: {specialist_name} cannot use {tool_name}"
            )
            return False
        
        # Verificar allowed
        if tool_enum in specialist.allowed_tools:
            return True
        
        # Default: denegar si no está explícitamente permitido
        logger.warning(
            f"[ORCHESTRATOR] DENIED (implicit): {tool_name} not in allowed list for {specialist_name}"
        )
        return False
    
    def validate_tool_chain(
        self,
        specialist_name: str,
        tool_chain: List[str]
    ) -> Tuple[bool, Optional[str]]:
        """
        Valida una cadena de herramientas.
        
        Args:
            specialist_name: Especialista que ejecuta
            tool_chain: Lista de herramientas en orden
        
        Returns:
            (valid: bool, error_message: Optional[str])
        """
        for i, tool in enumerate(tool_chain):
            if not self.can_use_tool(specialist_name, tool):
                return False, f"Step {i+1}: '{tool}' denied for {specialist_name}"
        
        return True, None
    
    def get_specialist_status(self, name: str) -> Optional[SpecialistState]:
        """Retorna estado de un especialista."""
        return self.specialists.get(name)
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Retorna estado de todos los especialistas."""
        return {
            name: {
                "status": spec.status.value,
                "allowed_tools": [t.value for t in spec.allowed_tools],
                "denied_tools": [t.value for t in spec.denied_tools],
                "task_count": spec.task_count,
                "error_count": spec.error_count,
                "last_activity": spec.last_activity.isoformat() if spec.last_activity else None,
            }
            for name, spec in self.specialists.items()
        }
    
    def set_specialist_status(self, name: str, status: SpecialistStatus):
        """Actualiza estado de un especialista."""
        if name in self.specialists:
            self.specialists[name].status = status
            logger.info(f"[ORCHESTRATOR] {name} status changed to {status.value}")


# Instancia global
default_orchestrator = AgentOrchestrator()


def route_query(domain: str, query: str) -> RoutingDecision:
    """Función de conveniencia."""
    return default_orchestrator.route_query(domain, query)


def can_use_tool(specialist: str, tool: str) -> bool:
    """Función de conveniencia."""
    return default_orchestrator.can_use_tool(specialist, tool)
