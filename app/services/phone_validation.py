"""
Serviço de Validação de Telefone
Responsável por validar e cachear números de telefone do Telegram/WhatsApp
"""

import asyncio
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta, timezone
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.memory import memory_manager
from app.core.config import Config

class PhoneValidationService:
    """Serviço para validação e persistência de números de telefone"""
    
    def __init__(self):
        self.validation_duration_hours = 720  # Validação válida por 30 dias (720 horas)
    
    async def validate_phone_from_contact(self, phone_number: str, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida número de telefone compartilhado via contato
        
        Args:
            phone_number: Número do telefone compartilhado
            user_info: Informações do usuário (nome, etc.)
        
        Returns:
            Dict com resultado da validação
        """
        try:
            # Normaliza o número
            normalized_phone = memory_manager._normalize_phone_for_search(phone_number)
            
            # Busca usuário no banco
            user = await memory_manager.get_user_by_phone(normalized_phone)
            
            if user:
                # Usuário encontrado - validação bem-sucedida
                print(f"   ✅ Usuário encontrado: {user.get('name', 'N/A')}")
                
                # Atualiza campos de validação na tabela customers
                await self._update_phone_validation(user['id'], user_info)
                
                return {
                    "valid": True,
                    "user": user,
                    "normalized_phone": normalized_phone,
                    "message": "Usuário validado com sucesso"
                }
            else:
                # Usuário não encontrado
                print(f"   ❌ Usuário não encontrado no banco")
                return {
                    "valid": False,
                    "user": None,
                    "normalized_phone": normalized_phone,
                    "message": "Usuário não cadastrado no sistema"
                }
                
        except Exception as e:
            print(f"❌ Erro na validação: {e}")
            return {
                "valid": False,
                "user": None,
                "normalized_phone": None,
                "message": f"Erro na validação: {str(e)}"
            }
    
    async def is_phone_validated(self, phone_number: str) -> bool:
        """
        Verifica se o telefone já foi validado recentemente
        
        Args:
            phone_number: Número do telefone
        
        Returns:
            bool: True se já foi validado recentemente
        """
        try:
            normalized_phone = memory_manager._normalize_phone_for_search(phone_number)
            
            # Busca usuário no banco
            user = await memory_manager.get_user_by_phone(normalized_phone)
            
            if user and user.get('phone_validated_at'):
                # Verifica se a validação ainda é válida
                validated_at = datetime.fromisoformat(user['phone_validated_at'].replace('Z', '+00:00'))
                validation_threshold = datetime.now(validated_at.tzinfo) - timedelta(hours=self.validation_duration_hours)
                
                if validated_at > validation_threshold:
                    print(f"✅ Telefone {normalized_phone} já validado recentemente")
                    return True
            
            print(f"❌ Telefone {normalized_phone} não validado ou expirado")
            return False
            
        except Exception as e:
            print(f"❌ Erro ao verificar validação: {e}")
            return False
    
    async def get_validated_user(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        Recupera dados do usuário validado
        
        Args:
            phone_number: Número do telefone
        
        Returns:
            Dict com dados do usuário ou None
        """
        try:
            normalized_phone = memory_manager._normalize_phone_for_search(phone_number)
            
            # Busca usuário no banco
            user = await memory_manager.get_user_by_phone(normalized_phone)
            
            if user and user.get('phone_validated_at'):
                # Verifica se a validação ainda é válida
                validated_at = datetime.fromisoformat(user['phone_validated_at'].replace('Z', '+00:00'))
                validation_threshold = datetime.now(validated_at.tzinfo) - timedelta(hours=self.validation_duration_hours)
                
                if validated_at > validation_threshold:
                    return user
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao recuperar usuário: {e}")
            return None
    
    async def _update_phone_validation(self, customer_id: str, user_info: Dict[str, Any]) -> None:
        """
        Atualiza campos de validação na tabela customers
        
        Args:
            customer_id: ID do cliente
            user_info: Informações do usuário do Telegram/WhatsApp
        """
        try:
            update_data = {
                "phone_validated_at": datetime.now().isoformat(),
                "phone_last_used_at": datetime.now().isoformat(),
                "phone_validation_source": "telegram",  # ou "whatsapp"
                "telegram_chat_id": user_info.get("chat_id"),
                "telegram_user_id": user_info.get("user_id")
            }
            
            result = memory_manager.supabase.table("customers")\
                .update(update_data)\
                .eq("id", customer_id)\
                .execute()
            
            if result.data:
                print(f"💾 Validação atualizada no banco para cliente: {customer_id}")
            else:
                print(f"❌ Erro ao atualizar validação para cliente: {customer_id}")
            
        except Exception as e:
            print(f"❌ Erro ao atualizar validação: {e}")
    
    async def is_chat_validated(self, chat_id: str) -> bool:
        """
        Verifica se o chat_id já foi validado recentemente
        
        Args:
            chat_id: ID do chat do Telegram
        
        Returns:
            bool: True se já foi validado recentemente
        """
        try:
            # Busca usuário pelo telegram_chat_id
            result = memory_manager.supabase.table("customers")\
                .select("phone_validated_at")\
                .eq("telegram_chat_id", chat_id)\
                .not_.is_("phone_validated_at", "null")\
                .execute()
            
            if result.data:
                user = result.data[0]
                if user.get('phone_validated_at'):
                    # Verifica se a validação ainda é válida
                    validated_at_str = user['phone_validated_at']
                    if validated_at_str.endswith('Z'):
                        validated_at_str = validated_at_str[:-1] + '+00:00'
                    validated_at = datetime.fromisoformat(validated_at_str)
                    validation_threshold = datetime.now(timezone.utc) - timedelta(hours=self.validation_duration_hours)
                    
                    if validated_at > validation_threshold:
                        print(f"✅ Chat {chat_id} já validado recentemente")
                        return True
            
            print(f"❌ Chat {chat_id} não validado ou expirado")
            return False
            
        except Exception as e:
            print(f"❌ Erro ao verificar validação do chat: {e}")
            return False
    
    async def get_phone_by_chat_id(self, chat_id: str) -> Optional[str]:
        """
        Recupera o telefone associado ao chat_id
        
        Args:
            chat_id: ID do chat do Telegram
        
        Returns:
            str: Número de telefone normalizado ou None
        """
        try:
            result = memory_manager.supabase.table("customers")\
                .select("whatsapp, phone_validated_at")\
                .eq("telegram_chat_id", chat_id)\
                .not_.is_("phone_validated_at", "null")\
                .execute()
            
            if result.data:
                user = result.data[0]
                if user.get('phone_validated_at'):
                    # Verifica se a validação ainda é válida
                    validated_at_str = user['phone_validated_at']
                    if validated_at_str.endswith('Z'):
                        validated_at_str = validated_at_str[:-1] + '+00:00'
                    validated_at = datetime.fromisoformat(validated_at_str)
                    validation_threshold = datetime.now(timezone.utc) - timedelta(hours=self.validation_duration_hours)
                    
                    if validated_at > validation_threshold:
                        phone = user.get('whatsapp')
                        return phone
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao recuperar telefone por chat_id: {e}")
            return None
    
    async def update_last_used(self, phone_number: str) -> None:
        """
        Atualiza timestamp de último uso do telefone
        
        Args:
            phone_number: Número do telefone
        """
        try:
            normalized_phone = memory_manager._normalize_phone_for_search(phone_number)
            
            update_data = {
                "phone_last_used_at": datetime.now().isoformat()
            }
            
            result = memory_manager.supabase.table("customers")\
                .update(update_data)\
                .eq("whatsapp", normalized_phone)\
                .execute()
            
            if result.data:
                pass  # Atualização realizada
            
        except Exception as e:
            print(f"❌ Erro ao atualizar último uso: {e}")

# Instância global do serviço
phone_validation_service = PhoneValidationService()
