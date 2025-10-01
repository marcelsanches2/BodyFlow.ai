#!/usr/bin/env python3
"""
Endpoints de produção para WhatsApp webhook
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from app.services.memory import memory_manager
from app.services.image_storage import image_storage_service
from app.adk.main_graph import bodyflow_graph
import logging

# Configuração de logging
logger = logging.getLogger(__name__)

# Router para endpoints de produção
whatsapp_router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

@whatsapp_router.post("/")
async def webhook_whatsapp(request: Request):
    """
    Webhook principal para receber mensagens do WhatsApp via Twilio
    """
    try:
        form_data = await request.form()
        from_number = form_data.get("From", "")
        message_body = form_data.get("Body", "")
        
        logger.info(f"Mensagem recebida de {from_number}: {message_body}")
        
        # Processa mensagem através do grafo ADK
        try:
            # Determina tipo de conteúdo
            content_type = "text"
            image_data = None
            image_url = None
            
            # Verifica se há imagem
            media_url = form_data.get("MediaUrl0")
            if media_url:
                content_type = "image"
                logger.info(f"📸 Processando imagem do WhatsApp - URL: {media_url}")
                
                try:
                    # Baixa a imagem do Twilio
                    import httpx
                    async with httpx.AsyncClient() as client:
                        response = await client.get(media_url)
                        if response.status_code == 200:
                            image_data = response.content
                            logger.info(f"✅ Imagem baixada com sucesso - Tamanho: {len(image_data)} bytes")
                            
                            # Faz upload da imagem para o Supabase Storage
                            image_url = await image_storage_service.upload_image(
                                image_data=image_data,
                                user_phone=from_number,
                                content_type="image/jpeg",  # Twilio geralmente envia como JPEG
                                image_type="whatsapp_media"
                            )
                            
                            if image_url:
                                logger.info(f"📸 Imagem armazenada no Supabase: {image_url}")
                            else:
                                logger.warning("⚠️ Falha ao armazenar imagem no Supabase")
                        else:
                            logger.error(f"❌ Falha ao baixar imagem: {response.status_code}")
                            image_data = None
                except Exception as e:
                    logger.error(f"❌ Erro ao processar imagem: {e}")
                    image_data = None
                    image_url = None
            
            # Mapeia número de telefone para user_id correto
            user_id = await _get_user_id_from_phone(from_number)
            if not user_id:
                # Usuário não encontrado - retorna mensagem de cadastro
                resposta = """🎉 **Bem-vindo ao BodyFlow.ai!**

Sou seu assistente pessoal de fitness e nutrição. Vou te ajudar a criar um plano personalizado para alcançar seus objetivos!

Para começar, você precisa se cadastrar primeiro no nosso site. 

📱 **Acesse:** [bodyflow.ai](https://bodyflow.ai) para criar sua conta

Após o cadastro, volte aqui e eu te ajudarei a completar seu perfil personalizado com:
• Sua idade, peso e altura
• Seus objetivos de fitness
• Seu nível de treino atual
• Suas restrições alimentares

📸 **Você também poderá enviar fotos de:**
• 🍽️ **Pratos de comida** → Calculo automático de calorias e nutrientes
• 📊 **Bioimpedância** → Análise completa da composição corporal

Depois disso, poderei criar planos de treino e dieta totalmente personalizados para você!

🔗 **Cadastre-se em:** bodyflow.ai"""
                
                # Cria resposta TwiML
                twiml_response = MessagingResponse()
                twiml_response.message(_clean_message_for_whatsapp(resposta))
                
                return _create_twiml_response(str(twiml_response))
            
            # Processa através do grafo ADK
            graph_result = await bodyflow_graph.process_message(
                user_id=user_id,
                content=message_body,
                channel="whatsapp",
                content_type=content_type,
                image_data=image_data
            )
            
            if graph_result.get("success"):
                resposta = graph_result.get("response", "Resposta não disponível")
            else:
                resposta = graph_result.get("response", "Erro interno do sistema")
                
        except Exception as e:
            logger.error(f"Erro no processamento ADK: {e}")
            resposta = "Erro interno do sistema. Tente novamente."
        
        # Limpa a resposta para compatibilidade com WhatsApp
        resposta_limpa = _clean_message_for_whatsapp(resposta)
        
        # Registra mensagem recebida e enviada
        await memory_manager.save_message(from_number, message_body, "inbound", image_url)
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
    # Verifica status do grafo ADK
    graph_status = await bodyflow_graph.get_graph_status()
    
    return {
        "status": "active",
        "service": "BodyFlow WhatsApp Bot",
        "version": "2.0.0",
        "adk_status": graph_status
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

def _clean_message_for_whatsapp(message: str) -> str:
    """
    Limpa mensagem para compatibilidade com WhatsApp Business API sandbox
    """
    if not message:
        return ""
    
    # Remove caracteres problemáticos
    cleaned = str(message).strip()
    
    # Substitui apenas caracteres problemáticos específicos do WhatsApp
    replacements = {
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
    error_text_clean = _clean_message_for_whatsapp(error_message)
    
    twiml_response = MessagingResponse()
    twiml_response.message(error_text_clean)
    
    return _create_twiml_response(str(twiml_response))

async def _get_user_id_from_phone(phone_number: str) -> str:
    """
    Mapeia número de telefone para user_id (UUID) do usuário
    
    Args:
        phone_number: Número de telefone do WhatsApp (formato Twilio)
    
    Returns:
        str: UUID do usuário ou None se não encontrado
    """
    try:
        # Remove prefixo "whatsapp:" se presente
        clean_phone = phone_number.replace("whatsapp:", "")
        
        # Normaliza o número para busca no banco
        normalized_phone = memory_manager._normalize_phone_for_search(clean_phone)
        
        # Busca usuário no banco
        user = await memory_manager.get_user_by_phone(normalized_phone)
        
        if user:
            logger.info(f"✅ Usuário encontrado para WhatsApp {phone_number}: {user.get('name', 'N/A')}")
            return user['id']
        else:
            logger.warning(f"❌ Usuário não encontrado para WhatsApp {phone_number}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao mapear telefone para user_id: {e}")
        return None
