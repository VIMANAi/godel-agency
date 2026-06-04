"""
Tests de Seguridad — Cobertura para hooks, gateway y orchestrator
Basado en casos de uso de Vigil y datos de encuestas Rubrum
"""

import pytest
import asyncio
from pathlib import Path

# Asegurar que src/ esté en path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from security.hooks import SecurityHook, CommandContext, CommandRisk, check_command
from security.gateway import SecurityGateway, PIICategory, validate_payload, redact_pii
from agents.orchestrator import (
    AgentOrchestrator, 
    SpecialistStatus, 
    ToolType,
    route_query,
    can_use_tool,
)


# ============================================================================
# TESTS: Security Hooks
# ============================================================================

class TestSecurityHooks:
    """Tests para hooks de aprobación de comandos."""
    
    @pytest.fixture
    def hook(self):
        return SecurityHook(interactive=False, auto_approve_low=True)
    
    @pytest.mark.asyncio
    async def test_auto_approve_low_risk(self, hook):
        """Comandos de bajo riesgo se auto-aprueban."""
        context = CommandContext(
            command_type="read_file",
            target_path="/some/path.txt"
        )
        approved, reason = await hook.check_command(context)
        assert approved is True
        assert reason is None
    
    @pytest.mark.asyncio
    async def test_block_sensitive_path(self, hook):
        """Paths sensibles son bloqueados."""
        context = CommandContext(
            command_type="read_file",
            target_path="/home/user/.ssh/id_rsa"
        )
        approved, reason = await hook.check_command(context)
        assert approved is False
        assert "sensitive path" in reason.lower()
    
    @pytest.mark.asyncio
    async def test_log_high_risk_command(self, hook):
        """Comandos de alto riesgo se loggean."""
        context = CommandContext(
            command_type="write_to_file",
            target_path="/tmp/test.txt"
        )
        approved, reason = await hook.check_command(context)
        # En modo no-interactivo, se aprueba pero se loggea
        assert approved is True
        
        summary = hook.get_approval_summary()
        assert summary["total_commands_checked"] == 1
        assert summary["auto_approved"] == 1
    
    @pytest.mark.asyncio
    async def test_block_delete_critical(self, hook):
        """Delete es comando crítico."""
        context = CommandContext(
            command_type="delete",
            target_path="/tmp/file.txt"
        )
        approved, reason = await hook.check_command(context)
        # Se aprueba en modo no-interactivo pero se loggea como crítico
        assert approved is True
        assert hook.approval_log[-1]["risk"] == "critical"


# ============================================================================
# TESTS: Security Gateway (PII Filtering)
# ============================================================================

