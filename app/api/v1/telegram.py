"""
Endpoints do Telegram para o BodyFlow Backend
Mantém a mesma lógica do WhatsApp, apenas adaptando para o formato do Telegram
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import logging
import sys
import os
import httpx
import json

# Ajusta o sys.path para permitir imports relativos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.memory import memory_manager
from app.services.phone_validation import phone_validation_service
from app.adk.main_graph import bodyflow_graph
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
    
    async def get_file_info(self, file_id: str) -> Optional[dict]:
        """
        Obtém informações do arquivo do Telegram
        """
        try:
            url = f"{self.api_url}/getFile"
            data = {"file_id": file_id}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data)
                
                if response.status_code == 200:
                    return response.json().get("result")
                else:
                    logger.error(f"❌ Erro ao obter info do arquivo: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erro ao obter info do arquivo: {e}")
            return None
    
    async def download_file(self, file_path: str) -> Optional[bytes]:
        """
        Baixa arquivo do Telegram
        """
        try:
            url = f"https://api.telegram.org/file/bot{self.bot_token}/{file_path}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    return response.content
                else:
                    logger.error(f"❌ Erro ao baixar arquivo: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erro ao baixar arquivo: {e}")
            return None
    
    async def send_contact_request(self, chat_id: str, text: str) -> bool:
        """
        Envia mensagem com botão para compartilhar contato
        """
        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
                "reply_markup": {
                    "keyboard": [[{
                        "text": "📱 Compartilhar meu número",
                        "request_contact": True
                    }]],
                    "resize_keyboard": True,
                    "one_time_keyboard": True
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data)
                
                if response.status_code == 200:
                    logger.info(f"✅ Botão de contato enviado para Telegram: {chat_id}")
                    return True
                else:
                    logger.error(f"❌ Erro ao enviar botão de contato: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erro ao enviar botão de contato: {e}")
            return False
    
    async def get_user_phone(self, user_id: str) -> Optional[str]:
        """
        Busca o número de telefone do usuário na API do Telegram
        """
        try:
            # Tenta buscar informações do usuário na API do Telegram
            url = f"{self.api_url}/getChat"
            data = {"chat_id": user_id}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data)
                
            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    chat_info = result.get("result", {})
                    # Verifica se tem número de telefone
                    phone_number = chat_info.get("phone_number")
                    if phone_number:
                        logger.info(f"📞 Telefone encontrado na API do Telegram: {phone_number}")
                        return phone_number
                    else:
                        logger.warning(f"⚠️ Usuário Telegram {user_id} não tem número de telefone público")
                        return None
                else:
                    logger.warning(f"⚠️ Erro na API do Telegram: {result.get('description')}")
                    return None
            else:
                logger.warning(f"⚠️ Erro HTTP ao buscar usuário: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar telefone do usuário: {e}")
            return None
    
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
        contact = message.get("contact")
        user_info = message.get("from", {})
        user_id = str(user_info.get("id", ""))
        username = user_info.get("username", "")
        first_name = user_info.get("first_name", "")
        
        if not chat_id:
            logger.warning("⚠️ Chat ID não encontrado")
            return {"status": "ok"}
        
        # Verifica se há foto/imagem na mensagem
        photo = message.get("photo")
        document = message.get("document")
        
        # Se não tem texto, contato nem imagem, ignora
        if not message_text and not contact and not photo and not document:
            logger.warning("⚠️ Mensagem sem texto, contato nem imagem")
            return {"status": "ok"}
        
        logger.info(f"📱 Processando mensagem do Telegram - Chat: {chat_id}, Usuário: {username or first_name}, Mensagem: {message_text}")
        
        # Verifica se o usuário compartilhou contato
        telegram_bot = TelegramBot(Config.TELEGRAM_BOT_TOKEN)
        
        # Verifica se é um contato compartilhado
        if contact:
            phone_number = contact.get("phone_number")
            first_name = contact.get("first_name", "")
            last_name = contact.get("last_name", "")
            user_id_contact = contact.get("user_id", "")
            
            logger.info(f"📞 Contato compartilhado pelo usuário")
            
            if not phone_number:
                logger.warning("⚠️ Número de telefone não encontrado no contato")
                await telegram_bot.send_message(chat_id, """❌ **Erro na Autenticação**

Não foi possível obter seu número de telefone. Isso pode acontecer se:

• Você não clicou no botão "Compartilhar meu número"
• Seu número não está público no Telegram
• Houve um problema técnico

🔄 **Tente novamente:**
1. Use o botão "📱 Compartilhar meu número"
2. Confirme o compartilhamento
3. Aguarde a verificação

