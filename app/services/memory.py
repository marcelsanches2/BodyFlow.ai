from supabase import create_client, Client
from typing import List, Dict, Any, Optional
import sys
import os
import uuid
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from app.core.config import Config
import json
from datetime import datetime, timedelta

class MemoryManager:
    def __init__(self):
        self.supabase: Client = create_client(
            Config.SUPABASE_URL, 
            Config.SUPABASE_KEY
        )
    
    async def save_message(self, phone: str, body: str, direction: str) -> bool:
        """
        Salva uma mensagem no banco de dados
        
        Args:
            phone: Número do telefone
            body: Conteúdo da mensagem
            direction: 'inbound' ou 'outbound'
        
        Returns:
            bool: True se salvou com sucesso
        """
        try:
            # Trunca mensagens muito longas para evitar problemas
            max_body_length = 10000  # 10KB
            truncated_body = body[:max_body_length] if len(body) > max_body_length else body
            
            data = {
                "phone": phone,
                "body": truncated_body,
                "direction": direction[:20] if len(direction) > 20 else direction,  # Limita direction para evitar erro de tamanho
                "created_at": datetime.utcnow().isoformat()
            }
            
            print(f"💾 MemoryManager: Salvando mensagem - {phone}: {direction} - {truncated_body[:50]}...")
            
            result = self.supabase.table("messages").insert(data).execute()
            
            success = len(result.data) > 0
            print(f"💾 MemoryManager: Mensagem salva com sucesso: {success}")
            
            return success
        except Exception as e:
            print(f"Erro ao salvar mensagem: {e}")
            return False


    async def get_user_history(self, phone: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Busca o histórico de mensagens do usuário
        
        Args:
            phone: Número do telefone
            limit: Número máximo de mensagens a retornar
        
        Returns:
            List[Dict]: Lista de mensagens ordenadas por data (mais recente primeiro)
        """
        try:
            # Busca direta sem await (cliente síncrono)
            result = self.supabase.table("messages")\
                .select("*")\
                .eq("phone", phone)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            print(f"🔍 MemoryManager: Buscando histórico para {phone} - {len(result.data) if result.data else 0} mensagens encontradas")
            
            return result.data if result.data else []
        except Exception as e:
            print(f"Erro ao buscar histórico: {e}")
            return []
    
    async def get_user_history_by_customer_id(self, customer_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Busca o histórico de mensagens do usuário pelo customer_id
        
        Args:
            customer_id: ID único do customer
            limit: Número máximo de mensagens a retornar
        
        Returns:
            List[Dict]: Lista de mensagens ordenadas por data (mais recente primeiro)
        """
        try:
            # Busca o número de telefone do customer
            customer_result = self.supabase.table("customers").select("whatsapp").eq("id", customer_id).execute()
            
            if not customer_result.data:
                print(f"❌ Customer não encontrado para ID: {customer_id}")
                return []
                
            phone = customer_result.data[0]["whatsapp"]
            
            # Busca mensagens pelo número de telefone
            result = self.supabase.table("messages")\
                .select("*")\
                .eq("phone", phone)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            print(f"🔍 MemoryManager: Buscando histórico para customer_id {customer_id} (phone: {phone}) - {len(result.data) if result.data else 0} mensagens encontradas")
            
            return result.data if result.data else []
        except Exception as e:
            print(f"Erro ao buscar histórico por customer_id: {e}")
            return []
    


    def _normalize_phone_for_search(self, phone: str) -> str:
        """
        Normaliza o número de telefone para busca no banco
        """
        # Remove prefixo whatsapp:
        clean_phone = phone.replace("whatsapp:", "") if phone.startswith("whatsapp:") else phone
        # Se já está no formato correto (11) 94075-1013, retorna
        if clean_phone.startswith("(") and ")" in clean_phone and "-" in clean_phone:
            return clean_phone
        
        # Remove todos os caracteres não numéricos exceto +
        digits_only = ""
        for char in clean_phone:
            if char.isdigit() or char == "+":
                digits_only += char
        
        # Converte +5511940751013 ou 5511940751013 para (11) 94075-1013
        if digits_only.startswith("+55"):
            # Remove +55
            number = digits_only[3:]
            print(f"   🇧🇷 Número sem +55: {number}")
            if len(number) >= 11:
                # +5511940751013 -> (11) 94075-1013
                ddd = number[:2]
                first_part = number[2:7]
                second_part = number[7:]
                normalized = f"({ddd}) {first_part}-{second_part}"
                print(f"   ✅ Normalizado: {normalized}")
                return normalized
        elif digits_only.startswith("55") and len(digits_only) >= 13:
            # Remove 55 (código do país sem +)
            number = digits_only[2:]
            print(f"   🇧🇷 Número sem 55: {number}")
            if len(number) >= 11:
                # 5511940751013 -> (11) 94075-1013
                ddd = number[:2]
                first_part = number[2:7]
                second_part = number[7:]
                normalized = f"({ddd}) {first_part}-{second_part}"
                print(f"   ✅ Normalizado: {normalized}")
                return normalized
        
        print(f"   ⚠️ Retornando original: {clean_phone}")
        return clean_phone


    async def get_user_by_phone(self, phone: str) -> Dict[str, Any]:
        """
        Busca um usuário pelo número de telefone na tabela customers
        
        Args:
            phone: Número do telefone
        
        Returns:
            Dict: Dados do usuário ou None se não encontrado
        """
        try:
            # Normaliza o número de telefone para busca
            normalized_phone = self._normalize_phone_for_search(phone)
            
            # Busca direta sem await (cliente síncrono)
            result = self.supabase.table("customers")\
                .select("*")\
                .eq("whatsapp", normalized_phone)\
                .execute()
            
            if result.data:
                user = result.data[0]
                return user
            else:
                return None
        except Exception as e:
            print(f"❌ Erro ao buscar usuário: {e}")
            return None

    async def get_user_by_id(self, customer_id: str) -> Dict[str, Any]:
        """
        Busca um usuário pelo customer_id na tabela customers
        
        Args:
            customer_id: ID do usuário (UUID)
        
        Returns:
            Dict: Dados do usuário ou None se não encontrado
        """
        try:
            # Busca direta sem await (cliente síncrono)
            result = self.supabase.table("customers").select("*").eq("id", customer_id).execute()
            
            if result.data:
                user = result.data[0]
                return user
            else:
                return None
                
        except Exception as e:
            print(f"❌ Erro ao buscar usuário por ID: {e}")
            return None

    async def is_user_active(self, phone: str) -> bool:
        """
        Verifica se um usuário está ativo
        
        Args:
            phone: Número do telefone
        
        Returns:
            bool: True se o usuário está ativo
        """
        user = await self.get_user_by_phone(phone)
        return user and user.get("is_active") == True
    

    # Métodos de modificação removidos - apenas consultas na tabela customers
    
    # === MÉTODOS DE SESSÃO ===
    
    async def create_session(self, user_id: str) -> str:
        """Cria nova sessão para o usuário"""
        try:
            # Marca sessões anteriores como inativas
            self.supabase.table("sessions").update({"active": False}).eq("user_id", user_id).execute()
            
            # Cria nova sessão
            session_id = str(uuid.uuid4())
            session_data = {
                "id": session_id,
                "user_id": user_id,
                "active": True,
                "summary": "",
                "active_topic": "",
                "started_at": datetime.now().isoformat(),
                "last_interaction_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table("sessions").insert(session_data).execute()
            return session_id if result.data else ""
            
        except Exception as e:
            print(f"Erro ao criar sessão: {e}")
            return ""
    
    async def get_active_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Recupera sessão ativa do usuário"""
        try:
            result = self.supabase.table("sessions").select("*").eq("user_id", user_id).eq("active", True).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao recuperar sessão ativa: {e}")
            return None
    
    async def update_session_summary(self, user_id: str, summary: str, active_topic: str) -> bool:
        """Atualiza resumo da sessão"""
        try:
            data = {
                "summary": summary[:1000],  # Limita tamanho
                "active_topic": active_topic[:100],
                "last_interaction_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table("sessions").update(data).eq("user_id", user_id).eq("active", True).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Erro ao atualizar resumo da sessão: {e}")
            return False
    
    async def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Atualiza perfil do usuário na tabela user_profile"""
        try:
            # Prepara dados para inserção/atualização na tabela user_profile (sem nome)
            data = {
                "user_id": user_id,
                "age": profile_data.get("age"),
                "height_cm": profile_data.get("height_cm"),
                "current_weight_kg": profile_data.get("current_weight_kg"),
                "current_body_fat_percent": profile_data.get("current_body_fat_percent"),
                "current_muscle_mass_kg": profile_data.get("current_muscle_mass_kg"),
                "goal": profile_data.get("goal"),
                "restrictions": profile_data.get("restrictions"),
                "training_level": profile_data.get("training_level"),
                "updated_at": datetime.now().isoformat()
            }
            
            # Remove campos None para evitar problemas
            data = {k: v for k, v in data.items() if v is not None}
            
            # Verifica se já existe um perfil para este usuário
            existing = self.supabase.table("user_profile").select("id").eq("user_id", user_id).execute()
            
            if existing.data:
                # Atualiza perfil existente
                result = self.supabase.table("user_profile").update(data).eq("user_id", user_id).execute()
                print(f"💾 MemoryManager: Atualizando perfil existente para user_id {user_id}: {len(result.data)} registro(s) atualizado(s)")
            else:
                # Cria novo perfil
                data["created_at"] = datetime.now().isoformat()
                result = self.supabase.table("user_profile").insert(data).execute()
                print(f"💾 MemoryManager: Criando novo perfil para user_id {user_id}: {len(result.data)} registro(s) criado(s)")
            
            # Atualiza apenas timestamp na tabela customers
            self.supabase.table("customers").update({
                "last_profile_update": datetime.now().isoformat()
            }).eq("id", user_id).execute()
            
            return len(result.data) > 0
        except Exception as e:
            print(f"❌ Erro ao atualizar perfil: {e}")
            return False
    
    # === MÉTODOS DE OBSERVABILIDADE ===
    
    async def save_observability_log(self, log_entry: Dict[str, Any]) -> bool:
        """Salva log de observabilidade"""
        try:
            # Converte log_entry para JSON string
            log_json = json.dumps(log_entry)
            
            data = {
                "log_data": log_json,
                "created_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table("observability_logs").insert(data).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Erro ao salvar log de observabilidade: {e}")
            return False
    
    async def get_performance_metrics(self, user_id: Optional[str] = None, time_range_hours: int = 24) -> Dict[str, Any]:
        """Recupera métricas de performance"""
        try:
            # Calcula timestamp de início
            start_time = datetime.now() - timedelta(hours=time_range_hours)
            
            query = self.supabase.table("observability_logs").select("*").gte("created_at", start_time.isoformat())
            
            if user_id:
                # Filtra por usuário específico (requer parsing do JSON)
                query = query.contains("log_data", f'"user_id": "{user_id}"')
            
            result = await query.execute()
            
            # Processa logs para extrair métricas
            metrics = {
                "total_interactions": len(result.data),
                "avg_execution_time": 0,
                "error_rate": 0,
                "agent_distribution": {},
                "confidence_distribution": {}
            }
            
            if result.data:
                execution_times = []
                errors = 0
                
                for log in result.data:
                    try:
                        log_data = json.loads(log["log_data"])
                        
                        # Coleta métricas
                        if "performance" in log_data:
                            exec_time = log_data["performance"].get("execution_time_ms", 0)
                            execution_times.append(exec_time)
                        
                        if "agent_chosen" in log_data:
                            agent = log_data["agent_chosen"]
                            metrics["agent_distribution"][agent] = metrics["agent_distribution"].get(agent, 0) + 1
                        
                        if "routing" in log_data and "confidence" in log_data["routing"]:
                            confidence = log_data["routing"]["confidence"]
                            if confidence < 0.7:
                                errors += 1
                        
                    except Exception:
                        continue
                
                # Calcula métricas finais
                if execution_times:
                    metrics["avg_execution_time"] = sum(execution_times) / len(execution_times)
                
                metrics["error_rate"] = errors / len(result.data) if result.data else 0
            
            return metrics
            
        except Exception as e:
            print(f"Erro ao recuperar métricas: {e}")
            return {}

# Instância global do gerenciador de memória
memory_manager = MemoryManager()
