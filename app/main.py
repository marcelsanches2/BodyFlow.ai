from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.config import Config
from app.core.channels import ChannelConfig
from app.api.v1.telegram import telegram_router

# Import condicional do WhatsApp
try:
    from app.api.v1.whatsapp import whatsapp_router
    WHATSAPP_AVAILABLE = True
except ImportError:
    WHATSAPP_AVAILABLE = False
    logger.warning("⚠️ WhatsApp router não disponível (twilio não instalado)")
from app.services.memory import memory_manager

# Importa endpoints de teste apenas se habilitados
try:
    from app.api.test.test_endpoints import test_router
    from app.api.test.config import TestConfig
    TEST_ENDPOINTS_ENABLED = TestConfig.ENABLE_TEST_ENDPOINTS
except ImportError:
    TEST_ENDPOINTS_ENABLED = False

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Criação da aplicação FastAPI
app = FastAPI(
    title="BodyFlow Backend",
    description="Backend para chatbot de fitness com WhatsApp, FastAPI e Google ADK",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui routers baseado no canal ativo
if ChannelConfig.is_whatsapp_active() and WHATSAPP_AVAILABLE:
    app.include_router(whatsapp_router)
    logger.info("✅ Canal WhatsApp ativo")
elif ChannelConfig.is_telegram_active():
    app.include_router(telegram_router)
    logger.info("✅ Canal Telegram ativo")
elif ChannelConfig.is_whatsapp_active() and not WHATSAPP_AVAILABLE:
    logger.error("❌ WhatsApp solicitado mas twilio não está instalado")
    logger.info("🔄 Fallback para Telegram")
    app.include_router(telegram_router)

# Inclui endpoints de teste apenas se habilitados
if TEST_ENDPOINTS_ENABLED:
    app.include_router(test_router)
    logger.info("✅ Endpoints de teste habilitados")
else:
    logger.info("ℹ️ Endpoints de teste desabilitados")

@app.on_event("startup")
async def startup_event():
    """
    Evento executado na inicialização da aplicação
    """
    logger.info("🚀 Iniciando BodyFlow Backend...")
    logger.info("✅ BodyFlow Backend iniciado com sucesso!")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento executado no encerramento da aplicação
    """
    logger.info("🛑 Encerrando BodyFlow Backend...")

@app.get("/")
async def root():
    """
    Endpoint raiz da aplicação
    """
    return {
        "message": "BodyFlow Backend API",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs",
        "whatsapp_webhook": "/whatsapp/",
        "test_endpoint": "/whatsapp/test"
    }

@app.get("/health")
async def health_check():
    """
    Endpoint de verificação de saúde da aplicação
    """
    return {
        "status": "healthy",
        "message": "BodyFlow Backend is running",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/stats")
async def get_stats():
    """
    Endpoint para obter estatísticas da aplicação
    """
    try:
        # Aqui você pode adicionar lógica para buscar estatísticas do Supabase
        return {
            "total_messages": 0,  # Implementar busca no Supabase
            "active_users": 0,   # Implementar busca no Supabase
            "uptime": "running",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Handler global para exceções não tratadas
    """
    logger.error(f"Erro não tratado: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "Ocorreu um erro interno. Tente novamente mais tarde."
        }
    )

if __name__ == "__main__":
    """
    Executa a aplicação diretamente
    """
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=Config.PORT,
        reload=Config.DEBUG,
        log_level="info"
    )
