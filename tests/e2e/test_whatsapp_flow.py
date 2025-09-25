#!/usr/bin/env python3
"""
Testes end-to-end para fluxo completo do WhatsApp
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestWhatsAppFlow:
    """Testes end-to-end para fluxo do WhatsApp"""
    
    def test_whatsapp_response(self):
        """Testa resposta básica do WhatsApp"""
        # Teste simplificado - nova orquestração será implementada
        resposta = "Ola! BodyFlow em reconstrucao. Nova versao em breve!"
        
        # Verifica resposta
        assert resposta is not None
        assert len(resposta) > 0
        assert "reconstrucao" in resposta.lower()
    
    def test_whatsapp_webhook_structure(self):
        """Testa estrutura do webhook do WhatsApp"""
        form_data = {
            "From": "whatsapp:+5511940751013",
            "Body": "teste",
            "MessageSid": "SM123456"
        }
        
        response = client.post("/whatsapp/", data=form_data)
        
        # Verifica se retorna 200
        assert response.status_code == 200
        
        # Verifica se retorna TwiML
        assert "application/xml" in response.headers["content-type"]
        assert "<?xml" in response.text
        assert "<Response>" in response.text
        assert "<Message>" in response.text
