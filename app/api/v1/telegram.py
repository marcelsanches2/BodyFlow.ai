"""
Endpoints do Telegram para o BodyFlow Backend
Mantém a mesma lógica do WhatsApp, apenas adaptando para o formato do Telegram
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import logging
import sys
import os
import httpx
import json

# Ajusta o sys.path para permitir imports relativos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.graph import bodyflow_graph
from app.services.memory import memory_manager
from app.utils.messages import UserMessages
from app.core.config import Config
from app.core.channels import ChannelConfig

logger = logging.getLogger(__name__)
telegram_router = APIRouter(prefix="/telegram", tags=["Telegram"])

class TelegramBot:
    """Classe para gerenciar interações com o Telegram Bot API"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
    
    async def send_message(self, chat_id: str, text: str) -> bool:
        """
        Envia mensagem para o Telegram
        """
        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data)
                
                if response.status_code == 200:
                    logger.info(f"✅ Mensagem enviada para Telegram: {chat_id}")
                    return True
                else:
                    logger.error(f"❌ Erro ao enviar mensagem para Telegram: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mensagem para Telegram: {e}")
            return False
    
    async def set_webhook(self, webhook_url: str) -> bool:
        """
        Configura o webhook do Telegram
        """
        try:
            url = f"{self.api_url}/setWebhook"
            data = {"url": webhook_url}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("ok"):
                        logger.info(f"✅ Webhook do Telegram configurado: {webhook_url}")
                        return True
                    else:
                        logger.error(f"❌ Erro ao configurar webhook: {result.get('description')}")
                        return False
                else:
                    logger.error(f"❌ Erro HTTP ao configurar webhook: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erro ao configurar webhook do Telegram: {e}")
            return False

# Instância do bot (será inicializada com o token)
telegram_bot = None

def _clean_message_for_telegram(message: str) -> str:
    """
    Limpa mensagem para compatibilidade com Telegram
    """
    if not message:
        return ""
    
    # Remove caracteres problemáticos
    cleaned = str(message).strip()
    
    # Substitui caracteres especiais por versões simples
    replacements = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
        'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c', 'ñ': 'n',
        'Á': 'A', 'À': 'A', 'Ã': 'A', 'Â': 'A', 'Ä': 'A',
        'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
        'Í': 'I', 'Ì': 'I', 'Î': 'I', 'Ï': 'I',
        'Ó': 'O', 'Ò': 'O', 'Õ': 'O', 'Ô': 'O', 'Ö': 'O',
        'Ú': 'U', 'Ù': 'U', 'Û': 'U', 'Ü': 'U',
        'Ç': 'C', 'Ñ': 'N',
        '"': '"', '"': '"',
        ''': "'", ''': "'",
        '–': '-', '—': '-',
        '…': '...'
    }
    
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    
    # Remove caracteres de controle
    cleaned = ''.join(char for char in cleaned if ord(char) >= 32 or char in '\n\r\t')
    
    return cleaned

@telegram_router.get("/")
async def telegram_status():
    """
    Endpoint de status do Telegram
    """
    return {"status": "ok", "channel": "telegram", "active": ChannelConfig.is_telegram_active()}

