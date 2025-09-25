#!/usr/bin/env python3
"""
Configuração para endpoints de teste
"""

import os

class TestConfig:
    """Configuração para endpoints de teste"""
    
    # Controla se endpoints de teste estão habilitados
    ENABLE_TEST_ENDPOINTS = os.getenv("ENABLE_TEST_ENDPOINTS", "true").lower() == "true"
    
    # Prefixo para endpoints de teste
    TEST_PREFIX = "/test"
    
    # Tags para documentação
    TEST_TAGS = ["Test"]
    
    # Configurações específicas para desenvolvimento
    DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"
    
    # Endpoints disponíveis apenas em desenvolvimento
    DEV_ONLY_ENDPOINTS = [
        "/test/debug-user/{phone}",
        "/test/webhook-logic",
        "/test/memory"
    ]
