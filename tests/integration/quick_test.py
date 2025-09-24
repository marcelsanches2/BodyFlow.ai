#!/usr/bin/env python3
"""
Teste rápido da integração local
"""

import asyncio
import httpx

async def quick_test():
    """Teste rápido"""
    
    BASE_URL = "http://localhost:8000"
    test_phone = "+14155238886"
    
    async with httpx.AsyncClient() as client:
        print("🧪 Teste Rápido - BodyFlow Backend")
        print("=" * 40)
        
        # 1. Testa servidor
        try:
            response = await client.get(f"{BASE_URL}/")
            print("✅ Servidor rodando!")
        except:
            print("❌ Servidor não está rodando!")
            print("💡 Execute: python3 app/main.py")
            return
        
        # 2. Simula webhook Twilio
        print("\n📱 Simulando webhook Twilio...")
        
        form_data = {
            "From": test_phone,
            "Body": "Já finalizei meu cadastro no BodyFlow",
            "MessageSid": "SMtest123"
        }
        
        try:
            response = await client.post(f"{BASE_URL}/whatsapp/", data=form_data)
            print(f"✅ Webhook response: {response.status_code}")
            print(f"📄 Response: {response.text[:100]}...")
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(quick_test())
