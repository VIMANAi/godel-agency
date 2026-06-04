"""
Data Ingestion Pipeline - Módulo independiente de ingesta y procesamiento
Separado completamente del scraping layer con anonimización robusta

Autor: SAIEL Intelligence System
Versión: 2.0 (Privacy-First)
"""

import pandas as pd
import json
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import logging
from pydantic import BaseModel, ValidationError, Field
import structlog
from faker import Faker

# Configuración de logging estructurado
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Inicializar Faker para datos sintéticos
fake = Faker('es_MX')

@dataclass
class AnonymizationConfig:
    """Configuración de anonimización"""
    hash_usernames: bool = True
    hash_user_ids: bool = True
    redact_emails: bool = True
    redact_phones: bool = True
    redact_addresses: bool = True
    redact_names: bool = True
    synthetic_data: bool = False
    allow_synthetic_input: bool = False
    preserve_length: bool = True

class SocialMediaRecord(BaseModel):
    """Schema Pydantic para validación de datos"""
    
    # Campos obligatorios
    id: str = Field(..., description="ID único del registro")
    source: str = Field(..., description="Fuente de datos (instagram, facebook, etc.)")
    text: str = Field(..., min_length=3, max_length=5000, description="Texto del comentario/post")
    date: str = Field(..., description="Fecha de publicación (ISO 8601)")
    
    # Campos opcionales con defaults
    user: Optional[str] = Field(None, description="Nombre de usuario (será anonimizado)")
    user_id: Optional[str] = Field(None, description="ID de usuario (será anonimizado)")
    likes: int = Field(0, ge=0, description="Número de likes")
    shares: int = Field(0, ge=0, description="Número de shares")
    comments: int = Field(0, ge=0, description="Número de comentarios")
    candidate: Optional[str] = Field(None, description="Candidato asociado")
    collected_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    # Metadata del procesamiento
    processed_version: str = Field(default="2.0")
    anonymized: bool = Field(default=False)
    quality_score: float = Field(default=1.0, ge=0.0, le=1.0)

