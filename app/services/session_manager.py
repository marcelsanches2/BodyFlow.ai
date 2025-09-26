"""
Sistema de Sessão Persistente para Agentes
"""

import time
from typing import Dict, Any, Optional

# Cache em memória para sessões ativas (temporário até resolver problema do Supabase)
_active_sessions_cache = {}

class SessionManager:
    """Gerenciador de sessões ativas para agentes"""
    
    @staticmethod
    async def set_active_session(user_id: str, agent_name: str):
        """Define agente ativo para usuário"""
        try:
            # Usa cache em memória temporariamente
            _active_sessions_cache[user_id] = {
                "active_agent": agent_name,
                "session_start": time.time(),
                "last_interaction": time.time()
            }
            
            print(f"🔒 Sessão ativa definida: {agent_name} para usuário {user_id}")
            
        except Exception as e:
            print(f"❌ Erro ao definir sessão ativa: {e}")
    
    @staticmethod
    async def get_active_session(user_id: str) -> Optional[Dict[str, Any]]:
        """Recupera sessão ativa do usuário"""
        try:
            # Usa cache em memória temporariamente
            return _active_sessions_cache.get(user_id)
            
        except Exception as e:
            print(f"❌ Erro ao recuperar sessão ativa: {e}")
            return None
    
    @staticmethod
    async def clear_active_session(user_id: str):
        """Limpa sessão ativa do usuário"""
        try:
            if user_id in _active_sessions_cache:
                del _active_sessions_cache[user_id]
                print(f"🔓 Sessão ativa limpa para usuário {user_id}")
            
        except Exception as e:
            print(f"❌ Erro ao limpar sessão ativa: {e}")
    
    @staticmethod
    async def update_last_interaction(user_id: str):
        """Atualiza última interação do usuário"""
        try:
            if user_id in _active_sessions_cache:
                _active_sessions_cache[user_id]["last_interaction"] = time.time()
            
        except Exception as e:
            print(f"❌ Erro ao atualizar última interação: {e}")
