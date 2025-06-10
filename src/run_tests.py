import pytest
import sys
import os
from datetime import datetime

def run_activity_tests():
    """Ejecuta las pruebas de actividades y genera reporte"""
    
    print("="*60)
    print("EJECUTANDO PRUEBAS TDD - SISTEMA SIGISI")
    print("="*60)
    print(f"Fecha y hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Configurar pytest con opciones detalladas
    pytest_args = [
        'tests/activities/test_register_activities_controller.py',
        'tests/export/test_excel_export_controller.py',
        '-v',  # Verbose
        '--tb=short',  # Traceback corto
        '--capture=no',  # Mostrar prints
        '--color=yes',  # Colores en terminal
        '--durations=10'  # Mostrar las 10 pruebas más lentas
    ]
    
    print("🚀 INICIANDO PRUEBAS DE CREACIÓN DE INFORMES...")
    print("-" * 40)
    
    # Ejecutar solo pruebas de actividades primero
    activity_result = pytest.main([
        'tests/activities/test_register_activities_controller.py',
        '-v', '--tb=short', '--capture=no'
    ])
    
    print("\n" + "="*60)
    print("📊 INICIANDO PRUEBAS DE EXPORTACIÓN DE EXCEL...")
    print("-" * 40)
    
    # Ejecutar pruebas de exportación
    export_result = pytest.main([
        'tests/export/test_excel_export_controller.py',
        '-v', '--tb=short', '--capture=no'
    ])
    
    # Resumen final
    print("\n" + "="*60)
    print("📋 RESUMEN DE RESULTADOS")
    print("="*60)
    
    activity_status = "✅ EXITOSO" if activity_result == 0 else "❌ FALLÓ"
    export_status = "✅ EXITOSO" if export_result == 0 else "❌ FALLÓ"
    
    print(f"Pruebas de Creación de Informes: {activity_status}")
    print(f"Pruebas de Exportación Excel: {export_status}")
    
    overall_status = "✅ TODAS LAS PRUEBAS EXITOSAS" if (activity_result == 0 and export_result == 0) else "❌ ALGUNAS PRUEBAS FALLARON"
    print(f"\nEstado General: {overall_status}")
    print("="*60)
    
    return activity_result == 0 and export_result == 0

if __name__ == "__main__":
    success = run_activity_tests()
    sys.exit(0 if success else 1)