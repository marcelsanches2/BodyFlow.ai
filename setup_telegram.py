#!/usr/bin/env python3
"""
Script para configurar o Telegram Bot do BodyFlow
"""

import os
import sys
import asyncio
import httpx
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

from app.core.config import Config
from app.core.channels import ChannelConfig

async def setup_telegram_webhook():
    """
    Configura o webhook do Telegram
    """
    print("🤖 Configurando Telegram Bot...")
    
    # Verifica se o token está configurado
    bot_token = Config.TELEGRAM_BOT_TOKEN
    if not bot_token:
        print("❌ Token do Telegram não configurado!")
        print("📝 Configure a variável TELEGRAM_BOT_TOKEN no arquivo .env")
        return False
    
    # Verifica se a URL do webhook está configurada
    webhook_url = Config.TELEGRAM_WEBHOOK_URL
    if not webhook_url:
        print("❌ URL do webhook não configurada!")
        print("📝 Configure a variável TELEGRAM_WEBHOOK_URL no arquivo .env")
        return False
    
    print(f"🔗 Configurando webhook: {webhook_url}")
    
    try:
        # Configura o webhook
        url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        data = {"url": webhook_url}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    print("✅ Webhook configurado com sucesso!")
                    return True
                else:
                    print(f"❌ Erro ao configurar webhook: {result.get('description')}")
                    return False
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao configurar webhook: {e}")
        return False

async def get_webhook_info():
    """
    Obtém informações sobre o webhook atual
    """
    bot_token = Config.TELEGRAM_BOT_TOKEN
    if not bot_token:
        print("❌ Token do Telegram não configurado!")
        return
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    webhook_info = result.get("result", {})
                    print("📊 Informações do webhook:")
                    print(f"   URL: {webhook_info.get('url', 'N/A')}")
                    print(f"   Pending updates: {webhook_info.get('pending_update_count', 0)}")
                    print(f"   Last error: {webhook_info.get('last_error_message', 'Nenhum')}")
                else:
                    print(f"❌ Erro ao obter informações: {result.get('description')}")
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Erro ao obter informações: {e}")

async def test_bot():
    """
    Testa se o bot está funcionando
    """
    bot_token = Config.TELEGRAM_BOT_TOKEN
    if not bot_token:
        print("❌ Token do Telegram não configurado!")
        return
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    bot_info = result.get("result", {})
                    print("🤖 Informações do bot:")
                    print(f"   Nome: {bot_info.get('first_name', 'N/A')}")
                    print(f"   Username: @{bot_info.get('username', 'N/A')}")
                    print(f"   ID: {bot_info.get('id', 'N/A')}")
                else:
                    print(f"❌ Erro ao obter informações do bot: {result.get('description')}")
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Erro ao testar bot: {e}")

def main():
    """
    Função principal
    """
    print("🚀 BodyFlow Telegram Setup")
    print("=" * 50)
    
    # Verifica se o canal está ativo
    if not ChannelConfig.is_telegram_active():
        print("⚠️ Canal Telegram não está ativo!")
        print("📝 Configure ACTIVE_CHANNEL=telegram no arquivo .env")
        return
    
    print("✅ Canal Telegram ativo")
    
    # Executa as configurações
    asyncio.run(test_bot())
    print()
    asyncio.run(setup_telegram_webhook())
    print()
    asyncio.run(get_webhook_info())
    
    print("\n🎯 Próximos passos:")
    print("1. Procure pelo seu bot no Telegram")
    print("2. Envie /start")
    print("3. Teste enviando 'treino' ou 'dieta'")

if __name__ == "__main__":
    main()
