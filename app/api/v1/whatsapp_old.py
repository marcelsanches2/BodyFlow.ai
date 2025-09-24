from fastapi import APIRouter, Request, Form, HTTPException
from twilio.twiml.messaging_response import MessagingResponse
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from app.graph import bodyflow_graph
from app.services.memory import memory_manager
from app.utils.messages import UserMessages
from app.core.config import Config
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Router para endpoints do WhatsApp
whatsapp_router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

@whatsapp_router.post("/")
async def webhook_whatsapp(request: Request):
    """
    Webhook para receber mensagens do Twilio WhatsApp
    
    Este endpoint recebe mensagens do Twilio e responde usando o grafo de agentes
    Verifica se o usuário está cadastrado e ativo antes de processar
    """
    try:
        # Extrai dados do formulário Twilio
        form_data = await request.form()
        
        # Dados da mensagem
        from_number = form_data.get("From", "")
        message_body = form_data.get("Body", "")
        message_sid = form_data.get("MessageSid", "")
        
        logger.info(f"Mensagem recebida de {from_number}: {message_body}")
        
        # Valida se tem dados essenciais
        if not from_number or not message_body:
            logger.error("Dados da mensagem incompletos")
            return _create_error_response("Dados da mensagem incompletos")
        
        # Verifica se o usuário está cadastrado e ativo
        logger.info(f"Buscando usuário com telefone: {from_number}")
        user = await memory_manager.get_user_by_phone(from_number)
        logger.info(f"Usuário encontrado: {user is not None}")
        if user:
            logger.info(f"Usuário ativo: {user.get('is_active')}")
        
        if not user:
            # Usuário não cadastrado - oferece cadastro
            resposta = _clean_message_for_whatsapp(UserMessages.WELCOME_NOT_REGISTERED)
            
            await memory_manager.save_message(from_number, message_body, "inbound")
            await memory_manager.save_message(from_number, resposta, "outbound")
            
            twiml_response = MessagingResponse()
            twiml_response.message(resposta)
            return _create_twiml_response(str(twiml_response))
        
        elif not user.get("is_active"):
            # Usuário cadastrado mas não ativo - apenas informa
            resposta = _clean_message_for_whatsapp(UserMessages.ACCOUNT_INACTIVE)
            
            await memory_manager.save_message(from_number, message_body, "inbound")
            await memory_manager.save_message(from_number, resposta, "outbound")
            
            twiml_response = MessagingResponse()
            twiml_response.message(resposta)
            return _create_twiml_response(str(twiml_response))
        
        # Usuário ativo - processa normalmente

        # Checa histórico ANTES de registrar a mensagem atual
        historico_antes = await memory_manager.get_user_history(from_number, limit=1)

        resposta = await bodyflow_graph.processar_mensagem(from_number, message_body)

        # Saúda o usuário no primeiro contato (sem histórico prévio)
        if not historico_antes:
            saudacao = UserMessages.FIRST_CONTACT_GREETING
            resposta = f"{saudacao}\n\n{resposta}"

        # Limpa a resposta para compatibilidade com WhatsApp
        resposta_limpa = _clean_message_for_whatsapp(resposta)

        # Registra mensagem recebida e enviada
        await memory_manager.save_message(from_number, message_body, "inbound")
        await memory_manager.save_message(from_number, resposta_limpa, "outbound")
        
        logger.info(f"Resposta enviada para {from_number}: {resposta_limpa[:100]}...")
        
        # Cria resposta TwiML
        twiml_response = MessagingResponse()
        twiml_response.message(resposta_limpa)
        
        return _create_twiml_response(str(twiml_response))
        
    except Exception as e:
        logger.error(f"Erro no webhook WhatsApp: {e}")
        return _create_error_response("Erro interno do servidor")

@whatsapp_router.get("/status")
async def status_webhook():
    """
    Endpoint para verificar status do webhook
    """
    return {
        "status": "active",
        "service": "BodyFlow WhatsApp Bot",
        "version": "1.0.0"
    }

@whatsapp_router.post("/status-callback")
async def status_callback(request: Request):
    """
    Endpoint para receber status callbacks do Twilio
    """
    try:
        form_data = await request.form()
        
        # Log do status callback
        logger.info("📊 Status Callback recebido:")
        logger.info(f"MessageSid: {form_data.get('MessageSid', 'N/A')}")
        logger.info(f"MessageStatus: {form_data.get('MessageStatus', 'N/A')}")
        logger.info(f"To: {form_data.get('To', 'N/A')}")
        logger.info(f"From: {form_data.get('From', 'N/A')}")
        logger.info(f"ErrorCode: {form_data.get('ErrorCode', 'N/A')}")
        logger.info(f"ErrorMessage: {form_data.get('ErrorMessage', 'N/A')}")
        
        # Salva o status no banco para análise
        await memory_manager.save_message(
            phone=form_data.get('To', 'unknown'),
            body=f"STATUS: {form_data.get('MessageStatus', 'unknown')} - {form_data.get('ErrorMessage', '')}",
            direction="inbound"  # Usa valor válido para a constraint
        )
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Erro no status callback: {e}")
        return {"status": "error", "message": str(e)}

