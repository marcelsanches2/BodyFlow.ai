from typing import Dict, Any, List
import random
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.utils.messages import UserMessages

class AgenteDieta:
    """
    Agente responsável por responder sobre dietas e nutrição
    """
    
    def __init__(self):
        # Estrutura simples para futuras implementações
        self.dietas_perda_peso = [UserMessages.Dieta.PERDER_PESO_RESPONSE]
        self.dietas_ganho_massa = [UserMessages.Dieta.GANHAR_MASSA_RESPONSE]
        self.dietas_manter_peso = [UserMessages.Dieta.MANTER_PESO_RESPONSE]
        self.dietas_saudaveis = [UserMessages.Dieta.DIETA_SAUDAVEL_RESPONSE]
    
    async def processar(self, estado: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa a mensagem e retorna sugestões de dieta
        
        Args:
            estado: Estado contendo mensagem, histórico e contexto
        
        Returns:
            Dict: Estado atualizado com resposta do agente
        """
        mensagem = estado.get("mensagem", "").lower()
        resposta = ""
        
        # Identifica o objetivo da dieta
        if any(palavra in mensagem for palavra in ["perder", "emagrecer", "reduzir", "diminuir", "queimar"]):
            resposta = random.choice(self.dietas_perda_peso)
        elif any(palavra in mensagem for palavra in ["ganhar", "aumentar", "massa", "musculo", "bulking"]):
            resposta = random.choice(self.dietas_ganho_massa)
        elif any(palavra in mensagem for palavra in ["manter", "manutenção", "equilibrio", "saudavel"]):
            resposta = random.choice(self.dietas_manter_peso)
        else:
            # Resposta genérica para dieta
            resposta = UserMessages.Dieta.WELCOME_MESSAGE
        
        # Adiciona dicas nutricionais
        dicas = UserMessages.Dieta.DICAS
        resposta += random.choice(dicas)
        
        # Atualiza o estado com a resposta
        estado["resposta"] = resposta
        estado["agente_usado"] = "AgenteDieta"
        
        return estado