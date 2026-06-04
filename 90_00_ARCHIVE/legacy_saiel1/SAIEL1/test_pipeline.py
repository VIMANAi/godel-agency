"""
Test Suite - Validación completa del Pipeline PDIV v2.0
Testing de anonimización, parseo, normalización y correlación

Autor: SAIEL Intelligence System
Versión: 1.0 (Test Suite)
"""

import json
import re
import shutil
import tempfile
from pathlib import Path

import pandas as pd

# Importar componentes del sistema
from engine.data_ingestion import AnonymizationConfig, DataIngestionPipeline
from engine.pdiv_calculator import PDIVCalculator
from engine.pdiv_pipeline import PDIVPipeline


class PipelineTester:
    """
    Suite de testing completo para el pipeline PDIV
    """

    def __init__(self):
        self.setup_test_environment()
        self.test_results = {"tests_passed": 0, "tests_failed": 0, "test_details": []}

    def setup_test_environment(self):
        """Configura ambiente de testing temporal"""
        self.test_dir = Path(tempfile.mkdtemp(prefix="saiel_test_"))
        self.raw_dir = self.test_dir / "data" / "raw"
        self.processed_dir = self.test_dir / "data" / "processed"
        self.rejected_dir = self.test_dir / "data" / "rejected"

        for path in [self.raw_dir, self.processed_dir, self.rejected_dir]:
            path.mkdir(parents=True, exist_ok=True)

        print(f"Test environment created at: {self.test_dir}")

    def create_test_data(self) -> Path:
        """Crea datos de prueba con PII conocido"""
        test_data = [
            {
                "id": "test_1",
                "source": "instagram",
                "text": "Juan Pérez está muy contento con el trabajo de Andrea Navarro en Tepic. Su email es juan.perez@email.com y teléfono 311-123-4567",
                "user": "juan_perez_123",
                "user_id": "user_12345",
                "date": "2026-04-24T10:00:00Z",
                "likes": 45,
                "shares": 12,
                "comments": 8,
                "candidate": "Andrea Navarro",
            },
            {
                "id": "test_2",
                "source": "facebook",
                "text": "María García critica la gestión pero reconoce mejoras. Contactar en maria.garcia@gmail.com o llamar al 311-987-6543. Mi CURP es GARM800101HDFXXX01",
                "user": "maria_garcia_456",
                "user_id": "user_67890",
                "date": "2026-04-24T11:00:00Z",
                "likes": 23,
                "shares": 5,
                "comments": 15,
                "candidate": "Geraldine Ponce",
            },
            {
                "id": "test_3",
                "source": "tiktok",
                "text": "Bot de prueba generando spam masivo con links https://spam-site.com/buy-votes",
                "user": "bot_spam_789",
                "user_id": "bot_789",
                "date": "2026-04-24T12:00:00Z",
                "likes": 1000,  # Valor anómalo
                "shares": 500,
                "comments": 200,
                "candidate": "Candidato X",
            },
            {
                "id": "test_4",
                "source": "twitter",
                "text": "Dr. Luis Hernández analiza las propuestas electorales con base en datos. IP: 192.168.1.1 para análisis técnico",
                "user": "dr_luis_hernandez",
                "user_id": "user_11111",
                "date": "2026-04-24T13:00:00Z",
                "likes": 67,
                "shares": 23,
                "comments": 9,
                "candidate": "Andrea Navarro",
            },
            {
                "id": "test_5",
                "source": "instagram",
                "text": "Texto muy corto",  # Debe ser rechazado
                "user": "user_short",
                "user_id": "user_short_1",
                "date": "2026-04-24T14:00:00Z",
                "likes": 1,
                "shares": 0,
                "comments": 0,
                "candidate": "Candidato Y",
            },
        ]

        test_file = self.raw_dir / "test_data.json"
        with open(test_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f, indent=2, ensure_ascii=False)

        return test_file

    def run_test(self, test_name: str, test_func):
        """Ejecuta un test individual y registra resultados"""
        print(f"\n--- RUNNING TEST: {test_name} ---")
        try:
            result = test_func()
            if result:
                print(f"✅ PASSED: {test_name}")
                self.test_results["tests_passed"] += 1
                self.test_results["test_details"].append({"test": test_name, "status": "PASSED", "details": result})
            else:
                print(f"❌ FAILED: {test_name}")
                self.test_results["tests_failed"] += 1
                self.test_results["test_details"].append(
                    {"test": test_name, "status": "FAILED", "details": "Test returned False"}
                )
        except Exception as e:
            print(f"❌ ERROR: {test_name} - {str(e)}")
            self.test_results["tests_failed"] += 1
            self.test_results["test_details"].append({"test": test_name, "status": "ERROR", "details": str(e)})

    def test_anonymization(self):
        """Test 1: Verificar anonimización de PII"""
        config = AnonymizationConfig(
            hash_usernames=True, hash_user_ids=True, redact_emails=True, redact_phones=True, redact_names=True
        )

        pipeline = DataIngestionPipeline(config=config, base_path=self.test_dir)
        test_file = self.create_test_data()

        # Procesar archivo
        results = pipeline.process_file(test_file)

        # Cargar resultados procesados
        processed_file = self.processed_dir / "test_data_processed.json"
        with open(processed_file, "r", encoding="utf-8") as f:
            processed_data = json.load(f)

        # Verificaciones
        checks = []

        # 1. Emails anonimizados
        for record in processed_data:
            if "email.com" in record["text"] or "gmail.com" in record["text"]:
                checks.append(False)
            else:
                checks.append(True)

        # 2. Teléfonos anonimizados
        phone_pattern = re.compile(r"\d{3}[-.]?\d{3}[-.]?\d{4}")
        for record in processed_data:
            if phone_pattern.search(record["text"]):
                checks.append(False)
            else:
                checks.append(True)

        # 3. Usuarios hasheados
        for record in processed_data:
            if record["user"] in ["juan_perez_123", "maria_garcia_456"]:
                checks.append(False)
            else:
                checks.append(True)

        # 4. CURP anonimizado
        for record in processed_data:
            if "GARM800101HDFXXX01" in record["text"]:
                checks.append(False)
            else:
                checks.append(True)

        # 5. IPs anonimizadas
        for record in processed_data:
            if "192.168.1.1" in record["text"]:
                checks.append(False)
            else:
                checks.append(True)

        return all(checks), {
            "emails_anonymized": all(checks[:4]),
            "phones_anonymized": all(checks[4:8]),
            "users_hashed": all(checks[8:12]),
            "curp_anonymized": all(checks[12:16]),
            "ips_anonymized": all(checks[16:20]),
        }

    def test_schema_validation(self):
        """Test 2: Verificar validación de schema"""
        config = AnonymizationConfig()
        pipeline = DataIngestionPipeline(config=config, base_path=self.test_dir)
        test_file = self.create_test_data()

        results = pipeline.process_file(test_file)

        # Verificar que se procesaron los registros válidos
        expected_valid = 4  # 5 totales - 1 muy corto
        expected_invalid = 1  # El texto muy corto

        success = results["valid_records"] == expected_valid and results["invalid_records"] == expected_invalid

        return success, {
            "valid_records": results["valid_records"],
            "invalid_records": results["invalid_records"],
            "expected_valid": expected_valid,
            "expected_invalid": expected_invalid,
        }

    def test_pdiv_calculation(self):
        """Test 3: Verificar cálculo PDIV"""
        # Crear datos procesados manualmente
        processed_data = [
            {
                "candidato": "Andrea Navarro",
                "text": "Buen trabajo del candidato",
                "sentimiento": "positivo",
                "source": "instagram",
                "likes": 100,
                "shares": 20,
                "comments": 10,
                "date": "2026-04-24T10:00:00Z",
            },
            {
                "candidato": "Geraldine Ponce",
                "text": "Crítica a la gestión",
                "sentimiento": "negativo",
                "source": "facebook",
                "likes": 50,
                "shares": 10,
                "comments": 5,
                "date": "2026-04-24T11:00:00Z",
            },
        ]

        df = pd.DataFrame(processed_data)
        calculator = PDIVCalculator()

        # Mock de sentimiento numérico
        df["sentimiento_num"] = [1, -1]  # positivo, negativo

        try:
            results = calculator.calculate_pdiv(df, region="tepic")

            # Verificaciones básicas
            checks = [
                len(results) == 2,  # Dos candidatos
                all(0 <= score <= 100 for score in results["pdiv_score"]),  # Scores en rango
                results.loc["Andrea Navarro", "pdiv_score"]
                > results.loc["Geraldine Ponce", "pdiv_score"],  # Andrea > Geraldine
            ]

            return all(checks), {
                "candidates_count": len(results),
                "scores_in_range": all(0 <= score <= 100 for score in results["pdiv_score"]),
                "andrea_score": results.loc["Andrea Navarro", "pdiv_score"],
                "geraldine_score": results.loc["Geraldine Ponce", "pdiv_score"],
            }

        except Exception as e:
            return False, {"error": str(e)}

    def test_pipeline_integration(self):
        """Test 4: Integración completa del pipeline"""
        try:
            # Crear pipeline PDIV con directorio de prueba
            pipeline = PDIVPipeline(region="tepic")
            pipeline.base_path = self.test_dir
            pipeline.setup_paths()

            # Crear datos de prueba
            test_file = self.create_test_data()

            # Ejecutar pipeline completo
            results = pipeline.run_complete_pipeline("test_data.json")

            # Verificaciones
            checks = [
                "metadata" in results,
                "pdiv_scores" in results,
                "matriz_posicionamiento" in results,
                "narrativas_descubiertas" in results,
                results["metadata"]["datos_anonimizados"] == True,
                results["metadata"]["pii_protegida"] == True,
            ]

            return all(checks), {
                "has_metadata": "metadata" in results,
                "has_pdiv_scores": "pdiv_scores" in results,
                "has_matrix": "matriz_posicionamiento" in results,
                "has_narratives": "narrativas_descubiertas" in results,
                "anonymized": results["metadata"]["datos_anonimizados"],
                "pii_protected": results["metadata"]["pii_protegida"],
            }

        except Exception as e:
            return False, {"error": str(e)}

    def test_performance(self):
        """Test 5: Performance del pipeline"""
        import time

        # Crear dataset más grande
        large_data = []
        for i in range(100):
            large_data.append(
                {
                    "id": f"perf_test_{i}",
                    "source": "instagram",
                    "text": f"Texto de prueba número {i} para evaluación de rendimiento del sistema de procesamiento de datos políticos",
                    "user": f"user_{i}",
                    "user_id": f"user_id_{i}",
                    "date": "2026-04-24T10:00:00Z",
                    "likes": i * 10,
                    "shares": i * 2,
                    "comments": i,
                    "candidate": "Candidato Test",
                }
            )

        test_file = self.raw_dir / "performance_test.json"
        with open(test_file, "w", encoding="utf-8") as f:
            json.dump(large_data, f, indent=2)

        config = AnonymizationConfig()
        pipeline = DataIngestionPipeline(config=config, base_path=self.test_dir)

        # Medir tiempo de procesamiento
        start_time = time.time()
        results = pipeline.process_file(test_file)
        end_time = time.time()

        processing_time = end_time - start_time
        records_per_second = len(large_data) / processing_time if processing_time > 0 else float("inf")

        # Verificar performance (<5 segundos para 100 registros = >20 reg/sec)
        success = processing_time < 5.0 and results["valid_records"] > 90

        return success, {
            "processing_time": processing_time,
            "records_processed": results["valid_records"],
            "records_per_second": records_per_second,
            "target_time": 5.0,
            "target_rps": 20.0,
        }

    def run_all_tests(self):
        """Ejecuta todos los tests"""
        print("=" * 80)
        print("SAIEL PIPELINE TEST SUITE - RUNNING ALL TESTS")
        print("=" * 80)

        # Definir tests
        tests = [
            ("Anonymization Test", self.test_anonymization),
            ("Schema Validation Test", self.test_schema_validation),
            ("PDIV Calculation Test", self.test_pdiv_calculation),
            ("Pipeline Integration Test", self.test_pipeline_integration),
            ("Performance Test", self.test_performance),
        ]

        # Ejecutar tests
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)

        # Generar reporte final
        self.generate_test_report()

        # Limpiar ambiente
        self.cleanup()

    def generate_test_report(self):
        """Genera reporte de resultados"""
        print("\n" + "=" * 80)
        print("TEST SUITE REPORT")
        print("=" * 80)

        total_tests = self.test_results["tests_passed"] + self.test_results["tests_failed"]
        pass_rate = (self.test_results["tests_passed"] / total_tests * 100) if total_tests > 0 else 0

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.test_results['tests_passed']}")
        print(f"Failed: {self.test_results['tests_failed']}")
        print(f"Pass Rate: {pass_rate:.1f}%")

        print("\nDetailed Results:")
        for detail in self.test_results["test_details"]:
            status_icon = "✅" if detail["status"] == "PASSED" else "❌"
            print(f"{status_icon} {detail['test']}: {detail['status']}")
            if detail["status"] != "PASSED":
                print(f"   Details: {detail['details']}")

        # Guardar reporte
        report_file = self.test_dir / "test_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)

        print(f"\nDetailed report saved to: {report_file}")

        return pass_rate >= 80  # Considerar éxito si >=80% pasan

    def cleanup(self):
        """Limpia ambiente de testing"""
        try:
            shutil.rmtree(self.test_dir)
            print(f"\nTest environment cleaned up: {self.test_dir}")
        except Exception as e:
            print(f"Error cleaning up: {e}")


# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    tester = PipelineTester()
    success = tester.run_all_tests()

    if success:
        print("\n🎉 PIPELINE TEST SUITE PASSED!")
        exit(0)
    else:
        print("\n⚠️  PIPELINE TEST SUITE FAILED!")
        exit(1)
