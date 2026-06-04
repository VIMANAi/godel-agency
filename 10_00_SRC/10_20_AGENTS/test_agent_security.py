# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");

"""Script de pruebas automatizadas de seguridad para el Agente Godel.

Este script valida de forma estática que las políticas de menor privilegio,
hooks interactivos y rutas permitidas se comporten exactamente según lo diseñado.
"""

from config.security import is_path_allowed, is_writing_outside


def run_tests():
    print("=" * 60)
    print("🧪 INICIANDO PRUEBAS AUTOMATIZADAS DE SEGURIDAD PARA GODEL")
    print("=" * 60)

    # 1. Rutas de Prueba
    safe_agency_path = "/home/fratfn/Desarrollo/Agency/src/core/test.py"
    safe_db_path = "/home/fratfn/Desarrollo/Databases/chromadb_store/index.db"
    unsafe_home_path = "/home/fratfn/documentos_importantes.txt"
    unsafe_system_path = "/etc/passwd"

    print("\n🔍 Validando políticas de acceso a directorios (is_path_allowed):")

    # Caso 1: Ruta segura en Agency
    assert is_path_allowed(safe_agency_path) is True, "❌ Falla: Debería permitir acceso en Agency"
    print(f"   [OK] Permitida ruta de Agency: {safe_agency_path}")

    # Caso 2: Ruta segura en Databases
    assert is_path_allowed(safe_db_path) is True, "❌ Falla: Debería permitir acceso en Databases"
    print(f"   [OK] Permitida ruta de Databases: {safe_db_path}")

    # Caso 3: Ruta insegura en Home
    assert is_path_allowed(unsafe_home_path) is False, "❌ Falla: Debería rechazar acceso en Home"
    print(f"   [OK] Rechazada ruta externa en Home: {unsafe_home_path}")

    # Caso 4: Ruta insegura en Sistema
    assert is_path_allowed(unsafe_system_path) is False, "❌ Falla: Debería rechazar acceso en Sistema"
    print(f"   [OK] Rechazada ruta del sistema: {unsafe_system_path}")

    print("\n🔍 Validando políticas de escritura (is_writing_outside):")

    # Caso 5: Escritura en zona segura
    args_safe = {"TargetFile": safe_agency_path}
    assert is_writing_outside(args_safe) is False, "❌ Falla: Escritura en zona segura debería ser libre"
    print(f"   [OK] Escritura segura libre de confirmación: {safe_agency_path}")

    # Caso 6: Escritura en zona insegura
    args_unsafe = {"TargetFile": unsafe_home_path}
    assert (
        is_writing_outside(args_unsafe) is True
    ), "❌ Falla: Escritura en zona insegura debería exigir Hook interactivo"
    print(f"   [OK] Escritura externa atrapada para confirmación: {unsafe_home_path}")

    print("\n" + "=" * 60)
    print("🎉 TODAS LAS PRUEBAS DE SEGURIDAD PASARON CON ÉXITO [100% OK]")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
