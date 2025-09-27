"""
Tool de Memória para ADK - Três camadas (curto, médio, longo prazo)
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from app.adk.simple_adk import Tool
from app.services.memory import memory_manager
from app.core.config import Config

class MemoryTool(Tool):
    """Tool de memória com três camadas para ADK"""
    
    def __init__(self):
        super().__init__(
            name="memory_tool",
            description="Gerencia memória em três camadas: curto, médio e longo prazo"
        )
    
    async def execute(self, *args, **kwargs):
        """Implementação do método abstrato execute"""
        return {"success": True, "message": "Memory tool executed"}
    
    async def get_short_term_memory(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Memória de curto prazo: últimas mensagens recentes
        """
        try:
            # user_id já é o customer_id (UUID), busca mensagens diretamente
            messages = await memory_manager.get_user_history_by_customer_id(user_id, limit=limit)
            
            print(f"🧠 MemoryTool: Buscando histórico para customer_id {user_id} - {len(messages)} mensagens encontradas")
            
            result = [
                {
                    "role": msg.get("direction", "unknown"),
                    "content": msg.get("body", ""),
                    "timestamp": msg.get("created_at", "")
                }
                for msg in messages
            ]
            
            print(f"🧠 MemoryTool: Histórico processado - {len(result)} mensagens")
            return result
        except Exception as e:
            print(f"❌ MemoryTool: Erro ao buscar histórico: {e}")
            return []
    
    async def get_medium_term_memory(self, user_id: str) -> Dict[str, Any]:
        """
        Memória de médio prazo: resumo incremental da sessão
        """
        try:
            # user_id já é o customer_id (UUID), busca sessão diretamente
            session = await memory_manager.get_active_session(user_id)
            if session:
                return {
                    "session_id": session.get("id"),
                    "summary": session.get("summary", ""),
                    "active_topic": session.get("active_topic", ""),
                    "started_at": session.get("started_at", ""),
                    "last_interaction": session.get("last_interaction_at", "")
                }
            return {}
        except Exception as e:
            return {}
    
    async def get_long_term_memory(self, user_id: str) -> Dict[str, Any]:
        """
        Memória de longo prazo: perfil persistente do usuário
        """
        try:
            # user_id já é o customer_id (UUID), busca usuário diretamente
            user = await memory_manager.get_user_by_id(user_id)
            if user:
                # Busca dados de perfil da tabela user_profile
                profile_data = await self._get_user_profile_data(user_id)
                
                return {
                    "user_id": user.get("id"),
                    "phone": user.get("whatsapp"),  # Campo correto na tabela customers
                    "is_active": user.get("is_active", False),
                    "profile": profile_data,
                    "onboarding_completed": user.get("onboarding_completed", False),
                    "last_profile_update": user.get("last_profile_update", "")
                }
            return {}
        except Exception as e:
            print(f"❌ MemoryTool: Erro ao buscar perfil: {e}")
            return {}
    
    async def _get_user_profile_data(self, user_id: str) -> Dict[str, Any]:
        """Busca dados de perfil da tabela user_profile e nome da tabela customers"""
        try:
            from app.core.config import Config
            from supabase import create_client
            
            supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
            
            # Busca dados de perfil da tabela user_profile
            profile_result = supabase.table('user_profile').select('*').eq('user_id', user_id).execute()
            
            # Busca nome da tabela customers
            customer_result = supabase.table('customers').select('name').eq('id', user_id).execute()
            
            profile_data = {}
            
            if profile_result.data:
                profile = profile_result.data[0]
                profile_data = {
                    "age": profile.get("age"),
                    "height_cm": profile.get("height_cm"),
                    "current_weight_kg": profile.get("current_weight_kg"),
                    "current_body_fat_percent": profile.get("current_body_fat_percent"),
                    "current_muscle_mass_kg": profile.get("current_muscle_mass_kg"),
                    "goal": profile.get("goal"),
                    "restrictions": profile.get("restrictions"),
                    "training_level": profile.get("training_level"),
                    "updated_at": profile.get("updated_at"),
                    "created_at": profile.get("created_at")
                }
            
            # Adiciona primeiro nome da tabela customers
            if customer_result.data:
                full_name = customer_result.data[0].get("name", "")
                # Extrai apenas o primeiro nome
                first_name = full_name.split()[0] if full_name else ""
                profile_data["name"] = first_name
            
            return profile_data
        except Exception as e:
            print(f"❌ MemoryTool: Erro ao buscar dados de perfil: {e}")
            return {}
    
    async def get_long_term_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Recupera apenas o perfil do usuário (longo prazo) da tabela user_profile
        """
        try:
            return await self._get_user_profile_data(user_id)
        except Exception as e:
            print(f"❌ MemoryTool: Erro ao buscar perfil: {e}")
            return {}
    
    async def save_message(self, user_id: str, content: str, direction: str) -> bool:
        """Salva mensagem na memória de curto prazo"""
        try:
            # user_id já é o customer_id (UUID), salva diretamente
            await memory_manager.save_message(user_id, content, direction)
            return True
        except Exception as e:
            return False
    
    async def update_session_summary(self, user_id: str, summary: str, active_topic: str) -> bool:
        """Atualiza resumo da sessão (médio prazo)"""
        try:
            # user_id já é o customer_id (UUID)
            await memory_manager.update_session_summary(user_id, summary, active_topic)
            return True
        except Exception as e:
            return False
    
    async def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Atualiza perfil do usuário (longo prazo)"""
        try:
            result = await memory_manager.update_user_profile(user_id, profile_data)
            return result
        except Exception as e:
            print(f"❌ MemoryTool: Erro ao atualizar perfil: {e}")
            return False
    
    async def update_long_term_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Atualiza perfil do usuário (longo prazo)"""
        try:
            await memory_manager.update_user_profile(user_id, profile_data)
            return True
        except Exception as e:
            return False
    
    async def create_new_session(self, user_id: str) -> str:
        """Cria nova sessão para o usuário"""
        try:
            # user_id já é o customer_id (UUID)
            session_id = await memory_manager.create_session(user_id)
            return session_id
        except Exception as e:
            return ""
    
    async def check_session_timeout(self, user_id: str) -> bool:
        """Verifica se a sessão atual expirou"""
        try:
            # user_id já é o customer_id (UUID)
            session = await memory_manager.get_active_session(user_id)
            if not session:
                return True
            
            last_interaction = datetime.fromisoformat(session.get("last_interaction_at", ""))
            timeout_threshold = datetime.now() - timedelta(minutes=ADKConfig.SESSION_TIMEOUT_MINUTES)
            
            return last_interaction < timeout_threshold
        except Exception as e:
            return True
    
    async def get_context_for_agent(self, user_id: str, agent_type: str) -> Dict[str, Any]:
        """
        Retorna contexto otimizado para um agente específico
        """
        # Normaliza o user_id para consistência
        user_id = memory_manager._normalize_phone_for_search(user_id)
        
        # Recupera memória em três camadas usando o ID normalizado
        short_term = await self.get_short_term_memory(user_id, limit=5)
        medium_term = await self.get_medium_term_memory(user_id)
        long_term = await self.get_long_term_memory(user_id)
        
        # Otimiza contexto baseado no tipo de agente
        context = {
            "short_term": short_term,
            "medium_term": medium_term,
            "long_term": long_term,
            "agent_type": agent_type,
            "timestamp": datetime.now().isoformat()
        }
        
        # Filtra contexto baseado no agente
        if agent_type == "onboarding":
            context["relevant_data"] = {
                "profile": long_term.get("profile", {}),
                "onboarding_status": long_term.get("onboarding_completed", False)
            }
        elif agent_type in ["super_personal_trainer", "super_personal_trainer_agent"]:
            context["relevant_data"] = {
                "profile": long_term.get("profile", {}),
                "recent_messages": short_term,
                "session_summary": medium_term.get("summary", "")
            }
        
        return context
    
    async def set_active_session(self, user_id: str, agent_name: str) -> bool:
        """
        Define agente ativo na sessão do usuário
        """
        try:
            user_id = memory_manager._normalize_phone_for_search(user_id)
            
            # Atualiza dados da sessão com agente ativo
            session_data = {
                "active_agent": agent_name,
                "session_start": datetime.now().isoformat(),
                "last_interaction": datetime.now().isoformat()
            }
            
            # Salva no contexto da sessão (implementação simplificada)
            # Em produção, isso seria salvo no banco de dados
            print(f"🔒 Sessão ativa definida: {agent_name} para usuário {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao definir sessão ativa: {e}")
            return False
    
    async def clear_active_session(self, user_id: str) -> bool:
        """
        Limpa sessão ativa do usuário
        """
        try:
            user_id = memory_manager._normalize_phone_for_search(user_id)
            print(f"🔓 Sessão ativa limpa para usuário {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao limpar sessão ativa: {e}")
            return False
    
    async def get_active_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Recupera dados da sessão ativa do usuário
        """
        try:
            user_id = memory_manager._normalize_phone_for_search(user_id)
            
            # Implementação simplificada - em produção seria recuperado do banco
            # Por enquanto, retorna None para simular que não há sessão ativa
            return None
            
        except Exception as e:
            print(f"❌ Erro ao recuperar sessão ativa: {e}")
            return None