@telegram_router.post("/")
async def telegram_webhook(request: Request):
    """
    Webhook principal do Telegram
    Recebe mensagens do Telegram e processa com a mesma lógica do WhatsApp
    """
    try:
        # Lê o JSON do Telegram
        body = await request.json()
        logger.info(f"📱 Mensagem recebida do Telegram: {json.dumps(body, indent=2)}")
        
        # Extrai informações da mensagem
        message = body.get("message", {})
        if not message:
            logger.warning("⚠️ Mensagem vazia recebida do Telegram")
            return {"status": "ok"}
        
        chat_id = str(message.get("chat", {}).get("id", ""))
        message_text = message.get("text", "")
        user_info = message.get("from", {})
        user_id = str(user_info.get("id", ""))
        username = user_info.get("username", "")
        first_name = user_info.get("first_name", "")
        
        if not chat_id or not message_text:
            logger.warning("⚠️ Chat ID ou texto da mensagem não encontrado")
            return {"status": "ok"}
        
        logger.info(f"📱 Processando mensagem do Telegram - Chat: {chat_id}, Usuário: {username or first_name}, Mensagem: {message_text}")
        
        # Verifica se o usuário está cadastrado e ativo
        user = await memory_manager.get_user_by_phone(chat_id)  # Usa chat_id como identificador
        
        if not user:
            # Usuário não cadastrado - oferece cadastro
            resposta = UserMessages.WELCOME_NOT_REGISTERED
        elif not user.get("is_active"):
            # Usuário cadastrado mas não ativo - apenas informa
            resposta = UserMessages.ACCOUNT_INACTIVE
        else:
            # Usuário ativo - processa normalmente
            
            # Checa histórico ANTES de registrar a mensagem atual
            historico_antes = await memory_manager.get_user_history(chat_id, limit=1)
            
            # Processa a mensagem com o grafo de agentes
            resposta = await bodyflow_graph.processar_mensagem(chat_id, message_text)
            
            # Saúda o usuário no primeiro contato (sem histórico prévio)
            if not historico_antes:
                saudacao = UserMessages.FIRST_CONTACT_GREETING
                resposta = f"{saudacao}\n\n{resposta}"
        
        # Limpa a mensagem para o Telegram
        resposta_limpa = _clean_message_for_telegram(resposta)
        
        # Salva no histórico
        await memory_manager.save_message(chat_id, message_text, "inbound")
        await memory_manager.save_message(chat_id, resposta_limpa, "outbound")
        
        # Envia resposta via Telegram Bot API
        if telegram_bot:
            await telegram_bot.send_message(chat_id, resposta_limpa)
        else:
            logger.error("❌ Bot do Telegram não inicializado")
            # Em modo de teste, apenas loga a resposta
            logger.info(f"📱 Resposta que seria enviada: {resposta_limpa}")
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"❌ Erro no webhook do Telegram: {e}")
        return {"status": "error", "message": str(e)}

@telegram_router.post("/setup-webhook")
async def setup_telegram_webhook(webhook_url: str = None):
    """
    Configura o webhook do Telegram
    """
    try:
        if not telegram_bot:
            return {"status": "error", "message": "Bot do Telegram não inicializado"}
        
        # Usa a URL fornecida ou a URL padrão da configuração
        url = webhook_url or ChannelConfig.TELEGRAM_CONFIG.get("webhook_url")
        if not url:
            return {"status": "error", "message": "URL do webhook não fornecida"}
        
        success = await telegram_bot.set_webhook(url)
        
        if success:
            return {"status": "success", "message": f"Webhook configurado: {url}"}
        else:
            return {"status": "error", "message": "Falha ao configurar webhook"}
            
    except Exception as e:
        logger.error(f"❌ Erro ao configurar webhook: {e}")
        return {"status": "error", "message": str(e)}

@telegram_router.get("/webhook-info")
async def get_webhook_info():
    """
    Obtém informações sobre o webhook atual do Telegram
    """
    try:
        if not telegram_bot:
            return {"status": "error", "message": "Bot do Telegram não inicializado"}
        
        url = f"{telegram_bot.api_url}/getWebhookInfo"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "message": f"Erro HTTP: {response.status_code}"}
                
    except Exception as e:
        logger.error(f"❌ Erro ao obter informações do webhook: {e}")
        return {"status": "error", "message": str(e)}

# Função para inicializar o bot do Telegram
def init_telegram_bot():
    """
    Inicializa o bot do Telegram com o token da configuração
    """
    global telegram_bot
    
    bot_token = ChannelConfig.TELEGRAM_CONFIG.get("bot_token")
    if bot_token:
        telegram_bot = TelegramBot(bot_token)
        logger.info("✅ Bot do Telegram inicializado")
    else:
        logger.warning("⚠️ Token do Telegram não configurado")

# Inicializa o bot na importação do módulo
init_telegram_bot()
