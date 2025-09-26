"""
Tool de Observabilidade para ADK
"""

import asyncio
import time
from typing import Dict, Any, Optional
from datetime import datetime
from app.adk.simple_adk import Tool
from app.services.memory import memory_manager

class ObservabilityTool(Tool):
    """Tool de observabilidade e telemetria para ADK"""
    
    def __init__(self):
        super().__init__(
            name="observability_tool",
            description="Registra telemetria, logs e métricas de performance"
        )
    
    async def execute(self, *args, **kwargs):
        """Implementação do método abstrato execute"""
        return {"success": True, "message": "Observability tool executed"}
    
    async def log_interaction(
        self,
        user_id: str,
        channel: str,
        input_data: Dict[str, Any],
        agent_chosen: str,
        response: str,
        execution_time_ms: float,
        routing_decision: Dict[str, Any],
        cost_tokens: Optional[int] = None,
        confidence: Optional[float] = None
    ) -> bool:
        """
        Registra uma interação completa no sistema de observabilidade
        """
        try:
            log_entry = {
                "user_id": user_id,
                "channel": channel,
                "timestamp": datetime.now().isoformat(),
                "input": {
                    "type": input_data.get("type", "text"),
                    "content_preview": str(input_data.get("content", ""))[:100],
                    "has_image": "image" in input_data
                },
                "agent_chosen": agent_chosen,
                "response_preview": response[:100],
                "performance": {
                    "execution_time_ms": execution_time_ms,
                    "cost_tokens": cost_tokens
                },
                "routing": {
                    "confidence": confidence,
                    "decision": routing_decision,
                    "fallback_used": confidence and confidence < 0.7
                },
                "session_id": await self._get_current_session_id(user_id)
            }
            
            await memory_manager.save_observability_log(log_entry)
            return True
            
        except Exception as e:
            # Log de erro sem expor dados sensíveis
            await self._log_error("log_interaction", str(e)[:100])
            return False
    
    async def log_agent_handoff(
        self,
        user_id: str,
        from_agent: str,
        to_agent: str,
        reason: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        Registra transferência entre agentes
        """
        try:
            handoff_entry = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "handoff": {
                    "from_agent": from_agent,
                    "to_agent": to_agent,
                    "reason": reason,
                    "context_summary": str(context)[:200]
                },
                "session_id": await self._get_current_session_id(user_id)
            }
            
            await memory_manager.save_observability_log(handoff_entry)
            return True
            
        except Exception as e:
            await self._log_error("log_agent_handoff", str(e)[:100])
            return False
    
    async def log_session_event(
        self,
        user_id: str,
        event_type: str,
        details: Dict[str, Any]
    ) -> bool:
        """
        Registra eventos de sessão (criação, timeout, encerramento)
        """
        try:
            session_event = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "details": details,
                "session_id": await self._get_current_session_id(user_id)
            }
            
            await memory_manager.save_observability_log(session_event)
            return True
            
        except Exception as e:
            await self._log_error("log_session_event", str(e)[:100])
            return False
    
    async def get_performance_metrics(
        self,
        user_id: Optional[str] = None,
        time_range_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Recupera métricas de performance
        """
        try:
            metrics = await memory_manager.get_performance_metrics(
                user_id=user_id,
                time_range_hours=time_range_hours
            )
            return metrics
        except Exception as e:
            await self._log_error("get_performance_metrics", str(e)[:100])
            return {}
    
    async def _get_current_session_id(self, user_id: str) -> str:
        """Recupera ID da sessão atual"""
        try:
            session = await memory_manager.get_active_session(user_id)
            return session.get("id", "") if session else ""
        except Exception:
            return ""
    
    async def _log_error(self, operation: str, error_message: str) -> None:
        """Log de erro interno"""
        try:
            error_log = {
                "timestamp": datetime.now().isoformat(),
                "operation": operation,
                "error": error_message,
                "level": "ERROR"
            }
            await memory_manager.save_observability_log(error_log)
        except Exception:
            # Falha silenciosa para evitar loops de erro
            pass
