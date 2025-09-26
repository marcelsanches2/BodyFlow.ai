"""
Router Central Multi-canal para ADK
"""

import asyncio
import time
from typing import Dict, Any, Optional
from datetime import datetime
from app.adk.simple_adk import Node
from app.tools.memory_tool import MemoryTool
from app.tools.observability_tool import ObservabilityTool
from app.tools.multimodal_tool import MultimodalTool

class RouterNode(Node):
    """Nó de roteamento inicial do ADK"""
    
    def __init__(self):
        super().__init__(
            name="router_node",
            description="Router central multi-canal e multi-modal"
        )
        self.memory_tool = MemoryTool()
        self.observability_tool = ObservabilityTool()
        self.multimodal_tool = MultimodalTool()
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa entrada e roteia para orquestrador apropriado
        """
        start_time = time.time()
        
        try:
            # Extrai dados da entrada
            user_id = input_data.get("user_id", "")
            channel = input_data.get("channel", "unknown")
            content = input_data.get("content", "")
            content_type = input_data.get("content_type", "text")
            
            # Verifica timeout de sessão
            session_expired = await self.memory_tool.check_session_timeout(user_id)
            if session_expired:
                await self._handle_session_timeout(user_id)
            
            # Determina tipo de conteúdo
            if content_type == "image":
                # Roteia para orquestrador de imagem
                result = await self._route_to_image_orchestrator(input_data)
            else:
                # Roteia para orquestrador de texto
                result = await self._route_to_text_orchestrator(input_data)
            
            # Registra observabilidade
            execution_time = (time.time() - start_time) * 1000
            await self.observability_tool.log_interaction(
                user_id=user_id,
                channel=channel,
                input_data=input_data,
                agent_chosen=result.get("orchestrator", "unknown"),
                response=result.get("response", ""),
                execution_time_ms=execution_time,
                routing_decision=result.get("routing_decision", {}),
                confidence=result.get("confidence")
            )
            
            return {
                "success": True,
                "response": result.get("response", ""),
                "agent_activated": result.get("agent_activated", ""),
                "metadata": {
                    "orchestrator": result.get("orchestrator"),
                    "confidence": result.get("confidence"),
                    "execution_time_ms": execution_time,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            # Log de erro
            execution_time = (time.time() - start_time) * 1000
            await self.observability_tool.log_interaction(
                user_id=input_data.get("user_id", ""),
                channel=input_data.get("channel", "unknown"),
                input_data=input_data,
                agent_chosen="error",
                response=f"Erro interno: {str(e)[:100]}",
                execution_time_ms=execution_time,
                routing_decision={"error": str(e)[:100]},
                confidence=0.0
            )
            
            return {
                "success": False,
                "response": "Desculpe, ocorreu um erro interno. Tente novamente.",
                "agent_activated": "error",
                "metadata": {
                    "error": str(e)[:100],
                    "execution_time_ms": execution_time
                }
            }
    
    async def _route_to_text_orchestrator(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Roteia para orquestrador de texto"""
        from app.adk.text_orchestrator import TextOrchestratorNode
        
        orchestrator = TextOrchestratorNode()
        result = await orchestrator.process(input_data)
        
        return {
            "orchestrator": "text_orchestrator",
            "response": result.get("response", ""),
            "agent_activated": result.get("agent_activated", ""),
            "confidence": result.get("confidence", 0.0),
            "routing_decision": result.get("routing_decision", {})
        }
    
    async def _route_to_image_orchestrator(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Roteia para orquestrador de imagem"""
        from app.adk.image_orchestrator import ImageOrchestratorNode
        
        # Prepara dados específicos para o Image Orchestrator
        image_input = {
            **input_data,
            "image_type": "image"  # Define o tipo de imagem
        }
        
        orchestrator = ImageOrchestratorNode()
        result = await orchestrator.process(image_input)
        
        return {
            "orchestrator": "image_orchestrator",
            "response": result.get("response", ""),
            "agent_activated": result.get("agent_activated", ""),
            "confidence": result.get("confidence", 0.0),
            "routing_decision": result.get("routing_decision", {})
        }
    
    async def _handle_session_timeout(self, user_id: str) -> None:
        """Gerencia timeout de sessão"""
        try:
            # Marca sessão anterior como encerrada
            await self.memory_tool.update_session_summary(
                user_id, 
                "Sessão encerrada por timeout", 
                "timeout"
            )
            
            # Cria nova sessão
            await self.memory_tool.create_new_session(user_id)
            
            # Log do evento
            await self.observability_tool.log_session_event(
                user_id,
                "session_timeout",
                {"action": "new_session_created"}
            )
            
        except Exception as e:
            await self.observability_tool.log_session_event(
                user_id,
                "session_timeout_error",
                {"error": str(e)[:100]}
            )
