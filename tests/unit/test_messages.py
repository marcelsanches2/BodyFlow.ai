#!/usr/bin/env python3
"""
Testes unitários para as mensagens
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from app.utils.messages import UserMessages

class TestUserMessages:
    """Testes para UserMessages"""
    
    def test_messages_exist(self):
        """Testa se todas as mensagens existem"""
        # Mensagens de boas-vindas
        assert hasattr(UserMessages, 'FIRST_CONTACT_GREETING')
        assert hasattr(UserMessages, 'WELCOME_NOT_REGISTERED')
        assert hasattr(UserMessages, 'ACCOUNT_INACTIVE')
        
        # Mensagens de erro
        assert hasattr(UserMessages, 'PROCESSING_ERROR')
        assert hasattr(UserMessages, 'USER_NOT_FOUND_ERROR')
    
    def test_treino_messages_exist(self):
        """Testa se mensagens de treino existem"""
        assert hasattr(UserMessages.Treino, 'WELCOME_MESSAGE')
        assert hasattr(UserMessages.Treino, 'PERNAS_RESPONSE')
        assert hasattr(UserMessages.Treino, 'PEITO_RESPONSE')
        assert hasattr(UserMessages.Treino, 'COSTAS_RESPONSE')
        assert hasattr(UserMessages.Treino, 'COMPLETO_RESPONSE')
        assert hasattr(UserMessages.Treino, 'DICAS')
    
    def test_dieta_messages_exist(self):
        """Testa se mensagens de dieta existem"""
        assert hasattr(UserMessages.Dieta, 'WELCOME_MESSAGE')
        assert hasattr(UserMessages.Dieta, 'PERDER_PESO_RESPONSE')
        assert hasattr(UserMessages.Dieta, 'GANHAR_MASSA_RESPONSE')
        assert hasattr(UserMessages.Dieta, 'MANTER_PESO_RESPONSE')
        assert hasattr(UserMessages.Dieta, 'DIETA_SAUDAVEL_RESPONSE')
        assert hasattr(UserMessages.Dieta, 'DICAS')
    
    def test_router_messages_exist(self):
        """Testa se mensagens de roteamento existem"""
        assert hasattr(UserMessages.Router, 'DEFAULT_RESPONSE')
        assert hasattr(UserMessages.Router, 'UNKNOWN_COMMAND')
    
    def test_messages_are_strings(self):
        """Testa se todas as mensagens são strings"""
        # Testa mensagens principais
        assert isinstance(UserMessages.FIRST_CONTACT_GREETING, str)
        assert isinstance(UserMessages.WELCOME_NOT_REGISTERED, str)
        assert isinstance(UserMessages.ACCOUNT_INACTIVE, str)
        
        # Testa mensagens de treino
        assert isinstance(UserMessages.Treino.WELCOME_MESSAGE, str)
        assert isinstance(UserMessages.Treino.PERNAS_RESPONSE, str)
        
        # Testa mensagens de dieta
        assert isinstance(UserMessages.Dieta.WELCOME_MESSAGE, str)
        assert isinstance(UserMessages.Dieta.PERDER_PESO_RESPONSE, str)
        
        # Testa mensagens de roteamento
        assert isinstance(UserMessages.Router.DEFAULT_RESPONSE, str)
        assert isinstance(UserMessages.Router.UNKNOWN_COMMAND, str)
    
    def test_messages_not_empty(self):
        """Testa se mensagens não estão vazias"""
        # Testa mensagens principais
        assert len(UserMessages.FIRST_CONTACT_GREETING) > 0
        assert len(UserMessages.WELCOME_NOT_REGISTERED) > 0
        assert len(UserMessages.ACCOUNT_INACTIVE) > 0
        
        # Testa mensagens de treino
        assert len(UserMessages.Treino.WELCOME_MESSAGE) > 0
        assert len(UserMessages.Treino.PERNAS_RESPONSE) > 0
        
        # Testa mensagens de dieta
        assert len(UserMessages.Dieta.WELCOME_MESSAGE) > 0
        assert len(UserMessages.Dieta.PERDER_PESO_RESPONSE) > 0
        
        # Testa mensagens de roteamento
        assert len(UserMessages.Router.DEFAULT_RESPONSE) > 0
        assert len(UserMessages.Router.UNKNOWN_COMMAND) > 0

if __name__ == "__main__":
    # Executa os testes se rodado diretamente
    import unittest
    unittest.main()
