#!/usr/bin/env python3
"""
Testes unitários para o grafo de agentes
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from app.graph import BodyFlowGraph

class TestBodyFlowGraph:
    """Testes para o BodyFlowGraph"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.graph = BodyFlowGraph()
    
    def test_init(self):
        """Testa inicialização do grafo"""
        assert self.graph is not None
        assert hasattr(self.graph, 'agente_treino')
        assert hasattr(self.graph, 'agente_dieta')
    
    def test_route_message_treino(self):
        """Testa roteamento para treino"""
        mensagem = "treino de pernas"
        rota = self.graph._route_message(mensagem)
        assert rota == "treino"
    
    def test_route_message_dieta(self):
        """Testa roteamento para dieta"""
        mensagem = "dieta para perder peso"
        rota = self.graph._route_message(mensagem)
        assert rota == "dieta"
    
    def test_route_message_default(self):
        """Testa roteamento padrão"""
        mensagem = "oi, como vai?"
        rota = self.graph._route_message(mensagem)
        assert rota == "default"
    
    def test_route_message_keywords_treino(self):
        """Testa palavras-chave de treino"""
        keywords_treino = [
            "treino", "exercicio", "musculacao", "academia",
            "perna", "peito", "costas", "biceps", "triceps"
        ]
        
        for keyword in keywords_treino:
            rota = self.graph._route_message(f"quero {keyword}")
            assert rota == "treino", f"Falhou para: {keyword}"
    
    def test_route_message_keywords_dieta(self):
        """Testa palavras-chave de dieta"""
        keywords_dieta = [
            "dieta", "alimentacao", "nutricao", "comida",
            "perder peso", "emagrecer", "ganhar massa", "massa"
        ]
        
        for keyword in keywords_dieta:
            rota = self.graph._route_message(f"quero {keyword}")
            assert rota == "dieta", f"Falhou para: {keyword}"

if __name__ == "__main__":
    # Executa os testes se rodado diretamente
    import unittest
    unittest.main()
