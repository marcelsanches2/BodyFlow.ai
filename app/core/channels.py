"""
Configuração de canais de comunicação
Permite alternar entre WhatsApp e Telegram mantendo a mesma lógica
"""

import os
from enum import Enum

class ChannelType(Enum):
    """Tipos de canais suportados"""
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"

class ChannelConfig:
    """Configuração dos canais de comunicação"""
    
    # Canal ativo (pode ser alterado via variável de ambiente)
    ACTIVE_CHANNEL = ChannelType(os.getenv("ACTIVE_CHANNEL", "telegram"))
    
    # Configurações do WhatsApp
    WHATSAPP_CONFIG = {
        "webhook_path": "/whatsapp/",
        "status_callback_path": "/whatsapp/status-callback",
        "phone_prefix": "whatsapp:",
        "message_format": "twiml"
    }
    
    # Configurações do Telegram
    TELEGRAM_CONFIG = {
        "webhook_path": "/telegram/",
        "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
        "webhook_url": os.getenv("TELEGRAM_WEBHOOK_URL", ""),
        "message_format": "json"
    }
    
    @classmethod
    def get_active_config(cls):
        """Retorna a configuração do canal ativo"""
        if cls.ACTIVE_CHANNEL == ChannelType.WHATSAPP:
            return cls.WHATSAPP_CONFIG
        elif cls.ACTIVE_CHANNEL == ChannelType.TELEGRAM:
            return cls.TELEGRAM_CONFIG
        else:
            raise ValueError(f"Canal não suportado: {cls.ACTIVE_CHANNEL}")
    
    @classmethod
    def is_whatsapp_active(cls):
        """Verifica se o WhatsApp está ativo"""
        return cls.ACTIVE_CHANNEL == ChannelType.WHATSAPP
    
    @classmethod
    def is_telegram_active(cls):
        """Verifica se o Telegram está ativo"""
        return cls.ACTIVE_CHANNEL == ChannelType.TELEGRAM
