import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

class Config:
    # Supabase Configuration
    SUPABASE_URL = os.getenv("SUPABASE_URL", "https://skeajcrmywosbhfnornk.supabase.co")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNrZWFqY3JteXdvc2JoZm5vcm5rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg1ODQzNTYsImV4cCI6MjA3NDE2MDM1Nn0.JZCwaCFOMf2ytRmjEfNnivyDM98ELOjhx6R32vghj1o")

    
    # Twilio Configuration
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "532cb2cc270fdc7f85e899e892cd21bb")
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8397034210:AAGpJOcyje4wL0bScsRCQJBvS6zu3LgtSaE")
    TELEGRAM_WEBHOOK_URL = os.getenv("TELEGRAM_WEBHOOK_URL", "https://bannered-anh-laughably.ngrok-free.dev/telegram/")
    
    # Anthropic Configuration
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    
    # Channel Configuration
    ACTIVE_CHANNEL = os.getenv("ACTIVE_CHANNEL", "telegram")  # "whatsapp" ou "telegram"
    
    # Application Configuration
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    PORT = int(os.getenv("PORT", "8000"))
    
    # Session Configuration
    SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))
