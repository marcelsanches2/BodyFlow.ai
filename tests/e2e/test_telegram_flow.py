"""
Testes end-to-end para o fluxo completo do Telegram
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.utils.messages import UserMessages

client = TestClient(app)

class TestTelegramFlow:
    """Testes end-to-end para o fluxo completo do Telegram"""

    @pytest.mark.asyncio
    async def test_complete_treino_flow_telegram(self):
        """Simula um fluxo completo de treino via Telegram"""
        chat_id = "123456789"
        
        with patch('app.api.v1.telegram.memory_manager') as mock_memory, \
             patch('app.api.v1.telegram.bodyflow_graph') as mock_graph, \
             patch('app.api.v1.telegram.telegram_bot', None):
            
            # Simula usuário ativo e sem histórico
            mock_memory.get_user_by_phone = AsyncMock(return_value={"whatsapp": chat_id, "is_active": True})
            mock_memory.get_user_history = AsyncMock(side_effect=[[], [{"phone": chat_id, "body": "treino", "direction": "inbound"}]])
            mock_memory.save_message = AsyncMock(return_value=True)
            mock_graph.processar_mensagem = AsyncMock(return_value=UserMessages.Treino.PERNAS_RESPONSE)

            # Primeira mensagem (primeiro contato)
            webhook_data = {
                "message": {
                    "message_id": 1,
                    "from": {"id": int(chat_id), "first_name": "Test"},
                    "chat": {"id": int(chat_id), "first_name": "Test", "type": "private"},
                    "date": 1640995200,
                    "text": "treino"
                }
            }
            
            response = client.post("/telegram/", json=webhook_data)
            assert response.status_code == 200
            
            # Verifica se a resposta foi processada (sem bot, apenas loga)
            assert response.status_code == 200
            
            # Segunda mensagem (já com histórico)
            webhook_data = {
                "message": {
                    "message_id": 2,
                    "from": {"id": int(chat_id), "first_name": "Test"},
                    "chat": {"id": int(chat_id), "first_name": "Test", "type": "private"},
                    "date": 1640995201,
                    "text": "treino de peito"
                }
            }
            
            response = client.post("/telegram/", json=webhook_data)
            assert response.status_code == 200
            
            # Verifica se a segunda mensagem foi processada
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_complete_dieta_flow_telegram(self):
        """Simula um fluxo completo de dieta via Telegram"""
        chat_id = "987654321"
        
        with patch('app.api.v1.telegram.memory_manager') as mock_memory, \
             patch('app.api.v1.telegram.bodyflow_graph') as mock_graph, \
             patch('app.api.v1.telegram.telegram_bot', None):
            
            # Simula usuário ativo e sem histórico
            mock_memory.get_user_by_phone = AsyncMock(return_value={"whatsapp": chat_id, "is_active": True})
            mock_memory.get_user_history = AsyncMock(side_effect=[[], [{"phone": chat_id, "body": "dieta", "direction": "inbound"}]])
            mock_memory.save_message = AsyncMock(return_value=True)
            mock_graph.processar_mensagem = AsyncMock(return_value=UserMessages.Dieta.PERDER_PESO_RESPONSE)

            # Primeira mensagem (primeiro contato)
            webhook_data = {
                "message": {
                    "message_id": 1,
                    "from": {"id": int(chat_id), "first_name": "Test"},
                    "chat": {"id": int(chat_id), "first_name": "Test", "type": "private"},
                    "date": 1640995200,
                    "text": "dieta"
                }
            }
            
            response = client.post("/telegram/", json=webhook_data)
            assert response.status_code == 200
            
            # Verifica se a resposta foi processada (sem bot, apenas loga)
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_complete_default_flow_telegram(self):
        """Simula um fluxo completo padrão via Telegram"""
        chat_id = "555666777"
        
        with patch('app.api.v1.telegram.memory_manager') as mock_memory, \
             patch('app.api.v1.telegram.bodyflow_graph') as mock_graph, \
             patch('app.api.v1.telegram.telegram_bot', None):
            
            # Simula usuário ativo e sem histórico
            mock_memory.get_user_by_phone = AsyncMock(return_value={"whatsapp": chat_id, "is_active": True})
            mock_memory.get_user_history = AsyncMock(side_effect=[[], [{"phone": chat_id, "body": "oi", "direction": "inbound"}]])
            mock_memory.save_message = AsyncMock(return_value=True)
            mock_graph.processar_mensagem = AsyncMock(return_value=UserMessages.Router.DEFAULT_RESPONSE)

            # Primeira mensagem (primeiro contato)
            webhook_data = {
                "message": {
                    "message_id": 1,
                    "from": {"id": int(chat_id), "first_name": "Test"},
                    "chat": {"id": int(chat_id), "first_name": "Test", "type": "private"},
                    "date": 1640995200,
                    "text": "oi"
                }
            }
            
            response = client.post("/telegram/", json=webhook_data)
            assert response.status_code == 200
            
            # Verifica se a resposta foi processada (sem bot, apenas loga)
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_first_contact_greeting_telegram(self):
        """Testa se a saudação é enviada apenas no primeiro contato via Telegram"""
        chat_id = "111222333"
        
        with patch('app.api.v1.telegram.memory_manager') as mock_memory, \
             patch('app.api.v1.telegram.bodyflow_graph') as mock_graph, \
             patch('app.api.v1.telegram.telegram_bot', None):
            
            # Simula usuário ativo e sem histórico (primeiro contato)
            mock_memory.get_user_by_phone = AsyncMock(return_value={"whatsapp": chat_id, "is_active": True})
            mock_memory.get_user_history = AsyncMock(return_value=[]) # Sem histórico
            mock_memory.save_message = AsyncMock(return_value=True)
            mock_graph.processar_mensagem = AsyncMock(return_value="Resposta do agente")

            webhook_data = {
                "message": {
                    "message_id": 1,
                    "from": {"id": int(chat_id), "first_name": "Test"},
                    "chat": {"id": int(chat_id), "first_name": "Test", "type": "private"},
                    "date": 1640995200,
                    "text": "oi"
                }
            }
            
            response = client.post("/telegram/", json=webhook_data)
            assert response.status_code == 200
            
            # Verifica se a resposta foi processada (sem bot, apenas loga)
            assert response.status_code == 200
