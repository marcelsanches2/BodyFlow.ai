#!/usr/bin/env python3
"""
Testes de integração para endpoints de teste
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from app.main import app

class TestTestEndpoints:
    """Testes de integração para endpoints de teste"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.client = TestClient(app)
    
    def test_test_status_endpoint(self):
        """Testa endpoint de status dos testes"""
        response = self.client.get("/test/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "test_active"
        assert data["service"] == "BodyFlow Test Endpoints"
        assert data["version"] == "1.0.0"
        assert "endpoints" in data
    
    def test_test_ultra_simple_endpoint(self):
        """Testa endpoint ultra simples"""
        form_data = {
            "From": "whatsapp:+5511940751013",
            "Body": "teste",
            "MessageSid": "SM123456"
        }
        
        response = self.client.post("/test/ultra-simple", data=form_data)
        
        assert response.status_code == 200
        assert "application/xml" in response.headers["content-type"]
        assert "Hi" in response.text
    
    def test_test_webhook_endpoint(self):
        """Testa endpoint de webhook de teste"""
        form_data = {
            "From": "whatsapp:+5511940751013",
            "Body": "teste",
            "MessageSid": "SM123456"
        }
        
        response = self.client.post("/test/webhook", data=form_data)
        
        assert response.status_code == 200
        assert "application/xml" in response.headers["content-type"]
        assert "Teste webhook funcionando!" in response.text
    
    def test_test_webhook_logic_endpoint(self):
        """Testa endpoint de lógica do webhook"""
        # Usa query parameters
        response = self.client.post("/test/webhook-logic?phone=%2B5511940751013&message=treino%20de%20pernas")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processed"
        assert data["agent"] == "treino"
        assert "pernas" in data["response"].lower()
    
    def test_test_debug_user_endpoint(self):
        """Testa endpoint de debug de usuário"""
        response = self.client.get("/test/debug-user/+5511940751013")
        
        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == "+5511940751013"
        assert "user_found" in data
        assert "is_active" in data
    
    def test_test_memory_endpoint(self):
        """Testa endpoint de teste de memória"""
        response = self.client.get("/test/memory")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "supabase_connected" in data

if __name__ == "__main__":
    # Executa os testes se rodado diretamente
    import unittest
    unittest.main()
