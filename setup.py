#!/usr/bin/env python3
"""
Script de setup para o BodyFlow Backend
Este script ajuda a configurar o ambiente e testar a aplicação
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ é necessário")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    return True

def install_dependencies():
    """Instala as dependências do projeto"""
    print("\n📦 Instalando dependências...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def create_env_file():
    """Cria arquivo .env se não existir"""
    env_file = Path(".env")
    if not env_file.exists():
        print("\n📝 Criando arquivo .env...")
        env_content = """# Supabase Configuration
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_anonima_aqui

# Twilio Configuration
TWILIO_AUTH_TOKEN=seu_auth_token_twilio

# Application Configuration
DEBUG=True
PORT=8000
"""
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ Arquivo .env criado!")
        print("⚠️  Configure as variáveis de ambiente no arquivo .env")
    else:
        print("✅ Arquivo .env já existe")

def show_supabase_sql():
    """Mostra o SQL necessário para criar a tabela no Supabase"""
    print("\n🗄️ SQL para Supabase:")
    print("=" * 50)
    sql = """
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(20) NOT NULL,
    body TEXT NOT NULL,
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('inbound', 'outbound')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_phone ON messages(phone);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
"""
    print(sql)
    print("=" * 50)
    print("💡 Execute este SQL no Supabase SQL Editor")

def show_next_steps():
    """Mostra os próximos passos"""
    print("\n🚀 Próximos Passos:")
    print("=" * 30)
    print("1. Configure as variáveis no arquivo .env")
    print("2. Execute o SQL no Supabase")
    print("3. Inicie o servidor:")
    print("   python app/main.py")
    print("4. Teste a aplicação:")
    print("   python test_example.py")
    print("5. Configure o webhook no Twilio:")
    print("   https://seu-dominio.com/whatsapp/")

def main():
    """Função principal do setup"""
    print("🤖 BodyFlow Backend - Setup")
    print("=" * 40)
    
    # Verifica Python
    if not check_python_version():
        return
    
    # Instala dependências
    if not install_dependencies():
        return
    
    # Cria arquivo .env
    create_env_file()
    
    # Mostra SQL do Supabase
    show_supabase_sql()
    
    # Mostra próximos passos
    show_next_steps()
    
    print("\n✅ Setup concluído!")
    print("🎉 Seu BodyFlow Backend está pronto para uso!")

if __name__ == "__main__":
    main()
