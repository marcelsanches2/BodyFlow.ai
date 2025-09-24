# Endpoints de Teste - BodyFlow Backend

Esta pasta contém endpoints específicos para desenvolvimento, teste e debug do sistema BodyFlow.

## 📁 Estrutura

```
app/api/v1/test/
├── __init__.py
├── config.py           # Configuração dos endpoints de teste
├── test_endpoints.py   # Implementação dos endpoints
└── README.md          # Este arquivo
```

## 🚀 Endpoints Disponíveis

### **Endpoints de Teste:**

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/test/ultra-simple` | POST | Teste ultra simples com TwiML "Hi" |
| `/test/webhook` | POST | Teste de webhook sem Twilio |
| `/test/webhook-logic` | POST | Teste da lógica do webhook |
| `/test/debug-user/{phone}` | GET | Debug de busca de usuário |
| `/test/status` | GET | Status dos endpoints de teste |
| `/test/memory` | GET | Teste de conexão com memória |

### **Endpoints de Produção:**

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/whatsapp/` | POST | Webhook principal do WhatsApp |
| `/whatsapp/status` | GET | Status do webhook de produção |
| `/whatsapp/status-callback` | POST | Callback de status do Twilio |

## ⚙️ Configuração

### **Habilitar/Desabilitar Endpoints de Teste:**

```bash
# Habilitar endpoints de teste
export ENABLE_TEST_ENDPOINTS=true

# Desabilitar endpoints de teste
export ENABLE_TEST_ENDPOINTS=false
```

### **Variáveis de Ambiente:**

- `ENABLE_TEST_ENDPOINTS`: Controla se endpoints de teste estão disponíveis
- `DEBUG`: Modo de debug (afeta alguns endpoints)

## 🔧 Como Usar

### **1. Teste Ultra Simples:**
```bash
curl -X POST "http://localhost:8000/test/ultra-simple" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:+5511940751013&Body=teste"
```

### **2. Debug de Usuário:**
```bash
curl "http://localhost:8000/test/debug-user/whatsapp:+5511940751013"
```

### **3. Teste de Lógica:**
```bash
curl -X POST "http://localhost:8000/test/webhook-logic" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+5511940751013", "message": "treino de pernas"}'
```

### **4. Status dos Endpoints:**
```bash
curl "http://localhost:8000/test/status"
```

## 🎯 Benefícios da Separação

### **✅ Endpoints de Produção:**
- **Limpos e focados** apenas no que é necessário
- **Sem código de debug** ou teste
- **Performance otimizada**
- **Segurança** (sem endpoints de debug expostos)

### **✅ Endpoints de Teste:**
- **Organizados** em pasta separada
- **Fácil de habilitar/desabilitar**
- **Documentação específica**
- **Não interferem** na produção

## 🚨 Segurança

### **Em Produção:**
- Endpoints de teste **devem ser desabilitados**
- Use `ENABLE_TEST_ENDPOINTS=false`
- Endpoints de debug **não devem estar expostos**

### **Em Desenvolvimento:**
- Endpoints de teste **podem ser habilitados**
- Use `ENABLE_TEST_ENDPOINTS=true`
- Úteis para debug e desenvolvimento

## 📝 Exemplos de Uso

### **Desenvolvimento:**
```bash
# Inicia servidor com endpoints de teste
ENABLE_TEST_ENDPOINTS=true python app/main.py
```

### **Produção:**
```bash
# Inicia servidor apenas com endpoints de produção
ENABLE_TEST_ENDPOINTS=false python app/main.py
```

## 🔍 Monitoramento

Os endpoints de teste incluem logs específicos:
- `Teste ultra simples - De: {from_number}, Mensagem: {message_body}`
- `Teste webhook - De: {from_number}, Mensagem: {message_body}`
- `Teste de lógica - Phone: {phone}, Message: {message}`

## 📋 Checklist

- [ ] Endpoints de produção funcionando
- [ ] Endpoints de teste separados
- [ ] Configuração de habilitação/desabilitação
- [ ] Documentação atualizada
- [ ] Testes unitários atualizados
- [ ] Segurança verificada
