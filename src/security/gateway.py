"""
Security Gateway — Filtrado PII y federación A2A
Basado en godel-core/config/gateway.py de Antigravity
Adaptado para datos electorales (candidatos públicos vs PII real)
"""

import re
import logging
from typing import Tuple, Optional, Dict, List, Set
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class PIICategory(Enum):
    """Categorías de información personal identificable."""
    EMAIL = "email"
    PHONE = "phone"
    CURP = "curp"
    RFC = "rfc"
    INE_KEY = "ine_key"
    PASSWORD = "password"
    API_KEY = "api_key"
    TOKEN = "token"
    SECRET = "secret"
    ADDRESS = "address"
    PRIVATE_NAME = "private_name"  # Nombres de personas NO públicas


@dataclass
class PIIFilterResult:
    """Resultado del filtrado de PII."""
    is_clean: bool
    violations: List[Dict[str, str]] = field(default_factory=list)
    redacted_text: Optional[str] = None


class SecurityGateway:
    """
    Gateway de seguridad para filtrado de PII y federación entre organizaciones.
    
    CRÍTICO para Vigil: Distingue entre candidatos públicos (permitidos) y PII real (bloqueado).
    
    Basado en Antigravity gateway.py, adaptaciones:
    - Rutas relativas
    - Lista de candidatos públicos de Nayarit 2026
    - Keywords restringidas para datos electorales sensibles
    """
    
    # Keywords que indican datos sensibles
    RESTRICTED_KEYWORDS: Set[str] = {
        # Credenciales
        "secret", "password", "token", "api_key", "apikey",
        "private_key", "credentials", "auth_token",
        # Electoral México
        "ine_key", "clave_ine", "lista_nominal", "credencial_ine",
        "curp", "rfc", "ife",
        # Contacto privado
        "email", "correo", "telefono", "celular", "whatsapp",
        "domicilio", "direccion", "calle", "numero_interior",
        # Datos bancarios
        "cuenta_bancaria", "clabe", "tarjeta", "cvv",
    }
    
    # Candidatos públicos de Nayarit 2026 (NO filtrar como PII)
    PUBLIC_CANDIDATES: Set[str] = {
        # Gubernatura
        "ivideliza reyes", "ivideliza hernandez reyes",
        "graciela rodriguez", "graciela gonzalez rodriguez",
        "rosa maria carreón", "rosa maria carreon",
        # Alcaldía Tepic
        "geraldine ponce", "geraldine ponce de leon",
        "luis zamora", "luis zamora valdez",
        "octavio chaparro", "octavio chaparro de la torre",
        "angelica warmlander", "angelica warmlander sotelo",
        # Otros mencionados en encuestas
        "arturo dujaili", "arturo dujaili vega",
        "fidel cedillo", "fidel cedillo cedillo",
        "hugo gonzalez", "hugo gonzalez rubio",
        "jose maria lopez", "chema lopez",
        "enrique corona", "enrique corona yllades",
        "manuel peralta", "manuel peralta medina",
        "francisco corona", "pancho corona",
        "juan de dios santos", "juan de dios",
        "leticia torres", "leticia torres soto",
        "gustavo cuevas", "gustavo cuevas cuellar",
        "diego lizarraga", "diego lizarraga",
        "cesar gomez", "cesar gomez villalpando",
        "misael emilio", "misael emilio corral",
        "maria del consuelo", "consuelo lopez",
        "miguel angel", "miguel angel lopez",
        "martha rosa", "martha rosa silva",
        "jorge peralta", "jorge alberto peralta",
        "francisco javier", "francisco javier hernandez",
        "hector gonzalez", "hector gonzalez rubio",
        "jesus alfredo", "jesus alfredo ramirez",
        "manuel peralta", "manuel peralta medina",
        "jorge alberto peralta", "jorge peralta",
        "jose roberto", "jose roberto lomeli",
        "jose de jesus", "jose de jesus hernandez",
    }
    
    # Partidos políticos (permitidos)
    PUBLIC_PARTIES: Set[str] = {
        "morena", "pan", "pri", "prd", "mc", "pvem", "pt",
        "coalicion", "fuerza y corazon", "sigamos haciendo historia",
    }
    
    # Patrones regex para PII
    PII_PATTERNS: Dict[PIICategory, re.Pattern] = {
        PIICategory.EMAIL: re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            re.IGNORECASE
        ),
        PIICategory.PHONE: re.compile(
            r'(\+?52[-.]?\s?)?(\(?\d{3}\)?[-.]?\s?\d{3}[-.]?\s?\d{4})',
            re.IGNORECASE
        ),
        PIICategory.CURP: re.compile(
            r'\b[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]{2}\b',
            re.IGNORECASE
        ),
        PIICategory.RFC: re.compile(
            r'\b[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}\b',
            re.IGNORECASE
        ),
        PIICategory.INE_KEY: re.compile(
            r'\b\d{10,18}\b',  # Simplificado, ajustar según formato real INE
        ),
    }
    
    def __init__(self, strict_mode: bool = False):
        """
        Args:
            strict_mode: Si True, bloquea más agresivamente (para producción)
        """
        self.strict_mode = strict_mode
        self.blocked_count = 0
        self.allowed_count = 0
    
    def validate_payload(
        self, 
        payload: str,
        context: str = "general"
    ) -> PIIFilterResult:
        """
        Valida que un payload no contenga PII no autorizado.
        
        Args:
            payload: Texto a validar
            context: Contexto de uso (e.g., "social_media", "survey", "internal")
        
        Returns:
            PIIFilterResult con estado y violaciones detectadas
        """
        violations = []
        
        # 1. Verificar keywords restringidas
        payload_lower = payload.lower()
        for keyword in self.RESTRICTED_KEYWORDS:
            if keyword in payload_lower:
                # Verificar si es falso positivo (e.g., "email" en contexto público)
                if not self._is_false_positive(keyword, payload):
                    violations.append({
                        "type": "keyword",
                        "keyword": keyword,
                        "severity": "high",
                        "context": context,
                    })
        
        # 2. Detectar PII con regex
        for category, pattern in self.PII_PATTERNS.items():
            matches = pattern.findall(payload)
            for match in matches:
                # Verificar si es candidato público (falso positivo)
                if not self._is_public_figure(str(match)):
                    violations.append({
                        "type": "pattern",
                        "category": category.value,
                        "match": str(match)[:20] + "..." if len(str(match)) > 20 else str(match),
                        "severity": "critical",
                    })
        
        is_clean = len(violations) == 0
        
        if is_clean:
            self.allowed_count += 1
        else:
            self.blocked_count += 1
            logger.warning(f"[GATEWAY] Blocked payload in context '{context}': {len(violations)} violations")
        
        return PIIFilterResult(
            is_clean=is_clean,
            violations=violations,
        )
    
    def redact_pii(self, text: str, preserve_candidates: bool = True) -> str:
        """
        Elimina PII de texto, preservando nombres de candidatos públicos.
        
        Args:
            text: Texto original
            preserve_candidates: Si True, no redacta nombres de candidatos
        
        Returns:
            Texto con PII redactado
        """
        result = text
        
        # Redactar emails
        result = self.PII_PATTERNS[PIICategory.EMAIL].sub("[EMAIL_REDACTED]", result)
        
        # Redactar teléfonos
        result = self.PII_PATTERNS[PIICategory.PHONE].sub("[PHONE_REDACTED]", result)
        
        # Redactar CURP (siempre, es muy sensible)
        result = self.PII_PATTERNS[PIICategory.CURP].sub("[CURP_REDACTED]", result)
        
        # Redactar RFC
        result = self.PII_PATTERNS[PIICategory.RFC].sub("[RFC_REDACTED]", result)
        
        # Redactar INE keys
        result = self.PII_PATTERNS[PIICategory.INE_KEY].sub("[INE_KEY_REDACTED]", result)
        
        return result
    
    def _is_false_positive(self, keyword: str, payload: str) -> bool:
        """Verifica si una keyword es falso positivo."""
        # Ejemplo: "email" en "email de contacto del partido" es público
        # Pero "mi email es..." es privado
        
        contextual_phrases = [
            "email del partido", "email publico", "email oficial",
            "contacto publico", "contacto oficial",
        ]
        
        payload_lower = payload.lower()
        for phrase in contextual_phrases:
            if phrase in payload_lower:
                return True
        
        return False
    
    def _is_public_figure(self, text: str) -> bool:
        """Verifica si el texto corresponde a una figura pública conocida."""
        text_lower = text.lower()
        
        # Verificar candidatos
        for candidate in self.PUBLIC_CANDIDATES:
            if candidate in text_lower:
                return True
        
        # Verificar partidos
        for party in self.PUBLIC_PARTIES:
            if party in text_lower:
                return True
        
        return False
    
    def can_federate_to(
        self,
        source_org: str,
        target_org: str,
        data_classification: str = "internal"
    ) -> Tuple[bool, str]:
        """
        Verifica si se puede federar datos entre organizaciones (A2A).
        
        Basado en gateway.py de Antigravity.
        
        Returns:
            (permitted: bool, reason: str)
        """
        # No federar datos clasificados
        if data_classification in ["secret", "confidential", "restricted"]:
            return False, f"Cannot federate {data_classification} data"
        
        # Reglas de federación específicas
        if source_org == "vigil" and target_org == "external":
            # Vigil solo federaría datos públicos/anonymized
            if data_classification != "public":
                return False, "Vigil only federates public/anonymized data externally"
        
        return True, "Federation permitted"
    
    def get_stats(self) -> Dict[str, int]:
        """Retorna estadísticas de filtrado."""
        return {
            "allowed": self.allowed_count,
            "blocked": self.blocked_count,
            "total": self.allowed_count + self.blocked_count,
        }


# Instancia global
default_gateway = SecurityGateway(strict_mode=False)


def validate_payload(payload: str, context: str = "general") -> PIIFilterResult:
    """Función de conveniencia."""
    return default_gateway.validate_payload(payload, context)


def redact_pii(text: str) -> str:
    """Función de conveniencia."""
    return default_gateway.redact_pii(text)
