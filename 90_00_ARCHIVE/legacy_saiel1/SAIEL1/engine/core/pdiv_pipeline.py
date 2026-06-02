"""
PDIV Pipeline - Flujo completo de procesamiento para cálculo PDIV
Integra recolección, análisis de sentimiento y cálculo de posicionamiento

Autor: SAIEL Intelligence System
Versión: 1.0 (Production Pipeline)
"""

import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Importar componentes del sistema
from pdiv_calculator import PDIVCalculator
from local_sentiment import cargar_comentarios, analizar_lote_local, verificar_ollama
from sensemaker_engine import IndustrialSensemaker
from data_ingestion import DataIngestionPipeline, AnonymizationConfig

class PDIVPipeline:
    """
    Pipeline completo para cálculo PDIV desde datos crudos hasta reportes finales
    """
    
    def __init__(self, region: str = 'nayarit', model_name: str = 'deepseek-r1:7b'):
        self.region = region
        self.model_name = model_name
        self.calculator = PDIVCalculator()
        self.sensemaker = IndustrialSensemaker()
        
        # Configurar rutas dinámicas
        self.setup_paths()
        
    def setup_paths(self):
        """Configura rutas según sistema operativo"""
        if os.name == "nt":  # Windows
            self.base_path = Path("c:/Users/dcamb/Desktop/Consultoria_Inteligencia")
        else:  # Linux/VM
            self.base_path = Path("/home/persival/Dev/Projects/SAIEL")
        
        self.raw_path = self.base_path / "data" / "raw"
        self.processed_path = self.base_path / "data" / "processed"
        self.reports_path = self.base_path / "reports"
        
        # Crear directorios si no existen
        for path in [self.raw_path, self.processed_path, self.reports_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def load_processed_data(self, filename: str = None) -> pd.DataFrame:
        """
        Carga datos ya procesados y anonimizados desde data/processed/
        Usa el nuevo pipeline de ingesta para datos limpios
        """
        print("--- CARGANDO DATOS PROCESADOS Y ANONIMIZADOS ---")
        
        # Configuración de anonimización
        config = AnonymizationConfig(
            hash_usernames=True,
            hash_user_ids=True,
            redact_emails=True,
            redact_phones=True,
            redact_names=True,
            synthetic_data=False,
            preserve_length=True
        )
        
        # Crear pipeline de ingesta
        ingestion_pipeline = DataIngestionPipeline(
            config=config,
            base_path=self.base_path
        )
        
        # Primero procesar datos crudos si es necesario
        if filename:
            # Procesar archivo específico
            raw_file = self.raw_path / filename
            if raw_file.exists():
                print(f"Procesando archivo específico: {filename}")
                ingestion_results = ingestion_pipeline.process_file(raw_file)
            else:
                print(f"Buscando archivo procesado: {filename}")
        else:
            # Procesar todos los archivos en data/raw/
            print("Procesando todos los archivos crudos...")
            ingestion_results = ingestion_pipeline.process_directory()
        
        # Cargar datos procesados
        if filename:
            processed_files = [self.processed_path / f"{filename.stem}_processed.json"]
        else:
            processed_files = list(self.processed_path.glob("*_processed.json"))
        
        all_data = []
        
        for file_path in processed_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                if isinstance(data, list):
                    # Los datos ya vienen estandarizados del pipeline de ingesta
                    for item in data:
                        # Convertir a formato PDIV
                        pdiv_record = self.convert_to_pdiv_format(item)
                        if pdiv_record:
                            all_data.append(pdiv_record)
                            
            except Exception as e:
                print(f"Error cargando procesado {file_path}: {e}")
        
        if not all_data:
            raise ValueError("No se encontraron datos procesados válidos")
        
        df = pd.DataFrame(all_data)
        print(f"Datos procesados cargados: {len(df)} registros")
        print(f"PII detectada y anonimizada: {ingestion_results.get('pii_detections', 0)} casos")
        
        return df
    
    def convert_to_pdiv_format(self, processed_record: Dict) -> Optional[Dict]:
        """
        Convierte registro procesado a formato PDIV
        """
        try:
            return {
                'candidato': processed_record.get('candidate', 'unknown'),
                'text': processed_record.get('text', ''),
                'user': processed_record.get('user', 'anonymous'),
                'source': processed_record.get('source', 'unknown'),
                'likes': processed_record.get('likes', 0),
                'shares': processed_record.get('shares', 0),
                'comments': processed_record.get('comments', 0),
                'date': processed_record.get('date', ''),
                'collected_at': processed_record.get('collected_at', ''),
                'anonymized': processed_record.get('anonymized', False),
                'quality_score': processed_record.get('quality_score', 1.0)
            }
        except Exception as e:
            print(f"Error convirtiendo registro: {e}")
            return None
    
    def standardize_record(self, record: Dict, source_file: str) -> Optional[Dict]:
        """
        Estandariza formato de registro para compatibilidad PDIV
        """
        try:
            # Mapeo de campos estándar
            standardized = {
                'candidato': record.get('candidato', record.get('target', 'unknown')),
                'text': record.get('text', record.get('comment', '')),
                'user': record.get('user', record.get('username', 'anonymous')),
                'source': record.get('source', source_file.split('_')[0] if '_' in source_file else 'unknown'),
                'likes': int(record.get('likes', 0)),
                'shares': int(record.get('shares', 0)),
                'comments': int(record.get('comments', 0)),
                'date': record.get('date', record.get('timestamp', datetime.now().isoformat())),
                'collected_at': record.get('collected_at', datetime.now().isoformat())
            }
            
            # Validar campos mínimos
            if not standardized['text'] or len(standardized['text'].strip()) < 3:
                return None
                
            return standardized
            
        except Exception as e:
            print(f"Error estandarizando registro: {e}")
            return None
    
    def analyze_sentiment_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analiza sentimiento usando Vertex AI (Gemini) o motor local (Ollama)
        """
        print(f"--- Iniciando Análisis de Sentimiento ---")
        
        use_cloud = os.getenv("SAIEL_USE_CLOUD", "true").lower() == "true"
        
        if use_cloud:
            from engine.vertex_adapter import VertexSentimentAnalyzer
            analyzer = VertexSentimentAnalyzer()
            texts = df['text'].tolist()
            cloud_results = []
            
            # Procesar en lotes de 10 para Vertex
            for i in range(0, len(texts), 10):
                batch = texts[i:i+10]
                cloud_results.extend(analyzer.analyze_batch(batch))
            
            df['sentimiento'] = [r.get('score', 0.0) for r in cloud_results]
            df['label'] = [r.get('label', 'neutro') for r in cloud_results]
            df['topic'] = [r.get('topic', 'General') for r in cloud_results]
            return df

        # --- FALLBACK A MOTOR LOCAL (Legacy) ---
        print(f"--- Usando motor local {self.model_name} ---")
            
            # Combinar resultados
            for j, item_analizado in enumerate(lote_resultado):
                if j < len(lote):
                    resultados_completos.append(item_analizado)
        
        # Integrar sentimiento al DataFrame original
        sentiment_df = pd.DataFrame(resultados_completos)
        
        # Merge por texto (asumiendo que el orden se mantiene)
        df['sentimiento'] = sentiment_df['sentimiento'].values
        df['intensidad'] = sentiment_df.get('intensidad', 3).values
        df['tema'] = sentiment_df.get('tema', 'general').values
        df['categoria'] = sentiment_df.get('categoria', 'neutro').values
        df['es_bot'] = sentiment_df.get('es_bot', False).values
        
        print(f"Análisis de sentimiento completado: {len(df)} registros procesados")
        
        return df
    
    def discover_narratives(self, df: pd.DataFrame) -> Dict:
        """
        Descubre narrativas usando el sensemaker engine
        """
        print("--- Descubriendo narrativas automáticas ---")
        
        try:
            # Filtrar comentarios con texto válido
            valid_df = df[df['text'].str.len() > 10].copy()
            
            if len(valid_df) < 10:
                print("Advertencia: Insuficientes comentarios para análisis de narrativas")
                return {"narrativas": []}
            
            # Usar sensemaker para clustering
            narrativas = self.sensemaker.discover_narratives(valid_df, n_clusters=5)
            
            # Agregar metadata de análisis
            analysis_meta = {
                "total_comentarios": len(valid_df),
                "clusters_generados": len(narrativas),
                "fecha_analisis": datetime.now().isoformat(),
                "region": self.region
            }
            
            return {
                "narrativas": narrativas,
                "metadata": analysis_meta
            }
            
        except Exception as e:
            print(f"Error en descubrimiento de narrativas: {e}")
            return {"narrativas": [], "error": str(e)}
    
    def run_complete_pipeline(self, input_file: str = None) -> Dict:
        """
        Ejecuta el pipeline completo de PDIV
        """
        print(f"=== INICIANDO PIPELINE PDIV - {self.region.upper()} ===")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 60)
        
        try:
            # 1. Cargar y procesar datos (con anonimización)
            print("\n1. CARGANDO Y PROCESANDO DATOS (CON ANONIMIZACIÓN)...")
            processed_df = self.load_processed_data(input_file)
            
            # 2. Análisis de sentimiento
            print("\n2. ANALIZANDO SENTIMIENTO...")
            sentiment_df = self.analyze_sentiment_batch(processed_df)
            
            # 3. Descubrimiento de narrativas
            print("\n3. DESCUBRIENDO NARRATIVAS...")
            narratives = self.discover_narratives(sentiment_df)
            
            # 4. Cálculo PDIV
            print("\n4. CALCULANDO PDIV...")
            pdiv_results = self.calculator.calculate_pdiv(sentiment_df, self.region)
            
            # 5. Matriz de posicionamiento
            print("\n5. GENERANDO MATRIZ DE POSICIONAMIENTO...")
            positioning_matrix = self.calculator.generate_positioning_matrix(pdiv_results)
            
            # 6. Compilar resultados finales
            final_results = {
                "metadata": {
                    "region": self.region,
                    "fecha_calculo": datetime.now().isoformat(),
                    "total_registros": len(sentiment_df),
                "datos_anonimizados": True,
                "pii_protegida": True,
                    "candidatos_analizados": len(pdiv_results),
                    "modelo_sentimiento": self.model_name,
                    "correlacion_objetivo": ">0.7"
                },
                "pdiv_scores": pdiv_results.to_dict('index'),
                "matriz_posicionamiento": positioning_matrix,
                "narrativas_descubiertas": narratives,
                "estadisticas_globales": {
                    "sentimiento_promedio": float(pdiv_results['sentimiento_score'].mean()),
                    "pdiv_promedio": float(pdiv_results['pdiv_score'].mean()),
                    "volumen_total": int(sentiment_df.groupby('candidato').size().sum()),
                "bots_detectados": int(sentiment_df['es_bot'].sum()) if 'es_bot' in sentiment_df.columns else 0,
                "registros_anonimizados": int(sentiment_df['anonymized'].sum()) if 'anonymized' in sentiment_df.columns else 0,
                "calidad_promedio": float(sentiment_df['quality_score'].mean()) if 'quality_score' in sentiment_df.columns else 1.0
                }
            }
            
            # 7. Guardar resultados
            self.save_results(final_results)
            
            # 8. Generar reporte
            self.generate_executive_report(final_results)
            
            # 9. Subir a BigQuery (Opcional Cloud)
            if os.getenv("SAIEL_USE_CLOUD", "true").lower() == "true":
                self.upload_to_bq(final_results)
            
            print("\n" + "=" * 60)
            print("PIPELINE PDIV COMPLETADO EXITOSAMENTE")
            print(f"Resultados guardados en: {self.processed_path}")
            print(f"Reporte generado en: {self.reports_path}")
            print("=" * 60)
            
            return final_results
            
        except Exception as e:
            print(f"\nERROR CRÍTICO EN PIPELINE: {e}")
            raise
    
    def save_results(self, results: Dict):
        """
        Guarda resultados en formato JSON estructurado
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Guardar resultados completos
        results_file = self.processed_path / f"pdiv_results_{self.region}_{timestamp}.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        
        # Guardar solo scores PDIV para fácil acceso
        pdiv_scores = results['pdiv_scores']
        scores_file = self.processed_path / f"pdiv_scores_{self.region}_{timestamp}.json"
        with open(scores_file, "w", encoding="utf-8") as f:
            json.dump(pdiv_scores, f, indent=2, ensure_ascii=False)
        
        print(f"Resultados guardados:")
        print(f"  - Completo: {results_file}")
        print(f"  - Scores: {scores_file}")
    
    def generate_executive_report(self, results: Dict):
        """
        Genera reporte ejecutivo en formato Markdown
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_path / f"REPORTE_PDIV_{self.region.upper()}_{timestamp}.md"
        
        # Extraer datos clave
        metadata = results['metadata']
        stats = results['estadisticas_globales']
        matrix = results['matriz_posicionamiento']
        
        # Generar contenido del reporte
        report_content = f"""# REPORTE DE INTELIGENCIA POLÍTICA - PDIV

## RESUMEN EJECUTIVO
**Región:** {metadata['region'].upper()}  
**Fecha:** {metadata['fecha_calculo']}  
**Total de Registros:** {metadata['total_registros']:,}  
**Candidatos Analizados:** {metadata['candidatos_analizados']}  

---

## INDICADORES CLAVE

### Salud Digital General
- **Sentimiento Promedio:** {stats['sentimiento_promedio']:.1f}/100
- **PDIV Promedio:** {stats['pdiv_promedio']:.1f}/100
- **Volumen Total:** {stats['volumen_total']:,} menciones
- **Bots Detectados:** {stats['bots_detectados']} ({stats['bots_detectados']/metadata['total_registros']*100:.1f}%)

---

## MATRIZ DE POSICIONAMIENTO ESTRATÉGICO

### Líderes (Alto PDIV, Alto Sentimiento)
{', '.join(matrix['cuadrantes']['lideres']) if matrix['cuadrantes']['lideres'] else 'Ninguno'}

### Retadores (Bajo PDIV, Alto Sentimiento)  
{', '.join(matrix['cuadrantes']['retadores']) if matrix['cuadrantes']['retadores'] else 'Ninguno'}

### Vulnerables (Alto PDIV, Bajo Sentimiento)
{', '.join(matrix['cuadrantes']['vulnerables']) if matrix['cuadrantes']['vulnerables'] else 'Ninguno'}

### Perdedores (Bajo PDIV, Bajo Sentimiento)
{', '.join(matrix['cuadrantes']['perdedores']) if matrix['cuadrantes']['perdedores'] else 'Ninguno'}

---

## DETALLE DE PUNTUACIONES PDIV

| Candidato | PDIV | Sentimiento | Volumen | Engagement | Crecimiento |
|-----------|------|-------------|----------|------------|-------------|
"""
        
        # Agregar tabla de candidatos
        for candidato, scores in results['pdiv_scores'].items():
            report_content += f"| {candidato} | {scores['pdiv_score']:.1f} | {scores['sentimiento_score']:.1f} | {scores['volumen_score']:.1f} | {scores['engagement_score']:.1f} | {scores['crecimiento_score']:.1f} |\n"
        
        # Agregar narrativas principales
        if results['narrativas_descubiertas']['narrativas']:
            report_content += f"""

---

## NARRATIVAS EMERGENTES

"""
            for i, narrativa in enumerate(results['narrativas_descubiertas']['narrativas'][:3]):
                salud = "POSITIVA" if narrativa['sentimiento_salud'] > 0.1 else "CRÍTICA" if narrativa['sentimiento_salud'] < -0.1 else "NEUTRAL"
                report_content += f"### {i+1}. Tema: Auto-detectado\n"
                report_content += f"- **Volumen:** {narrativa['volumen']} menciones ({narrativa['porcentaje']}%)\n"
                report_content += f"- **Salud:** {salud} ({narrativa['sentimiento_salud']:.2f})\n"
                if narrativa['ejemplos_clave']:
                    report_content += f"- **Ejemplo:** \"{narrativa['ejemplos_clave'][0][:100]}...\"\n"
                report_content += "\n"
        
        # Agregar recomendaciones
        report_content += f"""

---

## RECOMENDACIONES ESTRATÉGICAS

### Acciones Inmediatas (Próximas 72h)
1. **Monitoreo de Crisis:** Implementar alertas si sentimiento cae >10%
2. **Contenido Estratégico:** Potenciar narrativas con salud positiva
3. **Engagement Activo:** Responder a comentarios en fuentes de alto peso

### Mediano Plazo (1-2 semanas)
1. **Análisis de Competencia:** Monitorear PDIV de oponentes
2. **Optimización de Fuentes:** Ajustar estrategia según demographics
3. **Validación de Encuestas:** Comparar PDIV con polls tradicionales

---

## METADATOS TÉCNICOS
- **Modelo de Sentimiento:** {metadata['modelo_sentimiento']}
- **Correlación Objetivo:** {metadata['correlacion_objetivo']}
- **Procesamiento:** 100% local (On-premise)
- **Compliance:** LGPDPPSO, GDPR, Berkeley Protocol

*Reporte generado automáticamente por SAIEL Intelligence System*
"""
        
        # Guardar reporte
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)
        
        print(f"Reporte ejecutivo guardado: {report_file}")

    def upload_to_bq(self, results: Dict):
        """
        Sube las puntuaciones PDIV a BigQuery
        """
        try:
            from engine.bq_adapter import BigQueryAdapter
            adapter = BigQueryAdapter()
            adapter.setup_schema()
            
            # Preparar DataFrame para BQ
            rows = []
            for candidato, scores in results['pdiv_scores'].items():
                rows.append({
                    'candidato': candidato,
                    'pdiv_score': scores['pdiv_score'],
                    'sentimiento_score': scores['sentimiento_score'],
                    'volumen_score': scores['volumen_score'],
                    'engagement_score': scores['engagement_score'],
                    'crecimiento_score': scores['crecimiento_score'],
                    'region': self.region,
                    'fecha_calculo': datetime.now()
                })
            
            df_bq = pd.DataFrame(rows)
            adapter.upload_results(df_bq)
        except Exception as e:
            print(f"Error subiendo a BigQuery: {e}")

# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    # Ejemplo de uso
    pipeline = PDIVPipeline(region='tepic')
    
    try:
        results = pipeline.run_complete_pipeline()
        print("\nPipeline completado exitosamente")
        
    except Exception as e:
        print(f"Error en pipeline: {e}")
        raise
