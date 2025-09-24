# BodyFlow Backend 🤖💪

Backend para chatbot de fitness usando **FastAPI**, **Google ADK** e **Supabase** para responder mensagens do WhatsApp via Twilio.

## 📋 Funcionalidades

- ✅ **Webhook WhatsApp**: Recebe mensagens do Twilio e responde em formato TwiML
- ✅ **Agentes de IA**: Sistema de agentes especializados usando Google ADK
- ✅ **Roteamento Inteligente**: Direciona mensagens para agentes específicos
- ✅ **Memória Persistente**: Salva histórico no Supabase
- ✅ **Dois Agentes Especializados**:
  - 🏋️ **AgenteTreino**: Sugestões de exercícios e treinos
  - 🥗 **AgenteDieta**: Planos alimentares e nutrição

## 🏗️ Arquitetura

```
📂 bodyflow-backend/
├── app/
│   ├── main.py          # Entrypoint FastAPI
│   ├── whatsapp.py      # Webhook Twilio WhatsApp
│   ├── graph.py         # Grafo de agentes (Google ADK)
│   ├── memory.py        # Camada de memória (Supabase)
│   └── agents/
│       ├── __init__.py
│       ├── treino.py    # Agente de treinos
│       └── dieta.py     # Agente de dietas
├── requirements.txt     # Dependências Python
├── config.py           # Configurações
└── README.md
```

## 🚀 Instalação e Configuração

### 1. Clone e Instale Dependências

```bash
cd bodyflow-backend
pip install -r requirements.txt
```

### 2. Configure Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Supabase Configuration
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_anonima_aqui

# Twilio Configuration  
TWILIO_AUTH_TOKEN=seu_auth_token_twilio

# Application Configuration
DEBUG=True
PORT=8000
```

### 3. Configure o Supabase

Execute este SQL no **Supabase SQL Editor**:

```sql
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(20) NOT NULL,
    body TEXT NOT NULL,
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('inbound', 'outbound')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_phone ON messages(phone);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
```

### 4. Execute a Aplicação

```bash
# Desenvolvimento
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Produção
python app/main.py
```

## 📱 Configuração do Twilio WhatsApp

### 1. Configure o Webhook

No console do Twilio, configure o webhook para:
```
https://seu-dominio.com/whatsapp/
```

### 2. Teste o Webhook

Use o endpoint de teste:
```bash
curl -X POST "http://localhost:8000/whatsapp/test" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "phone=+5511999999999&message=quero treino de pernas"
```

## 🎯 Como Funciona

### 1. Fluxo de Mensagens

```
WhatsApp → Twilio → Webhook → Grafo ADK → Agente Específico → Resposta → Twilio → WhatsApp
```

### 2. Roteamento Inteligente

O sistema identifica automaticamente o tipo de consulta:

- **Palavras-chave de TREINO**: `treino`, `exercício`, `academia`, `perna`, `peito`, `costas`, etc.
- **Palavras-chave de DIETA**: `dieta`, `alimentação`, `nutrição`, `emagrecer`, `massa`, etc.
- **Resposta padrão**: Para mensagens não identificadas

### 3. Memória Contextual

- Salva todas as mensagens no Supabase
- Carrega últimas 5 mensagens como contexto
- Mantém histórico da conversa

## 🧪 Testando o Sistema

### 1. Endpoint de Teste

```bash
curl -X POST "http://localhost:8000/whatsapp/test" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "phone=+5511999999999&message=quero treino de pernas"
```

### 2. Exemplos de Mensagens

**Treinos:**
- "quero treino de pernas"
- "me ajuda com exercícios de peito"
- "treino completo para academia"

**Dietas:**
- "preciso de dieta para emagrecer"
- "quero ganhar massa muscular"
- "alimentação saudável"

### 3. Verificar Status

```bash
curl http://localhost:8000/health
curl http://localhost:8000/stats
```

## 📊 Endpoints da API

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Informações da API |
| `/health` | GET | Status da aplicação |
| `/stats` | GET | Estatísticas |
| `/whatsapp/` | POST | Webhook Twilio |
| `/whatsapp/test` | POST | Teste sem Twilio |
| `/whatsapp/status` | GET | Status do webhook |
| `/docs` | GET | Documentação Swagger |

## 🔧 Desenvolvimento

### Estrutura dos Agentes

Cada agente herda de uma classe base e implementa:

```python
class MeuAgente:
    async def processar(self, estado: Dict[str, Any]) -> Dict[str, Any]:
        # Lógica do agente
        estado["resposta"] = "Resposta do agente"
        estado["agente_usado"] = "MeuAgente"
        return estado
```

### Adicionando Novos Agentes

1. Crie um novo arquivo em `app/agents/`
2. Implemente a classe do agente
3. Adicione no `graph.py`:
   - Novo nó do agente
   - Condição de roteamento
   - Conexão no grafo

### Logs e Debugging

```bash
# Logs detalhados
export LOG_LEVEL=DEBUG
python app/main.py
```

## 🚀 Deploy

### 1. Docker (Recomendado)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "app/main.py"]
```

### 2. Railway/Render/Vercel

Configure as variáveis de ambiente e faça deploy do código.

## 📝 Próximos Passos

- [ ] Adicionar mais agentes (suplementos, recuperação, etc.)
- [ ] Implementar autenticação de usuários
- [ ] Adicionar métricas e analytics
- [ ] Integração com APIs de fitness
- [ ] Sistema de agendamento de treinos
- [ ] Chatbot com IA generativa (GPT/Claude)

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

- 📧 Email: suporte@bodyflow.ai
- 💬 Discord: [Link do servidor]
- 📖 Documentação: `/docs` (Swagger UI)

---

**BodyFlow Backend** - Transformando fitness em conversas inteligentes! 💪🤖
