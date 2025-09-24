#!/usr/bin/env python3
"""
Script para executar testes do BodyFlow Backend
"""

import sys
import os
import subprocess

def run_tests(test_type="all"):
    """
    Executa testes baseado no tipo especificado
    
    Args:
        test_type: "unit", "integration", "e2e", ou "all"
    """
    
    if test_type == "unit":
        test_path = "tests/unit"
        print("🧪 Executando testes unitários...")
    elif test_type == "integration":
        test_path = "tests/integration"
        print("🔗 Executando testes de integração...")
    elif test_type == "e2e":
        test_path = "tests/e2e"
        print("🎯 Executando testes end-to-end...")
    else:
        test_path = "tests"
        print("🚀 Executando todos os testes...")
    
    try:
        # Executa pytest
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            test_path, 
            "-v", 
            "--tb=short"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Erros:", result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Erro ao executar testes: {e}")
        return False

def main():
    """Função principal"""
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
    else:
        test_type = "all"
    
    print(f"📋 Executando testes: {test_type}")
    print("=" * 50)
    
    success = run_tests(test_type)
    
    if success:
        print("✅ Todos os testes passaram!")
    else:
        print("❌ Alguns testes falharam!")
        sys.exit(1)

if __name__ == "__main__":
    main()
