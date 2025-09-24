from typing import Dict, Any, List
from app.agents.treino import AgenteTreino
from app.agents.dieta import AgenteDieta
from app.services.memory import memory_manager
from app.utils.messages import UserMessages

class BodyFlowGraph:
    """
    Sistema de agentes simplificado para orquestrar as conversas
    """
    
    def __init__(self):
        self.agente_treino = AgenteTreino()
        self.agente_dieta = AgenteDieta()
    
    def _route_message(self, mensagem: str) -> str:
        """
        Função de roteamento que determina qual agente deve processar a mensagem
        
        Args:
            mensagem: Mensagem do usuário
        
        Returns:
            str: Condição de roteamento ('treino', 'dieta' ou 'default')
        """
        mensagem_lower = mensagem.lower()
        
        # Palavras-chave para treino
        palavras_treino = [
            "treino", "exercicio", "exercício", "academia", "musculacao", 
            "musculação", "perna", "peito", "costas", "biceps", "triceps",
            "agachamento", "supino", "remada", "puxada", "halteres", "barra"
        ]
        
        # Palavras-chave para dieta
        palavras_dieta = [
            "dieta", "alimentacao", "alimentação", "nutricao", "nutrição",
            "comida", "refeicao", "refeição", "caloria", "proteina", "proteína",
            "carboidrato", "emagrecer", "engordar", "massa", "peso"
        ]
        
        # Verifica se a mensagem contém palavras-chave de treino
        if any(palavra in mensagem_lower for palavra in palavras_treino):
            return "treino"
        
        # Verifica se a mensagem contém palavras-chave de dieta
        if any(palavra in mensagem_lower for palavra in palavras_dieta):
            return "dieta"
        
        # Resposta padrão para mensagens não identificadas
        return "default"
    
    async def processar_mensagem(self, phone: str, mensagem: str) -> str:
        """
        Processa uma mensagem completa usando o sistema de agentes
        
        Args:
            phone: Número do telefone do usuário
            mensagem: Mensagem recebida
        
        Returns:
            str: Resposta gerada pelos agentes
        """
        try:
            # Carrega histórico do usuário
            historico = await memory_manager.get_user_history(phone, limit=5)
            
            # Cria estado inicial
            estado = {
                "mensagem": mensagem,
                "phone": phone,
                "historico": historico,
                "contexto": self._extrair_contexto(historico)
            }
            
            # Determina qual agente usar
            rota = self._route_message(mensagem)
            
            # Processa com o agente apropriado
            if rota == "treino":
                estado_final = await self.agente_treino.processar(estado)
            elif rota == "dieta":
                estado_final = await self.agente_dieta.processar(estado)
            else:
                estado_final = await self._process_default(estado)
            
            # Salva a mensagem recebida
            await memory_manager.save_message(phone, mensagem, "inbound")
            
            # Retorna a resposta
            return estado_final.get("resposta", UserMessages.PROCESSING_ERROR)
            
        except Exception as e:
            print(f"Erro ao processar mensagem: {e}")
            return UserMessages.PROCESSING_ERROR
    
    async def _process_default(self, estado: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa mensagens que não se encaixam em treino ou dieta
        
        Args:
            estado: Estado da conversa
        
        Returns:
            Dict: Estado atualizado com resposta padrão
        """
        resposta = UserMessages.Router.DEFAULT_RESPONSE
        
        estado["resposta"] = resposta
        estado["agente_usado"] = "DefaultResponse"
        
        return estado
    
    def _extrair_contexto(self, historico: List[Dict[str, Any]]) -> str:
        """
        Extrai contexto relevante do histórico de mensagens
        
        Args:
            historico: Lista de mensagens anteriores
        
        Returns:
            str: Contexto resumido
        """
        if not historico:
            return "Primeira conversa com o usuário."
        
        # Pega as últimas 3 mensagens do usuário
        mensagens_usuario = [
            msg["body"] for msg in historico 
            if msg["direction"] == "inbound"
        ][:3]
        
        if mensagens_usuario:
            return f"Contexto recente: {' | '.join(mensagens_usuario)}"
        
        return "Usuário retornando após período sem conversa."

# Instância global do grafo
bodyflow_graph = BodyFlowGraph()
