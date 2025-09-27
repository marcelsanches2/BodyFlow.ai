"""
Serviço centralizado para comunicação com LLMs usando LiteLLM
Suporte a múltiplos provedores com fallback automático
"""

import os
import asyncio
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import litellm
from litellm import completion, acompletion


class LLMService:
    """Serviço centralizado para comunicação com LLMs usando LiteLLM"""
    
    def __init__(self):
        # Carrega variáveis de ambiente
        load_dotenv('.env.secrets')
        
        # Configuração dos provedores
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        self.providers = {
            "anthropic": {
                "api_key": anthropic_key,
                "model": "claude-3-5-sonnet-20241022",
                "priority": 1
            }
        }
        
        # Adiciona OpenAI apenas se a chave for válida (não placeholder)
        if openai_key and openai_key != "your_openai_api_key_here":
            # Adiciona GPT-4o como segunda opção
            self.providers["openai_gpt4o"] = {
                "api_key": openai_key,
                "model": "gpt-4o",
                "priority": 2
            }
            # Adiciona GPT-4o Mini como terceira opção
            self.providers["openai_gpt4o_mini"] = {
                "api_key": openai_key,
                "model": "gpt-4o-mini",
                "priority": 3
            }
        
        # Configurações do LiteLLM
        self.max_retries = 2
        self.base_delay = 1
        self.timeout = 10
        
        # Configura LiteLLM
        self._setup_litellm()
    
    def _setup_litellm(self):
        """Configura LiteLLM com os provedores disponíveis"""
        # Configura timeout global
        litellm.request_timeout = self.timeout
        
        # Configura retry automático
        litellm.num_retries = self.max_retries
        
        # Configura fallback automático
        litellm.drop_params = True
        
        # Configura logging
        litellm.set_verbose = False
    
    async def call_with_fallback(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 2000,
        temperature: float = 0.4,
        fallback_response: Optional[str] = None,
        conversation_context: Optional[str] = None
    ) -> str:
        """
        Chama LLM com fallback automático entre provedores
        
        Args:
            messages: Lista de mensagens para enviar
            max_tokens: Número máximo de tokens
            temperature: Temperatura para geração
            fallback_response: Resposta de fallback se todos os provedores falharem
            conversation_context: Contexto da conversa para manter continuidade
            
        Returns:
            Resposta da API ou fallback_response se houver erro
        """
        # Ordena provedores por prioridade
        sorted_providers = sorted(
            self.providers.items(),
            key=lambda x: x[1]["priority"]
        )
        
        # Prepara mensagens com contexto da conversa se fornecido
        enhanced_messages = messages.copy()
        if conversation_context:
            # Adiciona contexto da conversa como primeira mensagem do sistema
            context_message = {
                "role": "system",
                "content": f"CONTEXTO DA CONVERSA: {conversation_context}\n\nMantenha a continuidade desta conversa e responda de forma natural."
            }
            enhanced_messages = [context_message] + enhanced_messages
        
        for provider_name, provider_config in sorted_providers:
            if not provider_config["api_key"]:
                print(f"⚠️ {provider_name} não configurado, pulando...")
                continue
            
            try:
                print(f"🚀 Tentando {provider_name} ({provider_config['model']})...")
                
                # Log das mensagens para debug
                print(f"🔍 LLMService: Mensagens sendo enviadas:")
                for i, msg in enumerate(enhanced_messages):
                    if msg.get("role") == "user" and isinstance(msg.get("content"), list):
                        print(f"   Mensagem {i}: {msg['role']} - {len(msg['content'])} itens")
                        for j, item in enumerate(msg["content"]):
                            if item.get("type") == "text":
                                print(f"     Item {j}: texto ({len(item['text'])} chars)")
                            elif item.get("type") == "image_url":
                                print(f"     Item {j}: imagem (base64)")
                    else:
                        print(f"   Mensagem {i}: {msg['role']} - {len(str(msg.get('content', '')))} chars")
                
                # Configura modelo para LiteLLM (formato universal)
                model_name = provider_config['model']
                
                print(f"🔧 LLMService: Modelo configurado: {model_name}")
                
                # Configura API key para o provedor
                if provider_name.startswith("anthropic"):
                    os.environ["ANTHROPIC_API_KEY"] = provider_config["api_key"]
                elif provider_name.startswith("openai_"):
                    os.environ["OPENAI_API_KEY"] = provider_config["api_key"]
                
                # Chama LLM com timeout
                response = await asyncio.wait_for(
                    acompletion(
                        model=model_name,
                        messages=enhanced_messages,
                        max_tokens=max_tokens,
                        temperature=temperature
                    ),
                    timeout=self.timeout
                )
                
                # Extrai resposta
                content = response.choices[0].message.content
                print(f"✅ {provider_name} respondeu com sucesso!")
                return content
                
            except asyncio.TimeoutError:
                print(f"⏰ Timeout em {provider_name}")
                continue
                
            except Exception as e:
                error_str = str(e)
                print(f"❌ Erro em {provider_name}: {error_str[:200]}...")
                
                # Log específico para diferentes tipos de erro
                if "RateLimitError" in error_str:
                    print(f"🚫 Rate limit atingido em {provider_name}")
                elif "Invalid user message" in error_str:
                    print(f"📝 Formato de mensagem inválido em {provider_name}")
                elif "NotFoundError" in error_str:
                    print(f"🔍 Modelo não encontrado em {provider_name}")
                elif "AuthenticationError" in error_str:
                    print(f"🔑 Erro de autenticação em {provider_name}")
                
                # Se é erro retriável, tenta próximo provedor
                if self._is_retryable_error(error_str):
                    print(f"🔄 Tentando próximo provedor...")
                    continue
                else:
                    # Erro não retriável, pula para próximo provedor
                    print(f"⏭️ Pulando para próximo provedor...")
                    continue
        
        # Todos os provedores falharam
        print("❌ Todos os provedores falharam")
        
        # Retorna fallback se fornecido
        if fallback_response:
            return fallback_response
        
        # Fallback padrão
        return self._get_default_fallback()
    
    def _is_retryable_error(self, error_str: str) -> bool:
        """Verifica se o erro é retriável"""
        retryable_patterns = [
            "529",
            "overloaded",
            "rate limit",
            "too many requests",
            "service unavailable",
            "temporarily unavailable",
            "timeout",
            "connection"
        ]
        
        error_lower = error_str.lower()
        return any(pattern in error_lower for pattern in retryable_patterns)
    
    def _get_default_fallback(self) -> str:
        """Resposta de fallback padrão quando todos os LLMs falham"""
        return """
🤖 **Serviço Temporariamente Indisponível**

Desculpe, todos os serviços de IA estão com alta demanda no momento.

**O que você pode fazer:**
- Tente novamente em alguns minutos
- Reformule sua pergunta de forma mais simples
- Para orientações básicas, consulte nosso FAQ

**Orientações Gerais de Saúde:**
- Mantenha hidratação adequada (2-3L/dia)
- Consuma proteínas em todas as refeições
- Inclua fibras e micronutrientes
- Evite alimentos ultraprocessados
- Mantenha consistência nos treinos

*Estou trabalhando para melhorar a disponibilidade do serviço.*
"""
    
    def get_contextual_fallback(self, content: str, user_name: str, profile: Dict[str, Any]) -> str:
        """Retorna fallback contextual baseado no conteúdo da mensagem"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["treino", "exercício", "musculação", "academia"]):
            return self._get_training_fallback_sync(user_name, profile)
        elif any(word in content_lower for word in ["comida", "alimentação", "dieta", "nutrição"]):
            return self._get_nutrition_fallback_sync(user_name, profile)
        else:
            return self._get_general_fallback_sync(user_name, profile)
    
    def _get_training_fallback_sync(self, user_name: str, profile: Dict[str, Any]) -> str:
        """Fallback síncrono para consultas de treino"""
        age = profile.get("age", "N/A")
        goal = profile.get("goal", "N/A")
        training_level = profile.get("training_level", "N/A")
        
        return f"""
