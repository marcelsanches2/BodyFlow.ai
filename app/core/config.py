import os
from dotenv import load_dotenv
from pathlib import Path

# Carrega variáveis de ambiente de múltiplos arquivos possíveis
def load_environment_variables():
    """Carrega variáveis de ambiente de múltiplos arquivos possíveis"""
    possible_files = [
        ".env.secrets",      # Arquivo principal de segredos
        ".env.local",        # Arquivo local
        ".env",              # Arquivo padrão
        ".env_example"       # Arquivo de exemplo (fallback)
    ]
    
    for file_name in possible_files:
        file_path = Path(file_name)
        if file_path.exists():
            print(f"🔐 Carregando variáveis de: {file_name}")
            load_dotenv(file_path)
            return True
    
    print("⚠️ Nenhum arquivo de ambiente encontrado")
    return False

# Carrega variáveis de ambiente
load_environment_variables()

class Config:
    # Supabase Configuration
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    
    # Twilio Configuration
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_WEBHOOK_URL = os.getenv("TELEGRAM_WEBHOOK_URL", "")
    
    # Anthropic Configuration
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "")
    
    # Channel Configuration
    ACTIVE_CHANNEL = os.getenv("ACTIVE_CHANNEL", "")  # "whatsapp" ou "telegram"
    
    # Application Configuration
    DEBUG = os.getenv("DEBUG", "")
    PORT = int(os.getenv("PORT", ""))
