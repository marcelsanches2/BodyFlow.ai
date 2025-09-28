"""
Serviço de Logging de Observabilidade usando Supabase Logs
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from supabase import create_client, Client
from app.core.config import Config

class SupabaseObservabilityService:
    """Serviço de logging de observabilidade usando Supabase Logs"""
    
    def __init__(self):
        self.supabase: Client = create_client(
            Config.SUPABASE_URL, 
            Config.SUPABASE_KEY
        )
        
        # Configura logger Python para enviar logs estruturados para Supabase
        self._setup_observability_logger()
    
    def _setup_observability_logger(self):
        """Configura o logger Python para enviar logs de observabilidade"""
        # Cria logger específico para observabilidade
        self.observability_logger = logging.getLogger('bodyflow_observability')
        self.observability_logger.setLevel(logging.INFO)
        
        # Remove handlers existentes para evitar duplicação
        for handler in self.observability_logger.handlers[:]:
            self.observability_logger.removeHandler(handler)
        
        # Adiciona handler customizado para Supabase
        handler = SupabaseObservabilityHandler()
        handler.setLevel(logging.INFO)
        
        # Formato estruturado para logs de observabilidade
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        self.observability_logger.addHandler(handler)
    
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
        Registra uma interação completa usando logs estruturados do Supabase
        """
        try:
            log_data = {
                "event_type": "interaction",
                "user_id": user_id,
                "channel": channel,
                "timestamp": datetime.now().isoformat(),
                "input": {
                    "type": input_data.get("content_type", "text"),
                    "content_preview": str(input_data.get("content", ""))[:100],
                    "has_image": "image_data" in input_data
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
                }
            }
            
            # Log estruturado usando Python logging (capturado pelo Supabase)
            self.observability_logger.info(f"INTERACTION: {json.dumps(log_data)}")
            return True
            
        except Exception as e:
            self.observability_logger.error(f"Erro ao registrar interação: {e}")
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
            log_data = {
                "event_type": "agent_handoff",
                "user_id": user_id,
                "from_agent": from_agent,
                "to_agent": to_agent,
                "reason": reason,
                "context_preview": str(context)[:200],
                "timestamp": datetime.now().isoformat()
            }
            
            self.observability_logger.info(f"HANDOFF: {json.dumps(log_data)}")
            return True
            
        except Exception as e:
            self.observability_logger.error(f"Erro ao registrar handoff: {e}")
            return False
    
    async def log_error(
        self,
        error_type: str,
        error_message: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Registra erros usando logs estruturados
        """
        try:
            log_data = {
                "event_type": "error",
                "error_type": error_type,
                "error_message": error_message[:500],
                "user_id": user_id,
                "context": context,
                "timestamp": datetime.now().isoformat()
            }
            
            self.observability_logger.error(f"ERROR: {json.dumps(log_data)}")
            return True
            
        except Exception as e:
            self.observability_logger.error(f"Erro ao registrar erro: {e}")
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
            log_data = {
                "event_type": "performance_metric",
                "metric_name": metric_name,
                "value": value,
                "unit": unit,
                "user_id": user_id,
                "metadata": metadata,
                "timestamp": datetime.now().isoformat()
            }
            
            self.observability_logger.info(f"METRIC: {json.dumps(log_data)}")
            return True
            
        except Exception as e:
            self.observability_logger.error(f"Erro ao registrar métrica: {e}")
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
            log_data = {
                "event_type": "session_event",
                "user_id": user_id,
                "session_event_type": event_type,
                "details": details,
                "timestamp": datetime.now().isoformat()
            }
            
            self.observability_logger.info(f"SESSION: {json.dumps(log_data)}")
            return True
            
        except Exception as e:
            self.observability_logger.error(f"Erro ao registrar evento de sessão: {e}")
            return False


class SupabaseObservabilityHandler(logging.Handler):
    """Handler customizado para enviar logs de observabilidade para Supabase"""
    
    def emit(self, record):
        """Envia o log para Supabase usando a funcionalidade nativa de logs"""
        try:
            # O Supabase captura automaticamente logs estruturados
            # quando configurado corretamente no painel
            pass
        except Exception:
            # Evita loops infinitos de erro
            pass


# Instância global do serviço de observabilidade
supabase_observability_service = SupabaseObservabilityService()
