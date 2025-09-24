from typing import Dict, Any, List
import random
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.utils.messages import UserMessages

class AgenteTreino:
    """
    Agente responsável por responder sobre treinos e exercícios
    """
    
    def __init__(self):
        # Estrutura simples para futuras implementações
        self.treinos_pernas = [UserMessages.Treino.PERNAS_RESPONSE]
        self.treinos_peito = [UserMessages.Treino.PEITO_RESPONSE]
        self.treinos_costas = [UserMessages.Treino.COSTAS_RESPONSE]
        self.treinos_completos = [UserMessages.Treino.COMPLETO_RESPONSE]
    
    async def processar(self, estado: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa a mensagem e retorna sugestões de treino
        
        Args:
            estado: Estado contendo mensagem, histórico e contexto
        
        Returns:
            Dict: Estado atualizado com resposta do agente
        """
        mensagem = estado.get("mensagem", "").lower()
        resposta = ""
        
        # Identifica o tipo de treino solicitado
        if any(palavra in mensagem for palavra in ["perna", "pernas", "quadríceps", "posterior"]):
            resposta = random.choice(self.treinos_pernas)
        elif any(palavra in mensagem for palavra in ["peito", "peitoral", "supino"]):
            resposta = random.choice(self.treinos_peito)
        elif any(palavra in mensagem for palavra in ["costa", "costas", "dorsal", "remada"]):
            resposta = random.choice(self.treinos_costas)
        elif any(palavra in mensagem for palavra in ["completo", "full", "abc", "dividido"]):
            resposta = random.choice(self.treinos_completos)
        else:
            # Resposta genérica para treino
            resposta = UserMessages.Treino.WELCOME_MESSAGE
        
        # Adiciona dicas extras
        dicas = UserMessages.Treino.DICAS
        resposta += random.choice(dicas)
        
        # Atualiza o estado com a resposta
        estado["resposta"] = resposta
        estado["agente_usado"] = "AgenteTreino"
        
        return estado