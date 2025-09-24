#!/usr/bin/env python3
"""
Testes end-to-end para fluxo completo do WhatsApp
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
import asyncio
from unittest.mock import Mock, patch
from app.graph import bodyflow_graph
from app.services.memory import memory_manager

class TestWhatsAppFlow:
    """Testes end-to-end para fluxo do WhatsApp"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.test_phone = "whatsapp:+5511940751013"
    
    @pytest.mark.asyncio
    async def test_complete_treino_flow(self):
        """Testa fluxo completo de treino"""
        # Mock do memory_manager
        with patch.object(memory_manager, 'get_user_history') as mock_history, \
             patch.object(memory_manager, 'save_message') as mock_save:
            
            mock_history.return_value = []
            mock_save.return_value = True
            
            # Simula mensagem de treino
            mensagem = "treino de pernas"
            
            # Processa mensagem
            resposta = await bodyflow_graph.processar_mensagem(self.test_phone, mensagem)
            
            # Verifica resposta
            assert resposta is not None
            assert len(resposta) > 0
            assert "pernas" in resposta.lower() or "treino" in resposta.lower()
    
    @pytest.mark.asyncio
    async def test_complete_dieta_flow(self):
        """Testa fluxo completo de dieta"""
        # Mock do memory_manager
        with patch.object(memory_manager, 'get_user_history') as mock_history, \
             patch.object(memory_manager, 'save_message') as mock_save:
            
            mock_history.return_value = []
            mock_save.return_value = True
            
            # Simula mensagem de dieta
            mensagem = "dieta para perder peso"
            
            # Processa mensagem
            resposta = await bodyflow_graph.processar_mensagem(self.test_phone, mensagem)
            
            # Verifica resposta
            assert resposta is not None
            assert len(resposta) > 0
            assert "peso" in resposta.lower() or "dieta" in resposta.lower()
    
    @pytest.mark.asyncio
    async def test_complete_default_flow(self):
        """Testa fluxo padrão"""
        # Mock do memory_manager
        with patch.object(memory_manager, 'get_user_history') as mock_history, \
             patch.object(memory_manager, 'save_message') as mock_save:
            
            mock_history.return_value = []
            mock_save.return_value = True
            
            # Simula mensagem genérica
            mensagem = "oi, como vai?"
            
            # Processa mensagem
            resposta = await bodyflow_graph.processar_mensagem(self.test_phone, mensagem)
            
            # Verifica resposta
            assert resposta is not None
            assert len(resposta) > 0
            assert "treino" in resposta.lower() or "dieta" in resposta.lower()
    
    @pytest.mark.asyncio
    async def test_first_contact_greeting(self):
        """Testa saudação de primeiro contato"""
        # Mock do memory_manager
        with patch.object(memory_manager, 'get_user_history') as mock_history, \
             patch.object(memory_manager, 'save_message') as mock_save:
            
            # Simula primeiro contato (sem histórico)
            mock_history.return_value = []
            mock_save.return_value = True
            
            # Simula mensagem de primeiro contato
            mensagem = "oi"
            
            # Processa mensagem
            resposta = await bodyflow_graph.processar_mensagem(self.test_phone, mensagem)
            
            # Verifica se inclui saudação
            assert resposta is not None
            assert len(resposta) > 0
            # A saudação deve estar incluída na resposta

if __name__ == "__main__":
    # Executa os testes se rodado diretamente
    import unittest
    unittest.main()