💪 **Orientação de Treino**

{user_name}, vejo que você está falando sobre treino! 

Baseado no seu perfil:
- Objetivo: {goal}
- Nível: {training_level}
- Idade: {age} anos

**Orientações Gerais:**
- Mantenha consistência nos treinos
- Foque na progressão gradual
- Descanse adequadamente entre sessões
- Hidrate-se bem durante o treino

*Todos os serviços de IA estão com alta demanda no momento. Para orientações mais detalhadas, tente novamente em alguns minutos.*
"""
    
    def _get_nutrition_fallback_sync(self, user_name: str, profile: Dict[str, Any]) -> str:
        """Fallback síncrono para consultas de nutrição"""
        age = profile.get("age", "N/A")
        weight = profile.get("current_weight_kg", "N/A")
        height = profile.get("height_cm", "N/A")
        goal = profile.get("goal", "N/A")
        
        return f"""
🥗 **Orientação Nutricional**

{user_name}, vejo que você está falando sobre alimentação!

Baseado no seu perfil:
- Objetivo: {goal}
- Peso: {weight} kg
- Altura: {height} cm

**Orientações Gerais:**
- Consuma proteínas em todas as refeições
- Mantenha hidratação adequada (2-3L/dia)
- Inclua fibras e micronutrientes
- Evite alimentos ultraprocessados

*Todos os serviços de IA estão com alta demanda no momento. Para orientações mais detalhadas, tente novamente em alguns minutos.*
"""
    
    def _get_general_fallback_sync(self, user_name: str, profile: Dict[str, Any]) -> str:
        """Fallback síncrono geral para consultas"""
        age = profile.get("age", "N/A")
        weight = profile.get("current_weight_kg", "N/A")
        height = profile.get("height_cm", "N/A")
        goal = profile.get("goal", "N/A")
        
        return f"""
👩‍⚕️ **Consulta Nutricional**

{user_name}, estou aqui para te ajudar!

Baseado no seu perfil:
- Idade: {age} anos
- Peso: {weight} kg
- Altura: {height} cm
- Objetivo: {goal}

**Orientações Gerais:**
- Mantenha hidratação adequada (2-3L/dia)
- Consuma proteínas em todas as refeições
- Inclua fibras e micronutrientes
- Evite alimentos ultraprocessados

*Todos os serviços de IA estão com alta demanda no momento. Para orientações mais detalhadas, tente novamente em alguns minutos.*
"""
    
    def get_available_providers(self) -> List[str]:
        """Retorna lista de provedores disponíveis"""
        available = []
        for provider_name, provider_config in self.providers.items():
            if provider_config["api_key"]:
                available.append(provider_name)
        return available
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Retorna informações sobre os provedores configurados"""
        info = {}
        for provider_name, provider_config in self.providers.items():
            info[provider_name] = {
                "configured": bool(provider_config["api_key"]),
                "model": provider_config["model"],
                "priority": provider_config["priority"]
            }
        return info


# Instância global do serviço
llm_service = LLMService()
