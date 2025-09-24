# Testes do BodyFlow Backend

Esta pasta contém todos os testes do projeto BodyFlow Backend, organizados por tipo e responsabilidade.

## 📁 Estrutura

```
tests/
├── unit/           # Testes unitários
│   ├── test_agents.py
│   ├── test_graph.py
│   └── test_messages.py
├── integration/    # Testes de integração
│   ├── test_webhook_integration.py
│   └── quick_test.py
├── e2e/           # Testes end-to-end
│   └── test_whatsapp_flow.py
└── README.md      # Este arquivo
```

## 🧪 Tipos de Testes

### **Testes Unitários** (`unit/`)
- Testam componentes individuais isoladamente
- Rápidos e focados em uma única funcionalidade
- Usam mocks para dependências externas

### **Testes de Integração** (`integration/`)
- Testam a integração entre componentes
- Verificam se as APIs funcionam corretamente
- Testam webhooks e endpoints

### **Testes End-to-End** (`e2e/`)
- Testam fluxos completos do sistema
- Simulam cenários reais de uso
- Testam toda a cadeia de processamento

## 🚀 Como Executar

### **Executar todos os testes:**
```bash
python run_tests.py
```

### **Executar testes específicos:**
```bash
python run_tests.py unit          # Apenas testes unitários
python run_tests.py integration   # Apenas testes de integração
python run_tests.py e2e          # Apenas testes end-to-end
```

### **Executar com pytest diretamente:**
```bash
pytest tests/unit/               # Testes unitários
pytest tests/integration/        # Testes de integração
pytest tests/e2e/               # Testes end-to-end
pytest tests/                   # Todos os testes
```

### **Executar teste específico:**
```bash
pytest tests/unit/test_agents.py
pytest tests/integration/test_webhook_integration.py
```

## 📋 Testes Disponíveis

### **Testes Unitários:**
- `test_agents.py`: Testa AgenteTreino e AgenteDieta
- `test_graph.py`: Testa BodyFlowGraph e roteamento
- `test_messages.py`: Testa UserMessages e constantes

### **Testes de Integração:**
- `test_webhook_integration.py`: Testa endpoints do WhatsApp
- `quick_test.py`: Teste rápido de integração

### **Testes End-to-End:**
- `test_whatsapp_flow.py`: Testa fluxo completo do WhatsApp

## 🔧 Configuração

Os testes usam:
- **pytest** como framework de testes
- **unittest.mock** para mocks
- **fastapi.testclient** para testes de API
- **pytest-asyncio** para testes assíncronos

## 📝 Adicionando Novos Testes

1. **Escolha o tipo de teste** (unit/integration/e2e)
2. **Crie o arquivo** seguindo o padrão `test_*.py`
3. **Use a classe** `Test*` para organizar os testes
4. **Execute** para verificar se funciona

## 🎯 Boas Práticas

- **Testes unitários**: Rápidos, isolados, com mocks
- **Testes de integração**: Testam APIs e webhooks
- **Testes end-to-end**: Simulam fluxos reais
- **Nomes descritivos**: `test_processar_treino_pernas`
- **Setup/Teardown**: Use `setup_method()` quando necessário
- **Asserções claras**: Use mensagens descritivas
