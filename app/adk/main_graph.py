"""
Grafo Principal do ADK - BodyFlow
"""

import asyncio
from typing import Dict, Any
from app.adk.simple_adk import AgentDevelopmentKit, Graph
from app.adk.router_node import RouterNode
from app.adk.text_orchestrator import TextOrchestratorNode
from app.adk.image_orchestrator import ImageOrchestratorNode
from app.adk.agents.onboarding_agent import OnboardingAgentNode
from app.adk.agents.super_personal_trainer_agent import SuperPersonalTrainerAgentNode
from app.tools.memory_tool import MemoryTool
from app.tools.observability_tool import ObservabilityTool
from app.tools.multimodal_tool import MultimodalTool

class BodyFlowGraph:
    """Grafo principal do ADK para BodyFlow"""
    
    def __init__(self):
        self.adk = AgentDevelopmentKit({})
        self.graph = self.adk.create_graph()
        self._initialize_graph()
    
    def _initialize_graph(self):
        """Inicializa o grafo do ADK"""
        try:
            # Cria nós do grafo
            router_node = RouterNode()
            text_orchestrator = TextOrchestratorNode()
            image_orchestrator = ImageOrchestratorNode()
            
            # Agentes
            onboarding_agent = OnboardingAgentNode()
            super_personal_trainer_agent = SuperPersonalTrainerAgentNode()
            
            # Tools
            memory_tool = MemoryTool()
            observability_tool = ObservabilityTool()
            multimodal_tool = MultimodalTool()
            
            # Constrói grafo
            self.graph = Graph()
            
            # Adiciona nós
            self.graph.add_node("router", router_node)
            self.graph.add_node("text_orchestrator", text_orchestrator)
            self.graph.add_node("image_orchestrator", image_orchestrator)
            self.graph.add_node("onboarding_agent", onboarding_agent)
            self.graph.add_node("super_personal_trainer_agent", super_personal_trainer_agent)
            
            # Adiciona tools
            self.graph.add_tool("memory_tool", memory_tool)
            self.graph.add_tool("observability_tool", observability_tool)
            self.graph.add_tool("multimodal_tool", multimodal_tool)
            
            # Define conexões do grafo
            self._define_graph_connections()
            
            # Compila grafo
            self.graph.compile()
            
        except Exception as e:
            print(f"Erro ao inicializar grafo ADK: {e}")
            self.graph = None
    
    def _define_graph_connections(self):
        """Define conexões entre nós do grafo"""
        try:
            # Router conecta aos orquestradores
            self.graph.add_edge("router", "text_orchestrator", condition="content_type == 'text'")
            self.graph.add_edge("router", "image_orchestrator", condition="content_type == 'image'")
            
            # Text Orchestrator conecta aos agentes baseado na intenção
            self.graph.add_edge("text_orchestrator", "onboarding_agent", condition="intent == 'onboarding'")
            self.graph.add_edge("text_orchestrator", "super_personal_trainer_agent", condition="intent == 'super_personal_trainer'")
            
            # Image Orchestrator conecta ao Super Personal Trainer
            self.graph.add_edge("image_orchestrator", "super_personal_trainer_agent", condition="image_class in ['food', 'body', 'exercise']")
            
            
        except Exception as e:
            print(f"Erro ao definir conexões do grafo: {e}")
    
    async def process_message(self, user_id: str, content: str, channel: str, content_type: str = "text", image_data: bytes = None) -> Dict[str, Any]:
        """
        Processa mensagem através do grafo ADK
        
        Args:
            user_id: ID do usuário
            content: Conteúdo da mensagem
            channel: Canal de origem (whatsapp, telegram)
            content_type: Tipo de conteúdo (text, image)
            image_data: Dados da imagem (se aplicável)
        
        Returns:
            Dict com resposta e metadados
        """
        try:
            if not self.graph:
                return {
                    "success": False,
                    "response": "Sistema temporariamente indisponível. Tente novamente.",
                    "error": "Graph not initialized"
                }
            
            # Prepara dados de entrada
            input_data = {
                "user_id": user_id,
                "content": content,
                "channel": channel,
                "content_type": content_type,
                "image_data": image_data,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            # Executa grafo
            result = await self.graph.execute(input_data)
            
            return {
                "success": True,
                "response": result.get("response", ""),
                "agent_activated": result.get("agent_activated", ""),
                "metadata": result.get("metadata", {})
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": "Erro interno do sistema. Tente novamente.",
                "error": str(e)[:100]
            }
    
    async def get_graph_status(self) -> Dict[str, Any]:
        """Retorna status do grafo"""
        try:
            if not self.graph:
                return {
                    "status": "error",
                    "message": "Graph not initialized",
                    "nodes": 0,
                    "tools": 0
                }
            
            return {
                "status": "ok",
                "message": "Graph initialized successfully",
                "nodes": len(self.graph.nodes),
                "tools": len(self.graph.tools),
                "anthropic_model": "claude-3-5-sonnet-20241022",
                "session_timeout": 60
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)[:100],
                "nodes": 0,
                "tools": 0
            }

# Instância global do grafo
bodyflow_graph = BodyFlowGraph()
