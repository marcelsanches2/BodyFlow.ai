# 🤖 Configuração do Telegram - BodyFlow Backend

## 📋 Pré-requisitos

1. **Conta no Telegram** (gratuita)
2. **Servidor com URL pública** (ngrok, Heroku, VPS, etc.)
3. **Token do Bot** (criado via @BotFather)

## 🚀 Passo a Passo

### **1. Criar o Bot no Telegram**

#### 1.1 Criar o Bot
1. Abra o Telegram
2. Procure por **@BotFather**
3. Envie `/newbot`
4. Digite o nome do bot: `BodyFlow Assistant`
5. Digite o username: `bodyflow_assistant_bot` (deve terminar com `_bot`)
6. **COPIE O TOKEN** fornecido (ex: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### 1.2 Configurar Comandos
1. Envie `/setcommands` para @BotFather
2. Selecione seu bot
3. Cole este texto:
```
start - Iniciar conversa com o BodyFlow
treino - Solicitar treinos e exercícios
dieta - Solicitar dietas e nutrição
help - Ajuda e informações
```

### **2. Configurar Variáveis de Ambiente**

#### 2.1 Criar arquivo .env
Crie um arquivo `.env` na raiz do projeto com:

```bash
# Supabase Configuration
SUPABASE_URL=https://skeajcrmywosbhfnornk.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNrZWFqY3JteXdvc2JoZm5vcm5rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg1ODQzNTYsImV4cCI6MjA3NDE2MDM1Nn0.JZCwaCFOMf2ytRmjEfNnivyDM98ELOjhx6R32vghj1o

# Twilio Configuration
TWILIO_AUTH_TOKEN=532cb2cc270fdc7f85e899e892cd21bb

# Telegram Configuration
TELEGRAM_BOT_TOKEN=SEU_TOKEN_AQUI
TELEGRAM_WEBHOOK_URL=https://seu-dominio.com/telegram/

# Channel Configuration
ACTIVE_CHANNEL=telegram

# Application Configuration
DEBUG=True
PORT=8000

# Test Endpoints
ENABLE_TEST_ENDPOINTS=true
```

#### 2.2 Substituir valores
- `SEU_TOKEN_AQUI` → Token do seu bot
- `https://seu-dominio.com/telegram/` → URL do seu servidor + `/telegram/`

### **3. Configurar URL Pública**

#### 3.1 Usando ngrok (desenvolvimento)
```bash
# Instalar ngrok
# https://ngrok.com/download

# Expor o servidor local
ngrok http 8000

# Copiar a URL (ex: https://abc123.ngrok.io)
# Usar: https://abc123.ngrok.io/telegram/
```

#### 3.2 Usando Heroku (produção)
```bash
# Deploy no Heroku
# URL será: https://seu-app.herokuapp.com/telegram/
```

### **4. Configurar Webhook**

#### 4.1 Usar script automático
```bash
python3 setup_telegram.py
```

#### 4.2 Ou configurar manualmente
```bash
curl -X POST "https://api.telegram.org/botSEU_TOKEN/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://seu-dominio.com/telegram/"}'
```

### **5. Testar o Bot**

#### 5.1 Iniciar o servidor
```bash
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 5.2 Testar no Telegram
1. Procure pelo seu bot no Telegram
2. Envie `/start`
3. Teste enviando:
   - `treino` → Deve responder com treino
   - `dieta` → Deve responder com dieta
   - `oi` → Deve responder com saudação

## 🔧 Troubleshooting

### **Problema: Token não configurado**
```
❌ Token do Telegram não configurado!
```
**Solução:** Verifique se o arquivo `.env` tem `TELEGRAM_BOT_TOKEN=seu_token`

### **Problema: Webhook não configurado**
```
❌ URL do webhook não fornecida
```
**Solução:** Configure `TELEGRAM_WEBHOOK_URL=https://seu-dominio.com/telegram/`

### **Problema: Bot não responde**
1. Verifique se o servidor está rodando
2. Verifique se o webhook está configurado
3. Verifique os logs do servidor

### **Problema: Erro 404**
```
404 Not Found
```
**Solução:** Verifique se a URL do webhook termina com `/telegram/`

## 📊 Verificar Status

### **Status do Bot**
```bash
curl "https://api.telegram.org/botSEU_TOKEN/getMe"
```

### **Status do Webhook**
```bash
curl "https://api.telegram.org/botSEU_TOKEN/getWebhookInfo"
```

### **Status da Aplicação**
```bash
curl "http://localhost:8000/telegram/"
```

## 🔄 Alternar entre Canais

### **Para Telegram**
```bash
ACTIVE_CHANNEL=telegram
```

### **Para WhatsApp**
```bash
ACTIVE_CHANNEL=whatsapp
```

## 🎯 Próximos Passos

1. ✅ Configurar token do bot
2. ✅ Configurar URL do webhook
3. ✅ Testar mensagens
4. ✅ Verificar logs
5. ✅ Deploy em produção (opcional)

## 📞 Suporte

Se tiver problemas:
1. Verifique os logs do servidor
2. Teste os endpoints manualmente
3. Verifique a configuração do webhook
4. Consulte a documentação do Telegram Bot API
