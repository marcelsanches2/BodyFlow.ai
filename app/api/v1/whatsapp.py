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
            
            # Verifica se há imagem (placeholder para implementação futura)
            # if form_data.get("MediaUrl0"):
            #     content_type = "image"
            #     # image_data = await download_image(form_data.get("MediaUrl0"))
            
            # Processa através do grafo ADK
            graph_result = await bodyflow_graph.process_message(
                user_id=from_number,
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