@whatsapp_router.post("/test-ultra-simple")
async def test_ultra_simple_webhook(request: Request):
    """
    Endpoint ultra simples para teste - apenas "Hi"
    """
    try:
        form_data = await request.form()
        from_number = form_data.get("From", "")
        message_body = form_data.get("Body", "")
        
        logger.info(f"Teste ultra simples - De: {from_number}, Mensagem: {message_body}")
        
        # TwiML ultra simples - apenas "Hi"
        twiml_response = MessagingResponse()
        twiml_response.message("Hi")
        
        return _create_twiml_response(str(twiml_response))
        
    except Exception as e:
        logger.error(f"Erro no teste ultra simples: {e}")
        # Retorna TwiML de erro ultra simples
        twiml_response = MessagingResponse()
        twiml_response.message("Hi")
        return _create_twiml_response(str(twiml_response))

@whatsapp_router.get("/debug-user/{phone}")
async def debug_user(phone: str):
    """
    Endpoint para debugar busca de usuário
    """
    try:
        user = await memory_manager.get_user_by_phone(phone)
        return {
            "phone": phone,
            "user_found": user is not None,
            "user_data": user,
            "is_active": user.get("is_active") if user else None
        }
    except Exception as e:
        return {
            "error": str(e),
            "phone": phone
        }

@whatsapp_router.post("/test-webhook-logic")
async def test_webhook_logic(
    phone: str = Form(...),
    message: str = Form(...)
):
    """
    Endpoint para testar a lógica do webhook
    """
    try:
        logger.info(f"Teste de lógica - Mensagem de {phone}: {message}")
        
        # Verifica se o usuário está cadastrado e ativo
        user = await memory_manager.get_user_by_phone(phone)
        
        if not user:
            resposta = "Usuário não cadastrado"
        elif not user.get("is_active"):
            resposta = "Usuário inativo"
        else:
            resposta = "Usuário ativo - processando mensagem"
        
        return {
            "success": True,
            "phone": phone,
            "message": message,
            "response": resposta,
            "user_found": user is not None,
            "user_active": user.get("is_active") if user else None
        }
        
    except Exception as e:
        logger.error(f"Erro no teste de lógica: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@whatsapp_router.post("/test")
async def test_webhook(
    phone: str = Form(...),
    message: str = Form(...)
):
    """
    Endpoint para testar o webhook sem usar Twilio
    """
    try:
        logger.info(f"Teste - Mensagem de {phone}: {message}")
        
        # Verifica se o usuário está cadastrado e ativo
        user = await memory_manager.get_user_by_phone(phone)
        
        if not user:
            # Usuário não cadastrado - oferece cadastro
            resposta = UserMessages.WELCOME_NOT_REGISTERED
        elif not user.get("is_active"):
            # Usuário cadastrado mas não ativo - apenas informa
            resposta = UserMessages.ACCOUNT_INACTIVE
        else:
            # Usuário ativo - processa normalmente

            # Checa histórico ANTES de registrar a mensagem atual
            historico_antes = await memory_manager.get_user_history(phone, limit=1)

            resposta = await bodyflow_graph.processar_mensagem(phone, message)

            # Saúda o usuário no primeiro contato (sem histórico prévio)
            if not historico_antes:
                saudacao = "Olá! Sou o BodyFlow, seu assistente de fitness."
                resposta = f"{saudacao}\n\n{resposta}"
        
        # Salva no histórico
        await memory_manager.save_message(phone, message, "inbound")
        await memory_manager.save_message(phone, resposta, "outbound")
        
        return {
            "success": True,
            "phone": phone,
            "message": message,
            "response": resposta,
            "user_status": user.get("status") if user else "not_found",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Erro no teste: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# Endpoint de criação de usuários removido - apenas consultas na tabela customers

def _clean_message_for_whatsapp(message: str) -> str:
    """
    Limpa mensagem para compatibilidade com WhatsApp Business API sandbox
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

def _create_twiml_response(twiml_content: str):
    """
    Cria resposta TwiML válida para o Twilio WhatsApp Business API
    """
    from fastapi.responses import Response
    
    # Garante que o conteúdo é string limpa e sem caracteres problemáticos
    clean_content = str(twiml_content).strip()
    
    # Remove caracteres que podem causar problemas no sandbox
    clean_content = clean_content.replace('"', '"').replace('"', '"')
    clean_content = clean_content.replace(''', "'").replace(''', "'")
    clean_content = clean_content.replace('–', '-').replace('—', '-')
    
    return Response(
        content=clean_content,
        media_type="application/xml",
        headers={
            "Content-Type": "application/xml; charset=utf-8",
            "Cache-Control": "no-cache"
        }
    )

def _create_error_response(error_message: str):
    """
    Cria resposta de erro em formato TwiML
    """
    error_text = f"Desculpe, ocorreu um erro: {error_message}. Tente novamente em alguns instantes."
    error_text_clean = _clean_message_for_whatsapp(error_text)
    
    twiml_response = MessagingResponse()
    twiml_response.message(error_text_clean)
    
    return _create_twiml_response(str(twiml_response))

# Função auxiliar para validar webhook do Twilio (opcional)
def validate_twilio_signature(request: Request, signature: str, url: str) -> bool:
    """
    Valida a assinatura do Twilio para segurança adicional
    
    Args:
        request: Request do FastAPI
        signature: Assinatura do Twilio
        url: URL do webhook
    
    Returns:
        bool: True se a assinatura for válida
    """
    try:
        from twilio.request_validator import RequestValidator
        
        validator = RequestValidator(Config.TWILIO_AUTH_TOKEN)
        
        # Extrai dados do request
        form_data = request.form()
        
        return validator.validate(
            url=url,
            params=form_data,
            signature=signature
        )
    except Exception as e:
        logger.error(f"Erro na validação da assinatura: {e}")
        return False