class TestSecurityGateway:
    """Tests para filtrado de PII."""
    
    @pytest.fixture
    def gateway(self):
        return SecurityGateway(strict_mode=False)
    
    def test_block_email(self, gateway):
        """Emails son detectados y bloqueados."""
        result = gateway.validate_payload(
            "Contact me at john.doe@email.com for details",
            context="social_media"
        )
        assert not result.is_clean
        assert any(v["category"] == "email" for v in result.violations)
    
    def test_block_phone(self, gateway):
        """Teléfonos mexicanos son detectados."""
        result = gateway.validate_payload(
            "Call me at +52 311 123 4567",
            context="social_media"
        )
        assert not result.is_clean
        assert any(v["category"] == "phone" for v in result.violations)
    
    def test_block_curp(self, gateway):
        """CURP es siempre bloqueado."""
        result = gateway.validate_payload(
            "Mi CURP es ABC123456HDFRLR09",
            context="survey"
        )
        assert not result.is_clean
        assert any(v["category"] == "curp" for v in result.violations)
    
    def test_allow_public_candidates(self, gateway):
        """Nombres de candidatos públicos NO son PII."""
        # Geraldine Ponce es candidata pública en Tepic
        result = gateway.validate_payload(
            "Geraldine Ponce lidera intención de voto con 37.6%",
            context="survey"
        )
        assert result.is_clean, f"Violations: {result.violations}"
    
    def test_allow_ivideliza_reyes(self, gateway):
        """Ivideliza Reyes es candidata pública."""
        result = gateway.validate_payload(
            "Ivideliza Reyes con 66.7% en gubernatura",
            context="survey"
        )
        assert result.is_clean
    
    def test_allow_luis_zamora(self, gateway):
        """Luis Zamora es candidato público."""
        result = gateway.validate_payload(
            "Luis Zamora sube a 33.3% en Tepic",
            context="survey"
        )
        assert result.is_clean
    
    def test_block_private_name(self, gateway):
        """Nombres de personas privadas deben ser cuidados."""
        # Juan Pérez no está en lista de candidatos
        result = gateway.validate_payload(
            "Juan Pérez me dijo que votaría por Geraldine",
            context="social_media"
        )
        # Nota: Esto es un caso borde - "Juan Pérez" podría ser privado
        # Pero el gateway actual no tiene lista de nombres privados
        # Por ahora, permitimos pero loggeamos
        pass  # Test placeholder para mejora futura
    
    def test_block_restricted_keywords(self, gateway):
        """Keywords restringidas bloquean payload."""
        result = gateway.validate_payload(
            "La lista_nominal tiene 500,000 registros",
            context="internal"
        )
        assert not result.is_clean
        assert any("lista_nominal" in v.get("keyword", "") for v in result.violations)
    
    def test_redact_pii(self, gateway):
        """Redactar remueve PII manteniendo contexto."""
        text = "Contact: john@email.com or call +52 311 123 4567"
        redacted = gateway.redact_pii(text)
        
        assert "john@email.com" not in redacted
        assert "+52 311 123 4567" not in redacted
        assert "[EMAIL_REDACTED]" in redacted
        assert "[PHONE_REDACTED]" in redacted
    
    def test_redact_preserves_candidates(self, gateway):
        """Redactar no afecta nombres de candidatos."""
        text = "Geraldine Ponce contact: geraldine@partido.com"
        redacted = gateway.redact_pii(text)
        
        assert "Geraldine Ponce" in redacted  # Nombre preservado
        assert "geraldine@partido.com" not in redacted  # Email redactado
    
    def test_federation_rules(self, gateway):
        """Reglas de federación entre organizaciones."""
        # No federar datos secretos
        permitted, reason = gateway.can_federate_to(
            "vigil", "external", "secret"
        )
        assert not permitted
        assert "secret" in reason.lower()
        
        # Federar datos públicos
        permitted, reason = gateway.can_federate_to(
            "vigil", "external", "public"
        )
        assert permitted
    
    def test_contextual_false_positive(self, gateway):
        """Contexto puede evitar falsos positivos."""
        # "email del partido" es contexto público
        result = gateway.validate_payload(
            "El email del partido es público: contacto@partido.gob.mx",
            context="public"
        )
        # Este test es tricky - el email aún es PII técnicamente
        # Pero el contexto "público" podría influir
        pass  # Placeholder para mejora


# ============================================================================
# TESTS: Agent Orchestrator
# ============================================================================