Se o problema persistir, entre em contato conosco.""")
                return {"status": "ok"}
            
            # Valida o telefone usando o serviço de validação
            user_info = {
                "first_name": first_name,
                "last_name": last_name,
                "user_id": user_id_contact,
                "chat_id": chat_id
            }
            
            validation_result = await phone_validation_service.validate_phone_from_contact(phone_number, user_info)
            
            if not validation_result["valid"]:
                # Usuário não cadastrado
                await telegram_bot.send_message(chat_id, """🎉 **Bem-vindo ao BodyFlow.ai!**

Sou seu assistente pessoal de fitness e nutrição. Vou te ajudar a criar um plano personalizado para alcançar seus objetivos!

Para começar, você precisa se cadastrar primeiro no nosso site. 

📱 **Acesse:** [bodyflow.ai](https://bodyflow.ai) para criar sua conta

Após o cadastro, volte aqui e eu te ajudarei a completar seu perfil personalizado com:
• Sua idade, peso e altura
• Seus objetivos de fitness
• Seu nível de treino atual
• Suas restrições alimentares

Depois disso, poderei criar planos de treino e dieta totalmente personalizados para você!

🔗 **Cadastre-se em:** bodyflow.ai""")
                return {"status": "ok"}
        else:
            # Se não é contato, verifica se já foi validado antes
            # Primeiro, verifica se o chat_id já tem validação no banco
            is_validated = await phone_validation_service.is_chat_validated(chat_id)
            
            if is_validated:
                # Chat já validado, processa mensagem normalmente
                logger.info(f"✅ Chat {chat_id} já validado, processando mensagem normalmente")
                phone_number = await phone_validation_service.get_phone_by_chat_id(chat_id)
                if phone_number:
                    # Atualiza último uso
                    await phone_validation_service.update_last_used(phone_number)
                else:
                    logger.warning(f"⚠️ Chat {chat_id} validado mas telefone não encontrado")
                    await telegram_bot.send_message(chat_id, "Erro interno. Tente novamente.")
                    return {"status": "ok"}
            else:
                # Chat não validado, verifica se a mensagem é um telefone
                potential_phone = message_text if message_text and message_text.replace("+", "").replace(" ", "").replace("(", "").replace(")", "").replace("-", "").isdigit() else None
                
                if potential_phone:
                    # Se a mensagem parece ser um telefone, valida
                    user_info = {
                        "first_name": first_name,
                        "last_name": "",
                        "user_id": user_id,
                        "chat_id": chat_id
                    }
                    
                    validation_result = await phone_validation_service.validate_phone_from_contact(potential_phone, user_info)
                    
                    if validation_result["valid"]:
                        # Usuário validado, processa mensagem normalmente
                        phone_number = validation_result["normalized_phone"]
                    else:
                        # Usuário não cadastrado
                        await telegram_bot.send_message(chat_id, """🎉 **Bem-vindo ao BodyFlow.ai!**

Sou seu assistente pessoal de fitness e nutrição. Vou te ajudar a criar um plano personalizado para alcançar seus objetivos!

Para começar, você precisa se cadastrar primeiro no nosso site. 

📱 **Acesse:** [bodyflow.ai](https://bodyflow.ai) para criar sua conta

Após o cadastro, volte aqui e eu te ajudarei a completar seu perfil personalizado com:
• Sua idade, peso e altura
• Seus objetivos de fitness
• Seu nível de treino atual
• Suas restrições alimentares

Depois disso, poderei criar planos de treino e dieta totalmente personalizados para você!

🔗 **Cadastre-se em:** bodyflow.ai""")
                        return {"status": "ok"}
                else:
                    # Se não é contato nem telefone, pede para compartilhar
                    await telegram_bot.send_contact_request(chat_id, """🔐 **Autenticação Segura BodyFlow**

Olá! Para garantir sua segurança e acesso exclusivo aos seus dados pessoais de treino e dieta, preciso verificar sua identidade.

📱 **Por que preciso do seu número?**
• Verificar se você é um usuário cadastrado no BodyFlow
• Garantir que apenas você tenha acesso aos seus dados
• Proteger sua privacidade e informações pessoais

✅ **Seu número está seguro**
• Não compartilhamos com terceiros
• Usado apenas para autenticação
• Criptografado e protegido

Use o botão abaixo para compartilhar seu número de forma segura:""")
                    return {"status": "ok"}
            
            # Se chegou até aqui, significa que o usuário foi validado e tem telefone
            # Processa mensagem normalmente
        
        # Processa mensagem através do grafo ADK
        try:
            # Determina tipo de conteúdo
            content_type = "text"
            image_data = None
            
            # Verifica se há imagem
            if photo:
                content_type = "image"
                # Usa a foto de maior resolução (última da lista)
                largest_photo = photo[-1]
                file_id = largest_photo.get("file_id")
                
                if file_id:
                    logger.info(f"📸 Processando imagem do Telegram - File ID: {file_id}")
                    
                    # Obtém informações do arquivo
                    file_info = await telegram_bot.get_file_info(file_id)
                    if file_info and file_info.get("file_path"):
                        # Baixa a imagem
                        image_data = await telegram_bot.download_file(file_info["file_path"])
                        if image_data:
                            logger.info(f"✅ Imagem baixada com sucesso - Tamanho: {len(image_data)} bytes")
                        else:
                            logger.error("❌ Falha ao baixar imagem")
                            image_data = None
                    else:
                        logger.error("❌ Falha ao obter informações do arquivo")
                        image_data = None
                        
            elif document:
                # Verifica se é uma imagem enviada como documento
                mime_type = document.get("mime_type", "")
                if mime_type.startswith("image/"):
                    content_type = "image"
                    file_id = document.get("file_id")
                    
                    if file_id:
                        logger.info(f"📄 Processando documento de imagem - File ID: {file_id}")
                        
                        # Obtém informações do arquivo
                        file_info = await telegram_bot.get_file_info(file_id)
                        if file_info and file_info.get("file_path"):
                            # Baixa a imagem
                            image_data = await telegram_bot.download_file(file_info["file_path"])
                            if image_data:
                                logger.info(f"✅ Imagem (documento) baixada com sucesso - Tamanho: {len(image_data)} bytes")
                            else:
                                logger.error("❌ Falha ao baixar imagem (documento)")
                                image_data = None
                        else:
                            logger.error("❌ Falha ao obter informações do arquivo (documento)")
                            image_data = None
            
            # Busca customer_id pelo telefone validado
            customer_result = memory_manager.supabase.table("customers").select("id").eq("whatsapp", phone_number).execute()
            if customer_result.data:
                user_identifier = customer_result.data[0]["id"]  # Usa customer_id (UUID)
            else:
                user_identifier = phone_number  # Fallback para telefone
            
            # Define conteúdo baseado no tipo de mensagem
            if contact:
                content_to_process = "Contato compartilhado - verificar acesso"
            elif image_data or photo or document:
                # Se há texto junto com a imagem, usa o texto do usuário
                if message_text and message_text.strip():
                    content_to_process = message_text
                else:
                    content_to_process = "Análise de imagem enviada"
            else:
                content_to_process = message_text
            
            logger.info(f"🔍 Processando mensagem:")
            logger.info(f"   📝 Conteúdo: {content_to_process}")
            
            # Processa através do grafo ADK
            logger.info(f"🚀 Enviando para processamento no grafo ADK...")
            graph_result = await bodyflow_graph.process_message(
                user_id=user_identifier,
                content=content_to_process,
                channel="telegram",
                content_type=content_type,
                image_data=image_data
            )
            
            logger.info(f"📤 Resultado do grafo ADK:")
            logger.info(f"   ✅ Sucesso: {graph_result.get('success', False)}")
            logger.info(f"   🤖 Agente ativado: {graph_result.get('agent_activated', 'N/A')}")
            logger.info(f"   📝 Resposta: {graph_result.get('response', 'N/A')[:100]}...")
            
            if graph_result.get("success"):
                resposta = graph_result.get("response", "Resposta não disponível")
            else:
                resposta = graph_result.get("response", "Erro interno do sistema")
                
        except Exception as e:
            logger.error(f"Erro no processamento ADK: {e}")
            resposta = "Erro interno do sistema. Tente novamente."
        
        # Limpa a mensagem para o Telegram
        resposta_limpa = _clean_message_for_telegram(resposta)
        
        # Salva no histórico usando o número de telefone correto
        await memory_manager.save_message(phone_number, message_text, "inbound")
        await memory_manager.save_message(phone_number, resposta_limpa, "outbound")
        
        # Envia resposta via Telegram Bot API
        if telegram_bot:
            logger.info(f"📤 Enviando mensagem para Telegram:")
            logger.info(f"   📝 Mensagem: {resposta_limpa[:200]}...")
            await telegram_bot.send_message(chat_id, resposta_limpa)
            logger.info(f"✅ Mensagem enviada para Telegram: {chat_id}")
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
