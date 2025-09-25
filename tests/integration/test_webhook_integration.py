#!/usr/bin/env python3
"""
Testes de integração para webhook do WhatsApp
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app

class TestWebhookIntegration:
    """Testes de integração para webhook"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.client = TestClient(app)
    
    def test_webhook_status_endpoint(self):
        """Testa endpoint de status"""
        # Testa o canal ativo (Telegram)
        response = self.client.get("/telegram/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert data["channel"] == "telegram"
        assert data["active"] == True
    
    def test_webhook_telegram_endpoint_structure(self):
        """Testa estrutura do endpoint Telegram"""
        # Simula dados de entrada do Telegram
        webhook_data = {
            "message": {
                "message_id": 123,
                "from": {"id": 123456789, "first_name": "Test"},
                "chat": {"id": 123456789, "first_name": "Test", "type": "private"},
                "date": 1640995200,
                "text": "treino"
            }
        }
        
        # Mock do memory_manager para evitar chamadas reais ao Supabase
        with patch('app.api.v1.telegram.memory_manager') as mock_memory:
            mock_memory.get_user_by_phone = AsyncMock(return_value=None)
            mock_memory.get_user_history = AsyncMock(return_value=[])
            mock_memory.save_message = AsyncMock(return_value=True)
            
            # Mock do telegram_bot
            with patch('app.api.v1.telegram.telegram_bot', None):
                response = self.client.post("/telegram/", json=webhook_data)
                
                # Verifica se retorna 200
                assert response.status_code == 200
                
                # Verifica se retorna JSON
                data = response.json()
                assert data["status"] == "ok"
    
    def test_webhook_telegram_setup_endpoint(self):
        """Testa endpoint de setup do webhook do Telegram"""
        # Mock do telegram_bot
        with patch('app.api.v1.telegram.telegram_bot') as mock_bot:
            mock_bot.set_webhook = AsyncMock(return_value=True)
            
            response = self.client.post("/telegram/setup-webhook?webhook_url=https://test.com/telegram/")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
    
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
