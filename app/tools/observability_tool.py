"""
Tool de Observabilidade para ADK
"""

import asyncio
import time
from typing import Dict, Any, Optional
from datetime import datetime
from app.adk.simple_adk import Tool
from app.services.supabase_observability import supabase_observability_service

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
            # Delega para o serviço de observabilidade do Supabase
            return await supabase_observability_service.log_interaction(
                user_id=user_id,
                channel=channel,
                input_data=input_data,
                agent_chosen=agent_chosen,
                response=response,
                execution_time_ms=execution_time_ms,
                routing_decision=routing_decision,
                cost_tokens=cost_tokens,
                confidence=confidence
            )
            
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
        Registra handoff entre agentes
        """
        try:
            return await supabase_observability_service.log_agent_handoff(
                user_id=user_id,
                from_agent=from_agent,
                to_agent=to_agent,
                reason=reason,
                context=context
            )
        except Exception as e:
            await self._log_error("log_agent_handoff", str(e)[:100])
            return False
    
    async def log_error(
        self,
        error_type: str,
        error_message: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Registra erros no sistema de observabilidade
        """
        try:
            return await supabase_observability_service.log_error(
                error_type=error_type,
                error_message=error_message,
                user_id=user_id,
                context=context
            )
        except Exception as e:
            print(f"Erro ao registrar erro: {e}")
            return False
    
    async def log_performance_metric(
        self,
        metric_name: str,
        value: float,
        unit: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Registra métricas de performance
        """
        try:
            return await supabase_observability_service.log_performance_metric(
                metric_name=metric_name,
                value=value,
                unit=unit,
                user_id=user_id,
                metadata=metadata
            )
        except Exception as e:
            await self._log_error("log_performance_metric", str(e)[:100])
            return False
    
    async def log_session_event(
        self,
        user_id: str,
        event_type: str,
        details: Dict[str, Any]
    ) -> bool:
        """
        Registra eventos de sessão
        """
        try:
            return await supabase_observability_service.log_session_event(
                user_id=user_id,
                event_type=event_type,
                details=details
            )
        except Exception as e:
            await self._log_error("log_session_event", str(e)[:100])
            return False
    
    async def _log_error(self, method_name: str, error_message: str) -> None:
        """
        Método auxiliar para registrar erros internos
        """
        try:
            await supabase_observability_service.log_error(
                error_type=f"observability_tool_{method_name}",
                error_message=error_message
            )
        except Exception:
            # Evita loops infinitos de erro
            pass
    
    async def _get_current_session_id(self, user_id: str) -> Optional[str]:
        """
        Recupera ID da sessão atual do usuário
        """
        try:
            # Implementação simplificada - em produção seria mais robusta
            return f"session_{user_id}_{int(time.time())}"
        except Exception:
            return None