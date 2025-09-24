#!/usr/bin/env python3
"""
Endpoints de teste para desenvolvimento e debug
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from app.services.memory import memory_manager
from app.utils.messages import UserMessages
import logging

# Configuração de logging
logger = logging.getLogger(__name__)

# Router para endpoints de teste
test_router = APIRouter(prefix="/test", tags=["Test"])

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

@test_router.post("/ultra-simple")
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

@test_router.get("/debug-user/{phone}")
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

@test_router.post("/webhook-logic")
async def test_webhook_logic(
    phone: str,
    message: str,
    user_exists: bool = True,
    user_active: bool = True
):
    """
    Endpoint para testar lógica do webhook sem dependências externas
    """
    try:
        logger.info(f"Teste de lógica - Phone: {phone}, Message: {message}")
        
        # Simula lógica do webhook
        if not user_exists:
            return {
                "response": UserMessages.WELCOME_NOT_REGISTERED,
                "status": "user_not_found"
            }
        
        if not user_active:
            return {
                "response": UserMessages.ACCOUNT_INACTIVE,
                "status": "user_inactive"
            }
        
        # Simula processamento normal
        if "treino" in message.lower():
            return {
                "response": UserMessages.Treino.PERNAS_RESPONSE,
                "status": "processed",
                "agent": "treino"
            }
        elif "dieta" in message.lower():
            return {
                "response": UserMessages.Dieta.PERDER_PESO_RESPONSE,
                "status": "processed",
                "agent": "dieta"
            }
        else:
            return {
                "response": UserMessages.Router.DEFAULT_RESPONSE,
                "status": "processed",
                "agent": "default"
            }
            
    except Exception as e:
        logger.error(f"Erro no teste de lógica: {e}")
        return {
            "error": str(e),
            "status": "error"
        }

@test_router.post("/webhook")
async def test_webhook(request: Request):
    """
    Endpoint de teste para webhook do WhatsApp
    """
    try:
        form_data = await request.form()
        from_number = form_data.get("From", "")
        message_body = form_data.get("Body", "")
        
        logger.info(f"Teste webhook - De: {from_number}, Mensagem: {message_body}")
        
        # Resposta de teste simples
        twiml_response = MessagingResponse()
        twiml_response.message("Teste webhook funcionando!")
        
        return _create_twiml_response(str(twiml_response))
        
    except Exception as e:
        logger.error(f"Erro no teste webhook: {e}")
        twiml_response = MessagingResponse()
        twiml_response.message("Erro no teste")
        return _create_twiml_response(str(twiml_response))

@test_router.get("/status")
async def test_status():
    """
    Endpoint de status para testes
    """
    return {
        "status": "test_active",
        "service": "BodyFlow Test Endpoints",
        "version": "1.0.0",
        "endpoints": [
            "/test/ultra-simple",
            "/test/debug-user/{phone}",
            "/test/webhook-logic",
            "/test/webhook",
            "/test/status"
        ]
    }

@test_router.get("/memory")
async def test_memory():
    """
    Endpoint para testar conexão com memória
    """
    try:
        # Testa conexão com Supabase
        test_result = await memory_manager.get_user_history("test", limit=1)
        return {
            "status": "memory_ok",
            "supabase_connected": True,
            "test_result": test_result
        }
    except Exception as e:
        return {
            "status": "memory_error",
            "supabase_connected": False,
            "error": str(e)
        }
