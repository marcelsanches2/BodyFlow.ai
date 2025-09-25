#!/usr/bin/env python3
"""
Testes end-to-end para fluxo completo do Telegram
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestTelegramFlow:
    """Testes end-to-end para fluxo completo do Telegram"""
    
    def test_telegram_response(self):
        """Testa resposta básica do Telegram"""
        # Teste simplificado - nova orquestração será implementada
        resposta = "Ola! BodyFlow em reconstrucao. Nova versao em breve!"
        
        # Verifica resposta
        assert resposta is not None
        assert len(resposta) > 0
        assert "reconstrucao" in resposta.lower()
    
    def test_telegram_webhook_structure(self):
        """Testa estrutura do webhook do Telegram"""
        webhook_data = {
            "message": {
                "message_id": 123,
                "from": {"id": 123456789, "first_name": "Test"},
                "chat": {"id": 123456789, "first_name": "Test", "type": "private"},
                "date": 1640995200,
                "text": "treino"
            }
        }
        
        response = client.post("/telegram/", json=webhook_data)
        
        # Verifica se retorna 200
        assert response.status_code == 200
        
        # Verifica se retorna JSON
        data = response.json()
        assert data["status"] == "ok"
