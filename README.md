# BodyFlow.ai Backend

Sistema de IA para análise nutricional e treino personalizado usando Google ADK.

## 🚀 Configuração Rápida

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

**Opção A: Usando arquivo .env (Recomendado)**
```bash
# Copie o arquivo de exemplo
cp .env_example .env

# Edite o .env com suas chaves reais
nano .env
```

**Opção B: Usando setup_env.py**
```bash
# O script detectará automaticamente se existe .env
python3 setup_env.py
```

### 3. Executar o Sistema
```bash
python3 -m uvicorn app.main:app --reload --port 8000
```

## 🔑 Variáveis de Ambiente Necessárias

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `ANTHROPIC_API_KEY` | Chave da API Anthropic | `sk-ant-api03-...` |
| `SUPABASE_URL` | URL do projeto Supabase | `https://xxx.supabase.co` |
| `SUPABASE_KEY` | Chave anônima do Supabase | `eyJhbGciOiJIUzI1NiIs...` |
| `TELEGRAM_BOT_TOKEN` | Token do bot do Telegram | `1234567890:ABC...` |

## 📁 Estrutura do Projeto

```
bodyflow-backend/
├── app/
│   ├── adk/                 # Google ADK - Orquestração
│   │   ├── agents/          # Agentes de IA
│   │   ├── main_graph.py    # Grafo principal
│   │   └── ...
│   ├── api/                 # APIs REST
│   ├── services/           # Serviços (memória, sessão)
│   └── tools/              # Ferramentas (multimodal, memória)
├── .env_example            # Exemplo de configuração
├── setup_env.py           # Script de configuração
└── requirements.txt       # Dependências Python
```

## 🤖 Agentes Disponíveis

- **Onboarding Agent**: Cadastro e atualização de perfil
- **Super Personal Trainer Agent**: Análise nutricional, treino e saúde

## 🔄 Fluxo de Mensagens

1. **Telegram/WhatsApp** → `RouterNode`
2. **RouterNode** → `TextOrchestrator` ou `ImageOrchestrator`
3. **Orchestrator** → `SuperPersonalTrainerAgent`
4. **Agent** → Resposta personalizada

## 🧠 Recursos de IA

- **Análise de Imagens**: Identificação de alimentos, estimativa de calorias
- **Memória Persistente**: Histórico de conversas em 3 camadas
- **Sessões Ativas**: Continuidade de contexto entre mensagens
- **Multimodal**: Processamento de texto e imagem simultaneamente

## 🛠️ Desenvolvimento

### Testes Locais
```bash
# Teste básico
python3 -c "exec(open('setup_env.py').read()); from app.adk.main_graph import MainGraph; print('✅ Sistema OK')"

# Teste com imagem
python3 app/api/test/test_endpoints.py
```

### Logs e Debug
- Logs são salvos em `logs/`
- Use `DEBUG=True` no `.env` para logs detalhados

## 🔒 Segurança

- ✅ Chaves sensíveis são carregadas apenas do arquivo `.env`
- ✅ Arquivo `.env` está no `.gitignore`
- ✅ Arquivos de exemplo usam placeholders
- ✅ Chaves são mascaradas nos logs

## 📞 Suporte

Para dúvidas ou problemas, verifique:
1. Se todas as variáveis de ambiente estão configuradas
2. Se as chaves de API são válidas
3. Se o arquivo `.env` existe e está no diretório correto