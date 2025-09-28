"""
Orquestrador de Texto para ADK
"""

import asyncio
import os
import time
from typing import Dict, Any, Optional, List
from app.adk.simple_adk import Node
from app.tools.memory_tool import MemoryTool
from app.tools.observability_tool import ObservabilityTool
from app.services.session_manager import SessionManager
from app.services.llm_service import llm_service

class TextOrchestratorNode(Node):
    """Nó orquestrador para processamento de texto"""
    
    def __init__(self):
        super().__init__(
            name="text_orchestrator",
            description="Orquestra processamento de mensagens de texto"
        )
        self.memory_tool = MemoryTool()
        self.observability_tool = ObservabilityTool()
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orquestrador inteligente que analisa a necessidade real do usuário e roteia para o agente apropriado
        """
        start_time = time.time()
        
        try:
            user_id = input_data.get("user_id", "")
            content = input_data.get("content", "")
            
            print(f"🧠 TextOrchestrator: Analisando mensagem do usuário {user_id}: '{content}'")
            
            # Recupera contexto completo em três camadas (se não foi fornecido)
            if "context" not in input_data:
                context = await self.memory_tool.get_context_for_agent(user_id, "text_orchestrator")
            else:
                context = input_data.get("context", {})
            
            # Verifica se há imagem - se sim, redireciona diretamente para Image Orchestrator
            image_data = input_data.get("image_data")
            if image_data:
                print(f"🖼️ TextOrchestrator: Imagem detectada - redirecionando para Image Orchestrator")
                return await self._route_to_agent("image_orchestrator", user_id, content, context, image_data=image_data)
            
            # Verifica se é compartilhamento de contato
            if content == "Contato compartilhado - verificar acesso":
                print(f"📞 TextOrchestrator: Processando compartilhamento de contato")
                agent_result = await self._handle_contact_sharing(user_id, content, context)
                confidence = 1.0
                intent = "contact_verification"
            else:
                # Análise inteligente da situação do usuário e necessidade real
                user_analysis = await self._analyze_user_situation_and_intent(content, context)
                print(f"🔍 TextOrchestrator: Análise do usuário: {user_analysis}")
                
                # Roteamento inteligente baseado na análise
                agent_result = await self._intelligent_routing(user_id, content, context, user_analysis)
                confidence = user_analysis.get("confidence", 0.8)
                intent = user_analysis.get("intent", "unknown")
            
            # Atualiza resumo da sessão
            await self._update_session_summary(user_id, intent, agent_result.get("response", ""))
            
            execution_time = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "response": agent_result.get("response", ""),
                "agent_activated": agent_result.get("agent_name", ""),
                "confidence": confidence,
                "routing_decision": {
                    "intent": intent,
                    "confidence": confidence,
                    "context_used": len(context.get("short_term", [])),
                    "execution_time_ms": execution_time
                }
            }
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error_message = f"Erro no TextOrchestratorNode: {str(e)[:200]}"
            print(f"❌ {error_message}")
            print(f"❌ Traceback: {str(e)}")
            return {
                "success": False,
                "response": "Desculpe, ocorreu um erro ao processar sua mensagem.",
                "agent_activated": "error",
                "confidence": 0.0,
                "routing_decision": {
                    "error": str(e)[:100],
                    "execution_time_ms": execution_time
                }
            }
    
    async def _analyze_user_situation_and_intent(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Análise inteligente da situação do usuário e sua necessidade real
        """
        try:
            # Contexto do usuário
            long_term = context.get("long_term", {})
            short_term = context.get("short_term", [])
            medium_term = context.get("medium_term", {})
            
            # Status do usuário
            user_exists = bool(long_term.get("user_id"))
            onboarding_completed = long_term.get("onboarding_completed", False)
            current_profile = long_term.get("profile", {})
            
            # Histórico recente
            recent_messages = []
            if short_term:
                recent_messages = [f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in short_term[-3:]]
            
            # Última sessão
            last_session = medium_term.get("last_session", {})
            last_topic = last_session.get("last_active_topic", "")
            
            # Verifica se há sessão ativa de agente específico
            active_session = await SessionManager.get_active_session(context.get("user_id", ""))
            active_agent = active_session.get("active_agent") if active_session else ""
            
            prompt = f"""
Você é um assistente inteligente que entende profundamente as necessidades reais dos usuários de fitness e saúde.

CONTEXTO COMPLETO DO USUÁRIO:
- Usuário existe no sistema: {user_exists}
- Onboarding completo: {onboarding_completed}
- Perfil atual: {current_profile}
- Últimas mensagens: {' | '.join(recent_messages) if recent_messages else 'Nenhuma'}
- Último tópico ativo: {last_topic}
- Agente ativo atual: {active_agent if active_agent else 'Nenhum'}

MENSAGEM ATUAL: "{content}"

ANÁLISE INTELIGENTE:
Analise a mensagem do usuário e determine sua intenção.

MENSAGEM: "{content}"
ONBOARDING COMPLETO: {onboarding_completed}

INTENÇÕES POSSÍVEIS:
- "registration" - Usuário não existe, precisa se cadastrar
- "onboarding" - Usuário existe mas precisa completar perfil (inclui comandos como /start, "olá", "oi")
- "profile_update" - Usuário quer atualizar dados
- "super_personal_trainer" - Usuário quer consulta de saúde/nutrição/treino
- "saudacao" - Cumprimento
- "suporte" - Dúvidas/problemas
- "unknown" - Não conseguiu entender

IMPORTANTE: Comandos como "/start", "/iniciar", "olá", "oi" devem ser classificados como "onboarding" se o usuário existe mas não completou o onboarding, ou "saudacao" se já completou.

RESPONDA EM JSON:
{{
    "situation": "situação_do_usuário",
    "real_need": "necessidade_real",
    "intent": "intenção_específica",
    "confidence": 0.8,
    "reasoning": "explicação"
}}
"""
            
            # Usa o serviço centralizado LiteLLM
            fallback_response = """{
                "situation": "erro na análise",
                "real_need": "não identificada",
                "intent": "unknown",
                "confidence": 0.3,
                "reasoning": "LLM sobrecarregado - usando fallback para detecção simples"
            }"""
            
            result = await llm_service.call_with_fallback(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.1,
                fallback_response=fallback_response
            )
            
            # Tenta extrair JSON da resposta
            import json
            try:
                print(f"🔍 TextOrchestrator: Resposta bruta do LLM: '{result[:200]}...'")
                
                # Verifica se a resposta está vazia
                if not result or result.strip() == "":
                    print(f"⚠️ TextOrchestrator: Resposta vazia do LLM")
                    raise json.JSONDecodeError("Empty response", result, 0)
                
                # Remove possíveis markdown ou texto extra
                if "```json" in result:
                    result = result.split("```json")[1].split("```")[0]
                elif "```" in result:
                    result = result.split("```")[1].split("```")[0]
                
                # Limpa espaços em branco
                result = result.strip()
                
                print(f"🔍 TextOrchestrator: JSON limpo: '{result[:200]}...'")
                
                analysis = json.loads(result)
                print(f"✅ TextOrchestrator: JSON parseado com sucesso: {analysis}")
                return analysis
                
            except json.JSONDecodeError as e:
                print(f"❌ TextOrchestrator: Erro ao parsear JSON: {e}")
                print(f"❌ TextOrchestrator: Conteúdo que falhou: {result}")
                
                # Tenta usar detecção simples como fallback
                simple_intent = await self._simple_update_detection(content)
                if simple_intent:
                    print(f"🎯 TextOrchestrator: Usando detecção simples como fallback: {simple_intent}")
                    return {
                        "situation": "análise com detecção simples",
                        "real_need": "necessidade detectada por palavras-chave",
                        "intent": simple_intent,
                        "confidence": 0.7,
                        "reasoning": "JSON inválido - usando detecção simples"
                    }
                
                # Fallback final se não conseguir detectar nada
                return {
                    "situation": "análise falhou",
                    "real_need": "não identificada",
                    "intent": "unknown",
                    "confidence": 0.3,
                    "reasoning": "erro na análise - JSON inválido"
                }
                
        except Exception as e:
            print(f"❌ Erro na análise inteligente: {e}")
            return {
                "situation": "erro na análise",
                "real_need": "não identificada", 
                "intent": "unknown",
                "confidence": 0.1,
                "reasoning": f"erro: {e}"
            }
    
    async def _intelligent_routing(self, user_id: str, content: str, context: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Roteamento inteligente baseado na análise do usuário
        """
        try:
            intent = analysis.get("intent", "unknown")
            confidence = analysis.get("confidence", 0.5)
            
            print(f"🎯 TextOrchestrator: Roteando para intent '{intent}' com confiança {confidence}")
            
            # Verifica se há sessão ativa que deve ser mantida
            active_session = await SessionManager.get_active_session(user_id)
            active_agent = active_session.get("active_agent") if active_session else None
            
            print(f"🔍 TextOrchestrator: Sessão ativa para {user_id}: {active_session}")
            print(f"🔍 TextOrchestrator: Agente ativo: {active_agent}")
            
            if active_agent == "super_personal_trainer_agent":
                print(f"🔒 TextOrchestrator: Mantendo sessão ativa do Super Personal Trainer")
                return await self._route_to_agent("super_personal_trainer", user_id, content, context)
            
            # Roteamento baseado na análise inteligente
            if intent == "registration":
                # Usuário não existe - precisa se cadastrar
                return {
                    "agent_name": "registration_required",
                    "response": """🎉 **Bem-vindo ao BodyFlow.ai!**

Sou seu assistente pessoal de fitness e nutrição. Vou te ajudar a criar um plano personalizado para alcançar seus objetivos!

Para começar, você precisa se cadastrar primeiro no nosso site. 

📱 **Acesse:** [bodyflow.ai](https://bodyflow.ai) para criar sua conta

Após o cadastro, volte aqui e eu te ajudarei a completar seu perfil personalizado com:
• Sua idade, peso e altura
• Seus objetivos de fitness
• Seu nível de treino atual
• Suas restrições alimentares

Depois disso, poderei criar planos de treino e dieta totalmente personalizados para você!

🔗 **Cadastre-se em:** bodyflow.ai"""
                }
            
            elif intent == "onboarding":
                # Usuário existe mas precisa completar onboarding
                return await self._route_to_agent("onboarding", user_id, content, context, force_welcome=False)
            
            elif intent == "profile_update":
                # Usuário quer atualizar dados do perfil - detecta campo específico
                specific_field = await self._detect_specific_field(content)
                if specific_field:
                    print(f"🎯 TextOrchestrator: Campo específico detectado: {specific_field}")
                    return await self._route_to_agent("onboarding", user_id, content, context, force_welcome=False, update_intent=specific_field)
                else:
                    # Se não detectar campo específico, mostra perfil geral
                    return await self._route_to_agent("onboarding", user_id, content, context, force_welcome=False, update_intent="profile")
            
            elif intent == "super_personal_trainer":
                # Verifica se usuário completou onboarding antes de ir para Super Personal Trainer
                long_term = context.get("long_term", {})
                onboarding_completed = long_term.get("onboarding_completed", False)
                
                
                if not onboarding_completed:
                    # Usuário não completou onboarding - obrigatório ir para Profile Agent
                    print(f"🔒 TextOrchestrator: Usuário {user_id} não completou onboarding - redirecionando para Profile Agent")
                    return await self._route_to_agent("onboarding", user_id, content, context, force_welcome=True)
                else:
                    # Usuário com onboarding completo - pode ir para Super Personal Trainer
                    print(f"✅ TextOrchestrator: Usuário {user_id} completou onboarding - indo para Super Personal Trainer")
                    return await self._route_to_agent("super_personal_trainer", user_id, content, context)
            
            elif intent == "saudacao":
                # Cumprimento - resposta personalizada baseada no status
                return await self._handle_greeting(user_id, content, context)
            
            elif intent == "suporte":
                # Dúvidas ou problemas
                return {
                    "agent_name": "suporte",
                    "response": """🤝 **Como posso te ajudar?**

Sou seu Super Personal Trainer e posso te auxiliar com:

🏃‍♂️ **Treino sob medida** → Sugestões de exercícios, divisão de treinos e como melhorar performance
🥗 **Alimentação ajustada** → Cardápios, ideias de refeições e ajustes na dieta para seus objetivos  
📊 **Análise corporal** → Feedback sobre evolução, composição e pontos que podemos melhorar
🍽️ **Receitas fitness** → Pratos rápidos, saudáveis e fáceis de incluir na rotina

💪 **Escolha uma opção ou me diga direto seu objetivo que eu preparo algo pra você!**"""
                }
            
            else:
                # Intent desconhecido - fallback inteligente
                return await self._handle_unknown_intent(user_id, content, context, analysis)
                
        except Exception as e:
            print(f"❌ Erro no roteamento inteligente: {e}")
            return {
                "agent_name": "error",
                "response": """🤔 **Ocorreu um erro ao processar sua solicitação.**

Mas posso te ajudar com várias coisas! Escolha uma opção ou me diga direto seu objetivo:

🏃‍♂️ **Treino sob medida** → Sugestões de exercícios, divisão de treinos e como melhorar performance
🥗 **Alimentação ajustada** → Cardápios, ideias de refeições e ajustes na dieta para seus objetivos  
📊 **Análise corporal** → Feedback sobre evolução, composição e pontos que podemos melhorar
🍽️ **Receitas fitness** → Pratos rápidos, saudáveis e fáceis de incluir na rotina

💪 **Escolha uma opção ou me diga direto seu objetivo que eu preparo algo pra você!**"""
            }
    
    async def _handle_greeting(self, user_id: str, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trata cumprimentos de forma personalizada baseada no status do usuário
        """
        try:
            long_term = context.get("long_term", {})
            onboarding_completed = long_term.get("onboarding_completed", False)
            profile = long_term.get("profile", {})
            
            if onboarding_completed:
                # Usuário com perfil completo
                name = profile.get("name", "")
                greeting_name = f", {name}" if name else ""
                
                return {
                    "agent_name": "saudacao_completa",
                    "response": f"""👋 **Olá{greeting_name}!**

Que bom te ver de volta! 😊

Como posso te ajudar hoje?
🏃‍♂️ **Treino sob medida** → Sugestões de exercícios, divisão de treinos e como melhorar performance
🥗 **Alimentação ajustada** → Cardápios, ideias de refeições e ajustes na dieta para seus objetivos  
📊 **Análise corporal** → Feedback sobre evolução, composição e pontos que podemos melhorar
🍽️ **Receitas fitness** → Pratos rápidos, saudáveis e fáceis de incluir na rotina

📸 **Ou envie fotos de:**
• 🍽️ **Pratos de comida** → Cálculo automático de calorias e nutrientes
• 📊 **Bioimpedância** → Análise completa da composição corporal

💪 **Escolha uma opção ou me diga direto seu objetivo que eu preparo algo pra você!**"""
                }
            else:
                # Usuário com perfil incompleto - redireciona para onboarding
                return await self._route_to_agent("onboarding", user_id, content, context, force_welcome=True)
                
        except Exception as e:
            return {
                "agent_name": "saudacao_error",
                "response": "Olá! Como posso te ajudar hoje?"
            }
    
    async def _handle_unknown_intent(self, user_id: str, content: str, context: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trata intents desconhecidos com fallback inteligente
        """
        try:
            reasoning = analysis.get("reasoning", "")
            confidence = analysis.get("confidence", 0.0)
            
            if confidence < 0.3:
                # Confiança muito baixa - pede esclarecimento
                return {
                    "agent_name": "clarification_needed",
                    "response": """🤔 **Não consegui entender exatamente o que você precisa.**

Mas posso te ajudar com várias coisas! Escolha uma opção ou me diga direto seu objetivo:

🏃‍♂️ **Treino sob medida** → Sugestões de exercícios, divisão de treinos e como melhorar performance
🥗 **Alimentação ajustada** → Cardápios, ideias de refeições e ajustes na dieta para seus objetivos  
📊 **Análise corporal** → Feedback sobre evolução, composição e pontos que podemos melhorar
🍽️ **Receitas fitness** → Pratos rápidos, saudáveis e fáceis de incluir na rotina

💪 **Escolha uma opção ou me diga direto seu objetivo que eu preparo algo pra você!**"""
                }
            else:
                # Confiança alta ou moderada - tenta detecção simples primeiro
                simple_intent = await self._simple_update_detection(content)
                if simple_intent:
                    print(f"🎯 TextOrchestrator: Detecção simples encontrou: {simple_intent}")
                    return await self._route_to_agent(simple_intent, user_id, content, context)
                else:
                    # Se não encontrar nada, mostra mensagem melhorada de opções
                    return {
                        "agent_name": "clarification_needed",
                        "response": """🤔 **Não consegui entender exatamente o que você precisa.**

Mas posso te ajudar com várias coisas! Escolha uma opção ou me diga direto seu objetivo:

🏃‍♂️ **Treino sob medida** → Sugestões de exercícios, divisão de treinos e como melhorar performance
🥗 **Alimentação ajustada** → Cardápios, ideias de refeições e ajustes na dieta para seus objetivos  
📊 **Análise corporal** → Feedback sobre evolução, composição e pontos que podemos melhorar
🍽️ **Receitas fitness** → Pratos rápidos, saudáveis e fáceis de incluir na rotina

💪 **Escolha uma opção ou me diga direto seu objetivo que eu preparo algo pra você!**"""
                    }
                
        except Exception as e:
            return {
                "agent_name": "fallback_error",
                "response": """🤔 **Não consegui entender sua solicitação.**

Mas posso te ajudar com várias coisas! Escolha uma opção ou me diga direto seu objetivo:

🏃‍♂️ **Treino sob medida** → Sugestões de exercícios, divisão de treinos e como melhorar performance
🥗 **Alimentação ajustada** → Cardápios, ideias de refeições e ajustes na dieta para seus objetivos  
📊 **Análise corporal** → Feedback sobre evolução, composição e pontos que podemos melhorar
🍽️ **Receitas fitness** → Pratos rápidos, saudáveis e fáceis de incluir na rotina

💪 **Escolha uma opção ou me diga direto seu objetivo que eu preparo algo pra você!**"""
            }
    
    async def _simple_update_detection(self, content: str) -> Optional[str]:
        """
        Detecção simples e robusta de intenções de atualização usando palavras-chave
        """
        try:
            content_lower = content.lower().strip()
            
            # Detecção por palavras-chave específicas
            if any(word in content_lower for word in ["atualizar", "mudar", "alterar", "trocar"]):
                if any(word in content_lower for word in ["peso", "kg", "quilos"]):
                    return "weight"
                elif any(word in content_lower for word in ["altura", "cm", "metros", "metro"]):
                    return "height"
                elif any(word in content_lower for word in ["idade", "anos", "anos de idade"]):
                    return "age"
                elif any(word in content_lower for word in ["objetivo", "meta", "goal"]):
                    return "goal"
                elif any(word in content_lower for word in ["nível", "level", "experiência", "treino"]):
                    return "training_level"
                elif any(word in content_lower for word in ["restrição", "alergia", "dieta", "alimentar"]):
                    return "restrictions"
                elif any(word in content_lower for word in ["perfil", "dados", "informações"]):
                    return "profile"
            
            # Detecção por padrões específicos - todos direcionam para Super Personal Trainer
            # MAS apenas se o usuário completou onboarding (verificação será feita no roteamento)
            if any(pattern in content_lower for pattern in [
                "quero treinar", "preciso treinar", "fazer treino", "criar treino",
                "montar treino", "montar meu treino", "criar meu treino",
                "plano de treino", "exercícios", "academia", "musculação",
                "quero dieta", "preciso dieta", "plano alimentar", "alimentação",
                "comer", "refeições", "bioimpedância", "composição corporal", 
                "percentual de gordura", "massa muscular", "análise corporal",
                "receita", "receitas", "ingredientes", "preparo", "cozinhar",
                "nutricionista", "consulta nutricional", "análise de refeição", 
                "analisar comida", "avaliar alimentação", "orientação nutricional", 
                "consulta individual", "nutrição"
            ]):
                return "super_personal_trainer"
            
            return None
            
        except Exception as e:
            print(f"❌ Erro na detecção simples: {e}")
            return None
    
    async def _detect_specific_field(self, content: str) -> Optional[str]:
        """
        Detecta qual campo específico está sendo atualizado na mensagem
        """
        try:
            content_lower = content.lower().strip()
            
            # Detecção por padrões de dados específicos
            if any(word in content_lower for word in ["kg", "quilos", "peso"]):
                return "weight"
            elif any(word in content_lower for word in ["cm", "metros", "metro", "altura"]):
                return "height"
            elif any(word in content_lower for word in ["anos", "idade"]):
                return "age"
            elif any(word in content_lower for word in ["perder peso", "emagrecer", "ganhar massa", "condicionamento", "objetivo"]):
                return "goal"
            elif any(word in content_lower for word in ["iniciante", "intermediário", "avançado", "nível"]):
                return "training_level"
            elif any(word in content_lower for word in ["vegetariano", "vegano", "lactose", "alergia", "restrição"]):
                return "restrictions"
            
            # Detecção por números com contexto
            import re
            numbers = re.findall(r'\d+', content)
            if numbers:
                # Se tem números, analisa o contexto
                if any(word in content_lower for word in ["kg", "quilos"]):
                    return "weight"
                elif any(word in content_lower for word in ["cm", "metros", "metro"]):
                    return "height"
                elif any(word in content_lower for word in ["anos", "idade"]):
                    return "age"
                elif len(content_lower) < 10:  # Mensagem curta com número
                    # Para mensagens muito curtas como "75", "180", "25"
                    # Assume que é peso se não há contexto específico
                    return "weight"
            
            return None
            
        except Exception as e:
            print(f"❌ Erro na detecção de campo específico: {e}")
            return None
    
    async def _handle_contact_sharing(self, user_id: str, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trata o compartilhamento de contato do Telegram
        """
        try:
            long_term = context.get("long_term", {})
            
            # Verifica se o usuário existe no banco
            if not long_term or not long_term.get("user_id"):
                # Usuário não cadastrado - pede para se cadastrar
                return {
                    "agent_name": "registration_required",
                    "response": """🎉 **Bem-vindo ao BodyFlow.ai!**

Sou seu assistente pessoal de fitness e nutrição. Vou te ajudar a criar um plano personalizado para alcançar seus objetivos!

Para começar, você precisa se cadastrar primeiro no nosso site. 

📱 **Acesse:** [bodyflow.ai](https://bodyflow.ai) para criar sua conta

Após o cadastro, volte aqui e eu te ajudarei a completar seu perfil personalizado com:
• Sua idade, peso e altura
• Seus objetivos de fitness
• Seu nível de treino atual
• Suas restrições alimentares

Depois disso, poderei criar planos de treino e dieta totalmente personalizados para você!

🔗 **Cadastre-se em:** bodyflow.ai"""
                }
            else:
                # Usuário cadastrado - dá boas-vindas
                onboarding_completed = long_term.get("onboarding_completed", False)
                
                if onboarding_completed:
                    # Onboarding completo - pergunta o que quer fazer
                    return {
                        "agent_name": "welcome_completed",
                        "response": """🎉 **Bem-vindo de volta ao BodyFlow!**

Agora posso te ajudar com:
🏃‍♂️ **Treinos personalizados**
🥗 **Dietas específicas** 
📊 **Análise de bioimpedância**
🍽️ **Receitas fitness**

O que você gostaria de fazer hoje?"""
                    }
                else:
                    # Onboarding incompleto - continua onboarding
                    return await self._route_to_agent("onboarding", user_id, content, context, force_welcome=True)
                    
        except Exception as e:
            return {
                "agent_name": "error",
                "response": "Desculpe, ocorreu um erro ao verificar seu acesso. Tente novamente."
            }

        except Exception:
            return False
    
    
    
    
    async def _check_if_new_user(self, context: Dict[str, Any]) -> bool:
        """
        Verifica se é um usuário novo (não existe no banco)
        """
        try:
            long_term = context.get("long_term", {})
            # Se não tem user_id, é usuário novo
            return not bool(long_term.get("user_id"))
        except Exception:
            return True  # Em caso de erro, trata como novo usuário
    
    
    async def _route_to_agent(self, intent: str, user_id: str, content: str, context: Dict[str, Any], force_welcome: bool = False, update_intent: str = None, image_data: bytes = None) -> Dict[str, Any]:
        """Roteia para agente específico baseado na intenção"""
        
        agent_mapping = {
            "onboarding": "profile_agent",
            "super_personal_trainer": "super_personal_trainer_agent",
            "image_orchestrator": "image_orchestrator"
        }
        
        agent_name = agent_mapping.get(intent, "unknown")
        
        if agent_name == "unknown":
            return {
                "agent_name": "unknown",
                "response": """🤔 **Não consegui entender sua solicitação.**

Mas posso te ajudar com várias coisas! Escolha uma opção ou me diga direto seu objetivo:

🏃‍♂️ **Treino sob medida** → Sugestões de exercícios, divisão de treinos e como melhorar performance
🥗 **Alimentação ajustada** → Cardápios, ideias de refeições e ajustes na dieta para seus objetivos  
📊 **Análise corporal** → Feedback sobre evolução, composição e pontos que podemos melhorar
🍽️ **Receitas fitness** → Pratos rápidos, saudáveis e fáceis de incluir na rotina

💪 **Escolha uma opção ou me diga direto seu objetivo que eu preparo algo pra você!**"""
            }
        
        # Importa e executa agente específico
        try:
            agent = None
            if agent_name == "profile_agent":
                from app.adk.agents.profile_agent import ProfileAgentNode
                agent = ProfileAgentNode()
            elif agent_name == "super_personal_trainer_agent":
                from app.adk.agents.super_personal_trainer_agent import SuperPersonalTrainerAgentNode
                agent = SuperPersonalTrainerAgentNode()
            elif agent_name == "image_orchestrator":
                from app.adk.image_orchestrator import ImageOrchestratorNode
                agent = ImageOrchestratorNode()
            
            # Executa agente
            if agent:
                print(f"🎯 TextOrchestrator: Executando agente {agent_name} para intent '{intent}'")
                agent_input = {
                    "user_id": user_id,
                    "content": content,
                    "context": context,
                    "intent": intent,
                    "force_welcome": force_welcome,
                    "update_intent": update_intent,
                    "image_data": image_data
                }
                
                result = await agent.process(agent_input)
                print(f"🎯 TextOrchestrator: Resultado do agente {agent_name}: {result.get('response', '')[:100]}...")
                return {
                    "agent_name": agent_name,
                    "response": result.get("response", ""),
                    "handoff": result.get("handoff", None)
                }
            else:
                print(f"❌ TextOrchestrator: Agente {agent_name} não foi inicializado")
                return {
                    "agent_name": agent_name,
                    "response": """🤔 **Desculpe, ocorreu um erro ao inicializar o agente.**

Mas posso te ajudar com várias coisas! Escolha uma opção ou me diga direto seu objetivo:

🏃‍♂️ **Treino sob medida** → Sugestões de exercícios, divisão de treinos e como melhorar performance
🥗 **Alimentação ajustada** → Cardápios, ideias de refeições e ajustes na dieta para seus objetivos  
📊 **Análise corporal** → Feedback sobre evolução, composição e pontos que podemos melhorar
🍽️ **Receitas fitness** → Pratos rápidos, saudáveis e fáceis de incluir na rotina

💪 **Escolha uma opção ou me diga direto seu objetivo que eu preparo algo pra você!**"""
                }
                
        except Exception as e:
            print(f"❌ TextOrchestrator: Erro ao processar agente {agent_name}: {e}")
            return {
                "agent_name": agent_name,
                "response": """🤔 **Desculpe, ocorreu um erro ao processar sua solicitação.**

Mas posso te ajudar com várias coisas! Escolha uma opção ou me diga direto seu objetivo:

🏃‍♂️ **Treino sob medida** → Sugestões de exercícios, divisão de treinos e como melhorar performance
🥗 **Alimentação ajustada** → Cardápios, ideias de refeições e ajustes na dieta para seus objetivos  
📊 **Análise corporal** → Feedback sobre evolução, composição e pontos que podemos melhorar
🍽️ **Receitas fitness** → Pratos rápidos, saudáveis e fáceis de incluir na rotina

💪 **Escolha uma opção ou me diga direto seu objetivo que eu preparo algo pra você!**"""
            }
    
    async def _handle_low_confidence(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Lida com baixa confiança na classificação"""
        
        fallback_message = """
Não consegui entender claramente sua solicitação. 

Você pode escolher uma das opções abaixo:

🏃‍♂️ **Treino** - Exercícios e rotinas de treino
🥗 **Dieta** - Alimentação e nutrição  
📊 **Bioimpedância** - Análise de composição corporal
🍽️ **Receitas** - Receitas fitness personalizadas
👤 **Perfil** - Atualizar dados pessoais

Qual dessas opções te interessa mais?
"""
        
        return {
            "success": True,
            "response": fallback_message,
            "agent_activated": "fallback",
            "confidence": 0.0,
            "routing_decision": {
                "intent": "fallback",
                "reason": "low_confidence",
                "threshold": 0.7
            }
        }
    
    async def _update_session_summary(self, user_id: str, intent: str, response: str) -> None:
        """Atualiza resumo da sessão"""
        try:
            summary = f"Última intenção: {intent}. Resposta: {response[:100]}..."
            await self.memory_tool.update_session_summary(user_id, summary, intent)
        except Exception:
            # Falha silenciosa
            pass
