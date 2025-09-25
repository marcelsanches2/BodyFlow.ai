# API - BodyFlow Backend

Esta pasta contém todos os endpoints da API do BodyFlow Backend, organizados por versão.

## 📁 Estrutura

```
app/api/
├── README.md           # Documentação da API
├── test/               # Endpoints de teste e debug
│   ├── config.py       # Configuração dos endpoints de teste
│   ├── test_endpoints.py # Implementação dos endpoints de teste
│   └── README.md       # Documentação dos endpoints de teste
└── v1/                 # Versão 1 da API
    ├── whatsapp.py      # Endpoints de produção do WhatsApp
    ├── whatsapp_old.py  # Backup do arquivo antigo
    └── whatsapp_production.py # Backup do arquivo de produção
```

## 🚀 Endpoints Disponíveis

### **API v1 - Endpoints de Produção:**

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/whatsapp/` | POST | Webhook principal do WhatsApp |
| `/whatsapp/status` | GET | Status do webhook de produção |
| `/whatsapp/status-callback` | POST | Callback de status do Twilio |

### **API - Endpoints de Teste:**

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/test/ultra-simple` | POST | Teste ultra simples com TwiML "Hi" |
| `/test/webhook` | POST | Teste de webhook sem Twilio |
| `/test/webhook-logic` | POST | Teste da lógica do webhook |
| `/test/debug-user/{phone}` | GET | Debug de busca de usuário |
| `/test/status` | GET | Status dos endpoints de teste |
| `/test/memory` | GET | Teste de conexão com memória |

## ⚙️ Configuração

### **Habilitar/Desabilitar Endpoints de Teste:**

```bash
# Desenvolvimento (endpoints de teste habilitados)
ENABLE_TEST_ENDPOINTS=true

# Produção (endpoints de teste desabilitados)
ENABLE_TEST_ENDPOINTS=false
```

## 🔧 Como Usar

### **Desenvolvimento:**
```bash
ENABLE_TEST_ENDPOINTS=true python app/main.py
# Endpoints de teste disponíveis em /test/*
# Endpoints de produção disponíveis em /whatsapp/*
```

### **Produção:**
```bash
ENABLE_TEST_ENDPOINTS=false python app/main.py
# Apenas endpoints de produção em /whatsapp/*
```

## 📋 Versões da API

### **v1 (Atual):**
- Endpoints do WhatsApp
- Endpoints de teste e debug
- Suporte completo ao Twilio
- Integração com Supabase

### **Futuras Versões:**
- v2: Novos recursos e melhorias
- v3: Refatorações e otimizações

## 🎯 Benefícios da Estrutura

1. **Organização por versão** - Fácil manutenção e evolução
2. **Separação clara** entre produção e teste
3. **Escalabilidade** - Preparado para novas versões
4. **Documentação específica** para cada versão
5. **Testes organizados** por tipo e versão

## 📝 Exemplos de Uso

### **Webhook Principal:**
```bash
curl -X POST "http://localhost:8000/whatsapp/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:+5511940751013&Body=treino de pernas"
```

### **Status do Webhook:**
```bash
curl "http://localhost:8000/whatsapp/status"
```

### **Teste de Debug:**
```bash
curl "http://localhost:8000/test/debug-user/+5511940751013"
```

## 🔍 Monitoramento

Todos os endpoints incluem logs específicos:
- Endpoints de produção: `Mensagem recebida de {from_number}: {message_body}`
- Endpoints de teste: `Teste - De: {from_number}, Mensagem: {message_body}`

## 📋 Checklist

- [ ] Endpoints de produção funcionando
- [ ] Endpoints de teste separados
- [ ] Configuração de habilitação/desabilitação
- [ ] Documentação atualizada
- [ ] Testes unitários atualizados
- [ ] Testes de integração atualizados
- [ ] Segurança verificada
- [ ] Estrutura por versão implementada
