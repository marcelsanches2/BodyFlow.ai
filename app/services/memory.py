from supabase import create_client, Client
from typing import List, Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from app.core.config import Config
import json
from datetime import datetime

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
            
            result = self.supabase.table("messages").insert(data).execute()
            return len(result.data) > 0
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
            result = self.supabase.table("messages")\
                .select("*")\
                .eq("phone", phone)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data
        except Exception as e:
            print(f"Erro ao buscar histórico: {e}")
            return []
    


    def _normalize_phone_for_search(self, phone: str) -> str:
        """
        Normaliza o número de telefone para busca no banco
        Converte whatsapp:+5511940751013 para (11) 94075-1013
        """
        # Remove prefixo whatsapp:
        clean_phone = phone.replace("whatsapp:", "") if phone.startswith("whatsapp:") else phone
        
        # Se já está no formato correto, retorna
        if clean_phone.startswith("(") and ")" in clean_phone:
            return clean_phone
        
        # Converte +5511940751013 para (11) 94075-1013
        if clean_phone.startswith("+55"):
            # Remove +55
            number = clean_phone[3:]
            if len(number) >= 11:
                # +5511940751013 -> (11) 94075-1013
                ddd = number[:2]
                first_part = number[2:7]
                second_part = number[7:]
                return f"({ddd}) {first_part}-{second_part}"
        
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
            
            result = self.supabase.table("customers")\
                .select("*")\
                .eq("whatsapp", normalized_phone)\
                .execute()
            
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            print(f"Erro ao buscar usuário: {e}")
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

# Instância global do gerenciador de memória
memory_manager = MemoryManager()
