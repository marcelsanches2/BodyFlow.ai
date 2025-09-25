"""
Testes de integração para os endpoints do Telegram
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.utils.messages import UserMessages

client = TestClient(app)

class TestTelegramIntegration:
    """Testes de integração para os endpoints do Telegram"""

    def test_telegram_status_endpoint(self):
        """Testa o endpoint de status do Telegram"""
        response = client.get("/telegram/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["channel"] == "telegram"

    def test_telegram_webhook_endpoint_structure(self):
        """Testa se o endpoint principal do Telegram retorna JSON"""
        webhook_data = {
            "message": {
                "message_id": 123,
                "from": {
                    "id": 123456789,
                    "is_bot": False,
                    "first_name": "Test",
                    "username": "testuser"
                },
                "chat": {
                    "id": 123456789,
                    "first_name": "Test",
                    "username": "testuser",
                    "type": "private"
                },
                "date": 1640995200,
                "text": "treino"
            }
        }
        
        # Mock do memory_manager para simular usuário ativo e sem histórico
        with patch('app.api.v1.telegram.memory_manager') as mock_memory:
            mock_memory.get_user_by_phone = AsyncMock(return_value={"whatsapp": "123456789", "is_active": True})
            mock_memory.get_user_history = AsyncMock(return_value=[]) # Sem histórico
            mock_memory.save_message = AsyncMock(return_value=True) # Mock assíncrono
            
            # Mock do bodyflow_graph
            with patch('app.api.v1.telegram.bodyflow_graph') as mock_graph:
                mock_graph.processar_mensagem = AsyncMock(return_value="Resposta do agente")
                
                # Mock do telegram_bot
                with patch('app.api.v1.telegram.telegram_bot', None):
                    
                    response = client.post("/telegram/", json=webhook_data)
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert data["status"] == "ok"

    def test_telegram_webhook_with_user_not_found(self):
        """Testa webhook do Telegram com usuário não encontrado"""
        webhook_data = {
            "message": {
                "message_id": 123,
                "from": {
                    "id": 123456789,
                    "is_bot": False,
                    "first_name": "Test"
                },
                "chat": {
                    "id": 123456789,
                    "first_name": "Test",
                    "type": "private"
                },
                "date": 1640995200,
                "text": "oi"
            }
        }
        
        # Mock do memory_manager para simular usuário não encontrado
        with patch('app.api.v1.telegram.memory_manager') as mock_memory:
            mock_memory.get_user_by_phone = AsyncMock(return_value=None)
            mock_memory.save_message = AsyncMock(return_value=True)
            
            # Mock do telegram_bot
            with patch('app.api.v1.telegram.telegram_bot', None):
                
                response = client.post("/telegram/", json=webhook_data)
                
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "ok"

    def test_telegram_webhook_with_inactive_user(self):
        """Testa webhook do Telegram com usuário inativo"""
        webhook_data = {
            "message": {
                "message_id": 123,
                "from": {
                    "id": 123456789,
                    "is_bot": False,
                    "first_name": "Test"
                },
                "chat": {
                    "id": 123456789,
                    "first_name": "Test",
                    "type": "private"
                },
                "date": 1640995200,
                "text": "oi"
            }
        }
        
        # Mock do memory_manager para simular usuário inativo
        with patch('app.api.v1.telegram.memory_manager') as mock_memory:
            mock_memory.get_user_by_phone = AsyncMock(return_value={"whatsapp": "123456789", "is_active": False})
            mock_memory.save_message = AsyncMock(return_value=True)
            
            # Mock do telegram_bot
            with patch('app.api.v1.telegram.telegram_bot', None):
                
                response = client.post("/telegram/", json=webhook_data)
                
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "ok"

    def test_telegram_webhook_empty_message(self):
        """Testa webhook do Telegram com mensagem vazia"""
        webhook_data = {}
        
        response = client.post("/telegram/", json=webhook_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_telegram_webhook_missing_chat_id(self):
        """Testa webhook do Telegram sem chat_id"""
        webhook_data = {
            "message": {
                "message_id": 123,
                "from": {
                    "id": 123456789,
                    "is_bot": False,
                    "first_name": "Test"
                },
                "date": 1640995200,
                "text": "oi"
            }
        }
        
        response = client.post("/telegram/", json=webhook_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_telegram_webhook_missing_text(self):
        """Testa webhook do Telegram sem texto"""
        webhook_data = {
            "message": {
                "message_id": 123,
                "from": {
                    "id": 123456789,
                    "is_bot": False,
                    "first_name": "Test"
                },
                "chat": {
                    "id": 123456789,
                    "first_name": "Test",
                    "type": "private"
                },
                "date": 1640995200
            }
        }
        
        response = client.post("/telegram/", json=webhook_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