class TestAgentOrchestrator:
    """Tests para routing y permisos de especialistas."""
    
    @pytest.fixture
    def orchestrator(self):
        return AgentOrchestrator()
    
    def test_route_social_scraper(self, orchestrator):
        """Routing para tareas de colecta social."""
        decision = orchestrator.route_query(
            domain="social",
            query="recolectar posts de facebook"
        )
        assert decision.specialist == "social_scraper"
        assert decision.confidence > 0.5
    
    def test_route_narrative_analyst(self, orchestrator):
        """Routing para análisis narrativo."""
        decision = orchestrator.route_query(
            domain="narrative",
            query="analizar sentimiento de comentarios"
        )
        assert decision.specialist == "narrative_analyst"
    
    def test_route_compliance_officer(self, orchestrator):
        """Routing para revisión de crisis."""
        decision = orchestrator.route_query(
            domain="compliance",
            query="check crisis en redes"
        )
        assert decision.specialist == "compliance_officer"
    
    def test_route_default(self, orchestrator):
        """Routing default cuando no hay match claro."""
        decision = orchestrator.route_query(
            domain="unknown",
            query="hacer algo"
        )
        assert decision.specialist == "narrative_analyst"  # Default
    
    def test_social_scraper_denied_sensemaker(self, orchestrator):
        """Social scraper NO puede usar sensemaker."""
        assert not orchestrator.can_use_tool("social_scraper", "tool_run_sensemaker")
    
    def test_social_scraper_allowed_collect(self, orchestrator):
        """Social scraper SÍ puede colectar datos."""
        assert orchestrator.can_use_tool("social_scraper", "tool_collect_data")
    
    def test_narrative_denied_collect(self, orchestrator):
        """Narrative analyst NO puede colectar."""
        assert not orchestrator.can_use_tool("narrative_analyst", "tool_collect_data")
    
    def test_narrative_allowed_sensemaker(self, orchestrator):
        """Narrative analyst SÍ puede usar sensemaker."""
        assert orchestrator.can_use_tool("narrative_analyst", "tool_run_sensemaker")
    
    def test_compliance_allowed_crisis(self, orchestrator):
        """Compliance officer puede revisar crisis."""
        assert orchestrator.can_use_tool("compliance_officer", "tool_check_crisis")
    
    def test_compliance_denied_collect(self, orchestrator):
        """Compliance officer NO puede colectar datos."""
        assert not orchestrator.can_use_tool("compliance_officer", "tool_collect_data")
    
    def test_validate_tool_chain_success(self, orchestrator):
        """Cadena de herramientas válida."""
        valid, error = orchestrator.validate_tool_chain(
            "narrative_analyst",
            ["tool_query_memory", "tool_run_sentiment", "tool_read_report"]
        )
        assert valid is True
        assert error is None
    
    def test_validate_tool_chain_fail(self, orchestrator):
        """Cadena con herramienta denegada."""
        valid, error = orchestrator.validate_tool_chain(
            "narrative_analyst",
            ["tool_query_memory", "tool_collect_data"]  # collect_data denied
        )
        assert valid is False
        assert "denied" in error.lower()
    
    def test_unknown_specialist_denied(self, orchestrator):
        """Especialista desconocido no tiene permisos."""
        assert not orchestrator.can_use_tool("unknown_agent", "tool_collect_data")
    
    def test_unknown_tool_denied(self, orchestrator):
        """Herramienta desconocida es denegada."""
        assert not orchestrator.can_use_tool("social_scraper", "tool_unknown")
    
    def test_get_status(self, orchestrator):
        """Obtener estado de todos los especialistas."""
        status = orchestrator.get_all_status()
        
        assert "social_scraper" in status
        assert "narrative_analyst" in status
        assert "compliance_officer" in status
        
        for spec_status in status.values():
            assert "allowed_tools" in spec_status
            assert "denied_tools" in spec_status


# ============================================================================
# TESTS: Integración
# ============================================================================

class TestIntegration:
    """Tests de integración entre componentes."""
    
    @pytest.mark.asyncio
    async def test_full_pipeline_social_collection(self):
        """Pipeline completo: colecta social → gateway → hook."""
        # 1. Routing decide social_scraper
        decision = route_query("social", "recolectar posts facebook")
        assert decision.specialist == "social_scraper"
        
        # 2. Verificar permisos
        assert can_use_tool("social_scraper", "tool_collect_data")
        
        # 3. Simular payload con posible PII
        payload = "Post: Me gusta Geraldine Ponce, contacto: test@email.com"
        result = validate_payload(payload, context="social_media")
        
        # Debe detectar email pero no el nombre de candidato
        assert not result.is_clean  # Email bloqueado
        assert any(v["type"] == "pattern" for v in result.violations)
    
    @pytest.mark.asyncio
    async def test_electoral_survey_processing(self):
        """Procesamiento de encuesta con datos de candidatos."""
        # Datos tipo Rubrum survey
        survey_data = """
        Gubernatura:
        - Ivideliza Reyes: 66.7%
        - Graciela Rodríguez: 60%
        
        Alcaldía Tepic:
        - Geraldine Ponce: 37.6%
        - Luis Zamora: 33.3%
        """
        
        result = validate_payload(survey_data, context="survey")
        
        # Todos los nombres son públicos, no debe haber violaciones
        assert result.is_clean, f"False positives: {result.violations}"
    
    @pytest.mark.asyncio  
    async def test_security_check_with_hook(self):
        """Hook de seguridad en operación de escritura."""
        approved, reason = await check_command(
            command_type="write_to_file",
            target_path="/tmp/results.json",
            payload={"data": "test"}
        )
        # En modo no-interactivo, se aprueba con logging
        assert approved is True


# ============================================================================
# Entry point para ejecución manual
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
