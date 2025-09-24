#!/usr/bin/env python3
"""
Testes de integração para webhook do WhatsApp
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
import asyncio
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from app.main import app

class TestWebhookIntegration:
    """Testes de integração para webhook"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.client = TestClient(app)
    
    def test_webhook_status_endpoint(self):
        """Testa endpoint de status"""
        response = self.client.get("/whatsapp/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "active"
        assert data["service"] == "BodyFlow WhatsApp Bot"
        assert data["version"] == "1.0.0"
    
    def test_webhook_whatsapp_endpoint_structure(self):
        """Testa estrutura do endpoint WhatsApp"""
        # Simula dados de entrada do Twilio
        form_data = {
            "From": "whatsapp:+5511940751013",
            "Body": "teste",
            "MessageSid": "SM123456"
        }
        
        # Mock do memory_manager para evitar chamadas reais ao Supabase
        with patch('app.api.v1.whatsapp.memory_manager') as mock_memory:
            mock_memory.get_user_by_phone.return_value = None
            mock_memory.get_user_history.return_value = []
            mock_memory.save_message.return_value = True
            
            response = self.client.post("/whatsapp/", data=form_data)
            
            # Verifica se retorna 200
            assert response.status_code == 200
            
            # Verifica se retorna TwiML
            assert "application/xml" in response.headers["content-type"]
            assert "<?xml" in response.text
            assert "<Response>" in response.text
            assert "<Message>" in response.text
    
    def test_webhook_status_callback_endpoint(self):
        """Testa endpoint de status callback"""
        form_data = {
            "MessageSid": "SM123456",
            "MessageStatus": "delivered",
            "To": "whatsapp:+5511940751013",
            "From": "whatsapp:+14155238886",
            "ErrorCode": "",
            "ErrorMessage": ""
        }
        
        # Mock do memory_manager
        with patch('app.api.v1.whatsapp.memory_manager') as mock_memory:
            # Mock assíncrono para save_message
            async def mock_save_message(*args, **kwargs):
                return True
            mock_memory.save_message = mock_save_message
            
            response = self.client.post("/whatsapp/status-callback", data=form_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "received"
    
    def test_webhook_test_ultra_simple_endpoint(self):
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

if __name__ == "__main__":
    # Executa os testes se rodado diretamente
    import unittest
    unittest.main()
