#!/usr/bin/env python3
"""
Testes unitários para os agentes
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from app.agents.treino import AgenteTreino
from app.agents.dieta import AgenteDieta

class TestAgenteTreino:
    """Testes para o AgenteTreino"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.agente = AgenteTreino()
    
    def test_init(self):
        """Testa inicialização do agente"""
        assert self.agente is not None
        assert hasattr(self.agente, 'treinos_pernas')
        assert hasattr(self.agente, 'treinos_peito')
        assert hasattr(self.agente, 'treinos_costas')
        assert hasattr(self.agente, 'treinos_completos')
    
    @pytest.mark.asyncio
    async def test_processar_treino_pernas(self):
        """Testa processamento de treino de pernas"""
        estado = {"mensagem": "treino de pernas"}
        resultado = await self.agente.processar(estado)
        
        assert "resposta" in resultado
        assert "agente_usado" in resultado
        assert resultado["agente_usado"] == "AgenteTreino"
        assert "pernas" in resultado["resposta"].lower()
    
    @pytest.mark.asyncio
    async def test_processar_treino_peito(self):
        """Testa processamento de treino de peito"""
        estado = {"mensagem": "treino de peito"}
        resultado = await self.agente.processar(estado)
        
        assert "resposta" in resultado
        assert "agente_usado" in resultado
        assert resultado["agente_usado"] == "AgenteTreino"
        assert "peito" in resultado["resposta"].lower()

class TestAgenteDieta:
    """Testes para o AgenteDieta"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.agente = AgenteDieta()
    
    def test_init(self):
        """Testa inicialização do agente"""
        assert self.agente is not None
        assert hasattr(self.agente, 'dietas_perda_peso')
        assert hasattr(self.agente, 'dietas_ganho_massa')
        assert hasattr(self.agente, 'dietas_manter_peso')
        assert hasattr(self.agente, 'dietas_saudaveis')
    
    @pytest.mark.asyncio
    async def test_processar_dieta_perder_peso(self):
        """Testa processamento de dieta para perder peso"""
        estado = {"mensagem": "dieta para perder peso"}
        resultado = await self.agente.processar(estado)
        
        assert "resposta" in resultado
        assert "agente_usado" in resultado
        assert resultado["agente_usado"] == "AgenteDieta"
        assert "peso" in resultado["resposta"].lower()
    
    @pytest.mark.asyncio
    async def test_processar_dieta_ganhar_massa(self):
        """Testa processamento de dieta para ganhar massa"""
        estado = {"mensagem": "dieta para ganhar massa"}
        resultado = await self.agente.processar(estado)
        
        assert "resposta" in resultado
        assert "agente_usado" in resultado
        assert resultado["agente_usado"] == "AgenteDieta"
        assert "massa" in resultado["resposta"].lower()

if __name__ == "__main__":
    # Executa os testes se rodado diretamente
    import unittest
    unittest.main()