class DataIngestionPipeline:
    """
    Pipeline de ingesta de datos con anonimización y validación robusta
    """
    
    def __init__(self, 
                 config: AnonymizationConfig = None,
                 base_path: Path = None):
        self.config = config or AnonymizationConfig()
        if base_path:
            self.base_path = Path(base_path)
        else:
            from dotenv import load_dotenv
            import os
            load_dotenv()
            env_base_path = os.getenv("SAIEL_BASE_PATH")
            if env_base_path:
                self.base_path = Path(env_base_path)
            else:
                self.base_path = Path(__file__).resolve().parents[2]
        self.setup_paths()
        self.setup_anonymization()
        
        # Contadores para métricas
        self.stats = {
            'total_records': 0,
            'valid_records': 0,
            'invalid_records': 0,
            'anonymized_fields': 0,
            'pii_detected': 0
        }
    
    def setup_paths(self):
        """Configura rutas del pipeline"""
        self.raw_path = self.base_path / "data" / "raw"
        self.staging_path = self.base_path / "data" / "staging"
        self.processed_path = self.base_path / "data" / "processed"
        self.rejected_path = self.base_path / "data" / "rejected"
        
        for path in [self.raw_path, self.staging_path, self.processed_path, self.rejected_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def setup_anonymization(self):
        """Configura motores de anonimización"""
        # Patrones regex para PII
        self.pii_patterns = {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone': re.compile(r'(\+\d{1,3}[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}'),
            'cpf': re.compile(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b'),  # Brasil (por si acaso)
            'curp': re.compile(r'\b[A-Z]{4}\d{6}[HM][A-Z]{5}\d{2}\b'),  # México
            'ine': re.compile(r'\b[A-Z]{6}\d{8}\b'),  # Credencial México
            'ip_address': re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
            'url': re.compile(r'https?://[^\s<>"{}|\\^`[\]]+'),
            'hashtag': re.compile(r'#\w+'),
            'mention': re.compile(r'@\w+'),
        }
        
        # Patrones para nombres comunes en español
        self.name_patterns = [
            re.compile(r'\b(?:Juan|María|José|Luis|Ana|Carmen|Francisco|María|Laura|Sofía)\s+[A-Z][a-z]+\b'),
            re.compile(r'\b(?:Dr|Lic|Ing|Mtro|Sr|Sra|Don|Doña)\s+[A-Z][a-z]+\b'),
        ]
        
        # Cache de hashes para consistencia
        self.hash_cache = {}
    
    def hash_field(self, value: str, field_type: str = "default") -> str:
        """
        Genera hash consistente para campos sensibles
        """
        if not value or value in self.hash_cache:
            return self.hash_cache.get(value, value)
        
        # Usar salt diferente por tipo de campo
        salt = f"saiel_{field_type}_2026"
        hash_input = f"{value}{salt}".encode('utf-8')
        
        # SHA-256 para irreversibilidad
        hashed = hashlib.sha256(hash_input).hexdigest()[:16]
        
        # Preservar longitud si se configura
        if self.config.preserve_length:
            hashed = hashed[:len(value)] if len(value) > 16 else hashed
        
        self.hash_cache[value] = hashed
        return hashed
    
    def detect_pii(self, text: str) -> Dict[str, List[str]]:
        """
        Detecta información personal identificable (PII)
        """
        pii_found = {}
        
        # Detectar patrones conocidos
        for pii_type, pattern in self.pii_patterns.items():
            matches = pattern.findall(text)
            if matches:
                pii_found[pii_type] = matches
        
        # Detectar nombres
        for pattern in self.name_patterns:
            matches = pattern.findall(text)
            if matches and 'names' not in pii_found:
                pii_found['names'] = []
            if matches:
                pii_found['names'].extend(matches)
        
        return pii_found
    
    def anonymize_text(self, text: str) -> Tuple[str, Dict[str, int]]:
        """
        Anonimiza texto detectando y reemplazando PII
        """
        if not text:
            return text, {}
        
        anonymized = text
        anonymization_stats = {}
        
        # Anonimizar emails
        if self.config.redact_emails:
            emails = self.pii_patterns['email'].findall(anonymized)
            if emails:
                anonymized = self.pii_patterns['email'].sub('[EMAIL_REDACTED]', anonymized)
                anonymization_stats['emails'] = len(emails)
        
        # Anonimizar teléfonos
        if self.config.redact_phones:
            phones = self.pii_patterns['phone'].findall(anonymized)
            if phones:
                anonymized = self.pii_patterns['phone'].sub('[PHONE_REDACTED]', anonymized)
                anonymization_stats['phones'] = len(phones)
        
        # Anonimizar IDs gubernamentales
        for id_type in ['cpf', 'curp', 'ine']:
            if hasattr(self.pii_patterns, id_type):
                ids = self.pii_patterns[id_type].findall(anonymized)
                if ids:
                    anonymized = self.pii_patterns[id_type].sub(f'[{id_type.upper()}_REDACTED]', anonymized)
                    anonymization_stats[id_type] = len(ids)
        
        # Anonimizar IPs
        if self.pii_patterns['ip_address'].findall(anonymized):
            anonymized = self.pii_patterns['ip_address'].sub('[IP_REDACTED]', anonymized)
            anonymization_stats['ip_addresses'] = len(self.pii_patterns['ip_address'].findall(text))
        
        # Anonimizar URLs (mantener dominio)
        if self.pii_patterns['url'].findall(anonymized):
            urls = self.pii_patterns['url'].findall(anonymized)
            for url in urls:
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(url)
                    domain = parsed.netloc
                    anonymized = anonymized.replace(url, f'[URL: {domain}]')
                except:
                    anonymized = anonymized.replace(url, '[URL_REDACTED]')
            anonymization_stats['urls'] = len(urls)
        
        # Anonimizar nombres si se configura
        if self.config.redact_names:
            for pattern in self.name_patterns:
                names = pattern.findall(anonymized)
                if names:
                    for name in names:
                        anonymized = anonymized.replace(name, '[NAME_REDACTED]')
                    anonymization_stats['names'] = len(names)
        
        return anonymized, anonymization_stats
    
    def anonymize_record(self, record: Dict) -> Dict:
        """
        Anonimiza un registro completo
        """
        anonymized = record.copy()
        anonymization_log = {}
        
        # Anonimizar campos específicos
        if self.config.hash_usernames and anonymized.get('user'):
            original_user = anonymized['user']
            anonymized['user'] = self.hash_field(original_user, 'username')
            anonymization_log['user_hashed'] = True
        
        if self.config.hash_user_ids and anonymized.get('user_id'):
            original_id = anonymized['user_id']
            anonymized['user_id'] = self.hash_field(original_id, 'user_id')
            anonymization_log['user_id_hashed'] = True
        
        # Anonimizar texto
        if anonymized.get('text'):
            original_text = anonymized['text']
            anonymized_text, text_stats = self.anonymize_text(original_text)
            anonymized['text'] = anonymized_text
            anonymized['original_text_length'] = len(original_text)
            anonymized['anonymized_text_length'] = len(anonymized_text)
            anonymization_log.update(text_stats)
        
        # Generar datos sintéticos si se configura
        if self.config.synthetic_data:
            if anonymized.get('user'):
                anonymized['synthetic_user'] = fake.user_name()
            if anonymized.get('location'):
                anonymized['synthetic_location'] = fake.city()
        
        # Marcar como anonimizado
        anonymized['anonymized'] = True
        anonymized['anonymization_timestamp'] = datetime.now().isoformat()
        anonymized['anonymization_log'] = anonymization_log
        
        return anonymized
    
    def validate_and_parse_record(self, raw_record: Dict) -> Tuple[Optional[SocialMediaRecord], Dict]:
        """
        Valida y parsea un registro usando Pydantic
        """
        validation_log = {
            'validation_errors': [],
            'warnings': [],
            'quality_score': 1.0
        }
        
        try:
            # Estandarizar campos
            standardized = self.standardize_record(raw_record, validation_log)
            
            # Validar con Pydantic
            record = SocialMediaRecord(**standardized)
            
            # Calcular quality score
            quality_issues = len(validation_log['validation_errors'])
            validation_log['quality_score'] = max(0.0, 1.0 - (quality_issues * 0.1))
            
            return record, validation_log
            
        except ValidationError as e:
            validation_log['validation_errors'].extend([str(error) for error in e.errors()])
            return None, validation_log
        except Exception as e:
            validation_log['validation_errors'].append(f"Error inesperado: {str(e)}")
            return None, validation_log
    
    def standardize_record(self, raw_record: Dict, log: Dict) -> Dict:
        """
        Estandariza formato de registro
        """
        standardized = {}
        
        # Mapeo de campos estándar
        field_mapping = {
            'id': ['id', '_id', 'record_id', 'uuid'],
            'source': ['source', 'platform', 'red'],
            'text': ['text', 'comment', 'contenido', 'mensaje', 'caption'],
            'user': ['user', 'username', 'autor', 'ownerUsername'],
            'user_id': ['user_id', 'userId', 'id_usuario'],
            'date': ['date', 'timestamp', 'fecha', 'created_at'],
            'likes': ['likes', 'likesCount', 'me_gusta'],
            'shares': ['shares', 'sharesCount', 'compartidos'],
            'comments': ['comments', 'commentsCount', 'respuestas'],
            'candidate': ['candidate', 'candidato', 'target']
        }
        
        # Mapear campos
        for standard_field, possible_fields in field_mapping.items():
            for field in possible_fields:
                if field in raw_record and raw_record[field] is not None:
                    standardized[standard_field] = raw_record[field]
                    break
        
        # Generar ID si no existe
        if 'id' not in standardized:
            standardized['id'] = hashlib.md5(
                f"{raw_record.get('text', '')}{raw_record.get('date', '')}".encode()
            ).hexdigest()[:16]
        
        # Validaciones específicas
        if 'text' in standardized:
            text = standardized['text']
            if len(text.strip()) < 3:
                log['validation_errors'].append("Texto demasiado corto (<3 caracteres)")
            elif len(text) > 5000:
                log['warnings'].append("Texto muy largo (>5000 caracteres), será truncado")
                standardized['text'] = text[:5000]
        
        # Estandarizar fechas
        if 'date' in standardized:
            try:
                # Intentar parsear diferentes formatos
                date_str = standardized['date']
                if isinstance(date_str, (int, float)):
                    # Timestamp Unix
                    standardized['date'] = datetime.fromtimestamp(date_str).isoformat()
                else:
                    # Intentar parseo ISO
                    from dateutil import parser
                    parsed_date = parser.parse(date_str)
                    standardized['date'] = parsed_date.isoformat()
            except:
                log['warnings'].append("Fecha no reconocida, usando fecha actual")
                standardized['date'] = datetime.now().isoformat()
        
        # Validar campos numéricos
        for field in ['likes', 'shares', 'comments']:
            if field in standardized:
                try:
                    standardized[field] = int(standardized[field])
                    if standardized[field] < 0:
                        standardized[field] = 0
                        log['warnings'].append(f"{field} negativo, convertido a 0")
                except:
                    standardized[field] = 0
                    log['warnings'].append(f"{field} inválido, convertido a 0")
        
        return standardized
    
    def process_file(self, input_file: Path) -> Dict:
        """
        Procesa un archivo completo de datos crudos
        """
        logger.info("Iniciando procesamiento de archivo", 
                   file=str(input_file), 
                   pipeline="data_ingestion")
        
        results = {
            'input_file': str(input_file),
            'total_records': 0,
            'valid_records': 0,
            'invalid_records': 0,
            'anonymized_records': 0,
            'pii_detections': 0,
            'processing_time': None,
            'output_files': []
        }
        
        start_time = datetime.now()
        
        try:
            # Cargar datos (JSON y JSONL)
            raw_data = self.load_raw_data(input_file)
            
            results['total_records'] = len(raw_data)
            self.stats['total_records'] += len(raw_data)
            
            # Procesar cada registro
            valid_records = []
            invalid_records = []
            
            for i, raw_record in enumerate(raw_data):
                self.stats['total_records'] += 1
                is_synthetic = bool(raw_record.get("is_synthetic", False)) or "synthetic" in input_file.as_posix().lower()
                if is_synthetic and not self.config.allow_synthetic_input:
                    invalid_records.append({
                        'raw_record': raw_record,
                        'validation_errors': ["Registro sintético rechazado por configuración"],
                        'record_index': i
                    })
                    results['invalid_records'] += 1
                    self.stats['invalid_records'] += 1
                    continue
                
                # Validar y parsear
                record, validation_log = self.validate_and_parse_record(raw_record)
                
                if record:
                    # Anonimizar
                    anonymized = self.anonymize_record(record.dict())
                    
                    # Detectar PII
                    pii_detected = self.detect_pii(record.text)
                    if pii_detected:
                        results['pii_detections'] += 1
                        self.stats['pii_detected'] += 1
                        anonymized['pii_detected'] = pii_detected
                    
                    valid_records.append(anonymized)
                    results['valid_records'] += 1
                    self.stats['valid_records'] += 1
                    results['anonymized_records'] += 1
                    
                else:
                    invalid_records.append({
                        'raw_record': raw_record,
                        'validation_errors': validation_log['validation_errors'],
                        'record_index': i
                    })
                    results['invalid_records'] += 1
                    self.stats['invalid_records'] += 1
            
            # Guardar resultados
            if valid_records:
                output_file = self.processed_path / f"{input_file.stem}_processed.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(valid_records, f, indent=2, ensure_ascii=False)
                results['output_files'].append(str(output_file))
            
            if invalid_records:
                rejected_file = self.rejected_path / f"{input_file.stem}_rejected.json"
                with open(rejected_file, 'w', encoding='utf-8') as f:
                    json.dump(invalid_records, f, indent=2, ensure_ascii=False)
                results['output_files'].append(str(rejected_file))
            
            results['processing_time'] = (datetime.now() - start_time).total_seconds()
            
            logger.info("Procesamiento completado", 
                       file=str(input_file),
                       valid_records=results['valid_records'],
                       invalid_records=results['invalid_records'],
                       processing_time=results['processing_time'])
            
            return results
            
        except Exception as e:
            logger.error("Error procesando archivo", 
                        file=str(input_file), 
                        error=str(e),
                        pipeline="data_ingestion")
            raise
    
    def process_directory(self, directory: Path = None) -> Dict:
        """
        Procesa todos los archivos en un directorio
        """
        if directory is None:
            directory = self.raw_path
        
        logger.info("Iniciando procesamiento de directorio", 
                   directory=str(directory),
                   pipeline="data_ingestion")
        
        results = {
            'directory': str(directory),
            'files_processed': 0,
            'total_records': 0,
            'valid_records': 0,
            'invalid_records': 0,
            'processing_time': None,
            'file_results': []
        }
        
        start_time = datetime.now()
        
        # Procesar todos los JSON/JSONL files de forma recursiva
        for file_path in directory.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.suffix.lower() not in {".json", ".jsonl"}:
                continue
            if file_path.name.endswith(('_processed.json', '_rejected.json')):
                continue  # Skip already processed files
            
            try:
                file_result = self.process_file(file_path)
                results['file_results'].append(file_result)
                results['files_processed'] += 1
                
                # Acumular estadísticas
                results['total_records'] += file_result['total_records']
                results['valid_records'] += file_result['valid_records']
                results['invalid_records'] += file_result['invalid_records']
                
            except Exception as e:
                logger.error("Error procesando archivo", 
                           file=str(file_path), 
                           error=str(e))
        
        results['processing_time'] = (datetime.now() - start_time).total_seconds()
        
        logger.info("Procesamiento de directorio completado",
                   directory=str(directory),
                   files_processed=results['files_processed'],
                   total_records=results['total_records'],
                   valid_records=results['valid_records'])
        
        return results

    def load_raw_data(self, input_file: Path) -> List[Dict[str, Any]]:
        """
        Carga archivos JSON o JSONL de manera robusta.
        """
        if input_file.suffix.lower() == ".jsonl":
            records: List[Dict[str, Any]] = []
            with open(input_file, 'r', encoding='utf-8') as f:
                for line_number, line in enumerate(f, start=1):
                    stripped = line.strip()
                    if not stripped:
                        continue
                    try:
                        parsed = json.loads(stripped)
                    except json.JSONDecodeError as exc:
                        logger.warning(
                            "Línea JSONL inválida",
                            file=str(input_file),
                            line_number=line_number,
                            error=str(exc)
                        )
                        continue
                    if isinstance(parsed, list):
                        records.extend([item for item in parsed if isinstance(item, dict)])
                    elif isinstance(parsed, dict):
                        records.append(parsed)
            return records

        with open(input_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        if isinstance(raw_data, list):
            return [item for item in raw_data if isinstance(item, dict)]
        if isinstance(raw_data, dict):
            return [raw_data]
        return []
    
    def get_processing_stats(self) -> Dict:
        """
        Retorna estadísticas de procesamiento
        """
        return {
            'pipeline_stats': self.stats.copy(),
            'config': asdict(self.config),
            'cache_size': len(self.hash_cache),
            'processing_version': '2.0'
        }

# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    # Configuración de ejemplo
    config = AnonymizationConfig(
        hash_usernames=True,
        hash_user_ids=True,
        redact_emails=True,
        redact_phones=True,
        redact_names=True,
        synthetic_data=False,
        preserve_length=True
    )
    
    # Crear pipeline
    pipeline = DataIngestionPipeline(config=config)
    
    # Procesar directorio de datos crudos
    try:
        results = pipeline.process_directory()
        print("\n=== RESULTADOS DEL PIPELINE DE INGESTA ===")
        print(f"Archivos procesados: {results['files_processed']}")
        print(f"Registros totales: {results['total_records']}")
        print(f"Registros válidos: {results['valid_records']}")
        print(f"Registros inválidos: {results['invalid_records']}")
        print(f"Tiempo procesamiento: {results['processing_time']:.2f} segundos")
        
        # Estadísticas detalladas
        stats = pipeline.get_processing_stats()
        print(f"\n=== ESTADÍSTICAS DE ANONIMIZACIÓN ===")
        print(f"PII detectada: {stats['pipeline_stats']['pii_detected']}")
        print(f"Cache de hashes: {stats['cache_size']} entradas")
        
    except Exception as e:
        logger.error("Error en ejecución principal", error=str(e))
        print(f"Error: {e}")
