"""
Agente de Onboarding para ADK
"""

import asyncio
import os
import time
from typing import Dict, Any, Optional, List
from app.adk.simple_adk import Node
from anthropic import Anthropic
from app.tools.memory_tool import MemoryTool
from app.tools.observability_tool import ObservabilityTool

class OnboardingAgentNode(Node):
    """Agente responsável pelo onboarding de usuários"""
    
    def __init__(self):
        super().__init__(
            name="onboarding_agent",
            description="Conduz processo de onboarding e coleta de dados essenciais"
        )
        self.memory_tool = MemoryTool()
        self.observability_tool = ObservabilityTool()
        self.anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Estados do onboarding
        self.onboarding_steps = [
            "welcome",
            "age",
            "weight",
            "height", 
            "goal",
            "training_level",
            "restrictions",
            "completion"
        ]
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa mensagem no contexto do onboarding
        """
        start_time = time.time()
        
        try:
            user_id = input_data.get("user_id", "")
            content = input_data.get("content", "")
            context = input_data.get("context", {})
            force_welcome = input_data.get("force_welcome", False)
            update_intent = input_data.get("update_intent", None)
            
            print(f"🎯 OnboardingAgent: processando mensagem '{content}' com update_intent='{update_intent}'")
            
            # Se há intenção de atualização específica, trata isso primeiro
            if update_intent:
                return await self._handle_profile_update(user_id, content, context, update_intent)
            
            # Recupera estado atual do onboarding
            current_state = await self._get_current_onboarding_state(user_id)
            current_profile = current_state.get("data", {})
            
            # Se for welcome forçado, mostra mensagem de boas-vindas
            if force_welcome:
                result = await self._handle_welcome_step_with_bodyflow_greeting(user_id, content, current_profile)
            else:
                # Detecta se o usuário quer alterar o objetivo especificamente
                goal = await self._extract_goal(content)
                if goal and current_profile.get("goal"):
                    # Usuário quer alterar objetivo
                    updated_profile = {**current_profile, "goal": goal}
                    result = {
                        "response": f"✅ Objetivo atualizado para: **{goal}**\n\nVamos continuar com o próximo passo:",
                        "current_step": "training_level",
                        "profile_updated": True,
                        "profile_data": updated_profile
                    }
                else:
                    # Processa resposta do usuário normalmente
                    result = await self._process_onboarding_step(user_id, content, current_state, context)
            
            # Atualiza perfil se necessário
            if result.get("profile_updated"):
                await self._update_user_profile(user_id, result.get("profile_data", {}))
            
            # Verifica se onboarding foi completado
            if result.get("onboarding_completed"):
                await self._complete_onboarding(user_id)
                result["handoff"] = await self._suggest_next_agent(user_id, context)
            
            execution_time = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "response": result.get("response", ""),
                "agent_name": "onboarding_agent",
                "handoff": result.get("handoff"),
                "metadata": {
                    "current_step": result.get("current_step"),
                    "onboarding_completed": result.get("onboarding_completed", False),
                    "execution_time_ms": execution_time
                }
            }
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "response": "Erro no processo de cadastro. Tente novamente.",
                "agent_name": "onboarding_agent",
                "metadata": {
                    "error": str(e)[:100],
                    "execution_time_ms": execution_time
                }
            }
    
    async def _handle_profile_update(self, user_id: str, content: str, context: Dict[str, Any], update_intent: str) -> Dict[str, Any]:
        """
        Lida com atualizações específicas do perfil
        """
        try:
            print(f"🔄 OnboardingAgent: Tratando atualização de '{update_intent}'")
            
            # Trata atualização geral de perfil
            if update_intent == "profile":
                return await self._show_profile_and_options(user_id, context)
            
            # Extrai o novo valor usando os métodos específicos
            new_value = None
            if update_intent == "goal":
                new_value = await self._extract_goal(content)
            elif update_intent == "age":
                new_value = await self._extract_age(content)
            elif update_intent == "weight":
                new_value = await self._extract_weight(content)
            elif update_intent == "height":
                new_value = await self._extract_height(content)
            elif update_intent == "training_level":
                new_value = await self._extract_training_level(content)
            elif update_intent == "restrictions":
                new_value = await self._extract_restrictions(content)
            
            if new_value is not None:
                # Atualiza o perfil
                long_term = context.get("long_term", {})
                current_profile = long_term.get("profile", {})
                updated_profile = {**current_profile, update_intent: new_value}
                
                # Salva no banco
                await self.memory_tool.update_long_term_profile(user_id, updated_profile)
                
                # Confirma atualização
                field_names = {
                    "goal": "objetivo",
                    "age": "idade", 
                    "weight": "peso",
                    "height": "altura",
                    "training_level": "nível de treino",
                    "restrictions": "restrições"
                }
                
                field_name = field_names.get(update_intent, update_intent)
                
                return {
                    "response": f"✅ **{field_name.title()} atualizado para: {new_value}**\n\nComo posso ajudar você hoje?",
                    "profile_updated": True
                }
            else:
                # Quando não consegue extrair valor, pede informação específica
                return await self._ask_for_specific_field_value(update_intent)
                
        except Exception as e:
            print(f"❌ Erro na atualização de perfil: {e}")
            return {
                "response": "Ocorreu um erro ao atualizar seus dados. Tente novamente."
            }
    
    async def _show_profile_and_options(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mostra o perfil atual e opções de atualização
        """
        try:
            long_term = context.get("long_term", {})
            current_profile = long_term.get("profile", {})
            
            # Mostra o perfil atual
            profile_info = []
            
            if current_profile.get('age'):
                profile_info.append(f"• **Idade:** {current_profile['age']} anos")
            if current_profile.get('weight'):
                profile_info.append(f"• **Peso:** {current_profile['weight']} kg")
            if current_profile.get('height'):
                profile_info.append(f"• **Altura:** {current_profile['height']} cm")
            if current_profile.get('goal'):
                profile_info.append(f"• **Objetivo:** {current_profile['goal']}")
            if current_profile.get('training_level'):
                profile_info.append(f"• **Nível de treino:** {current_profile['training_level']}")
            if current_profile.get('restrictions'):
                profile_info.append(f"• **Restrições:** {current_profile['restrictions']}")
            
            profile_text = "\n".join(profile_info) if profile_info else "Nenhuma informação encontrada"
            
            return {
                "response": f"""📋 **Seu Perfil Atual**

{profile_text}

🔄 **Para atualizar alguma informação, me diga qual campo você quer alterar:**

• **Idade:** "tenho 25 anos" ou "idade 30"
• **Peso:** "peso 75 kg" ou "agora peso 80"
• **Altura:** "altura 175 cm" ou "tenho 1,80"
• **Objetivo:** "quero perder peso" ou "objetivo ganhar massa"
• **Nível:** "sou iniciante" ou "nível intermediário"
• **Restrições:** "não como carne" ou "sem lactose"

Ou você pode dizer "atualizar [campo específico]" como "atualizar peso"."""
            }
            
        except Exception as e:
            return {
                "response": "Ocorreu um erro ao mostrar seu perfil. Tente novamente."
            }
    
    async def _ask_for_specific_field_value(self, field: str) -> Dict[str, Any]:
        """
        Pede valor específico para um campo
        """
        field_messages = {
            "weight": """📏 **Atualizar Peso**

Para atualizar seu peso, me diga qual é seu peso atual.""",
            
            "age": """🎂 **Atualizar Idade**

Para atualizar sua idade, me diga quantos anos você tem.""",
            
            "height": """📐 **Atualizar Altura**

Para atualizar sua altura, me diga qual é sua altura.""",
            
            "goal": """🎯 **Atualizar Objetivo**

Para atualizar seu objetivo, me diga qual é seu novo objetivo.""",
            
            "training_level": """🏋️ **Atualizar Nível de Treino**

Para atualizar seu nível de treino, me diga qual é seu nível atual.""",
            
            "restrictions": """🚫 **Atualizar Restrições**

Para atualizar suas restrições alimentares, me diga quais são."""
        }
        
        return {
            "response": field_messages.get(field, f"Hmm, não consegui entender sua {field}. Pode ser mais específico?")
        }
    
    async def _detect_intent_to_change(self, content: str, current_profile: Dict[str, Any]) -> Optional[str]:
        """Detecta se o usuário quer alterar uma informação específica"""
        try:
            prompt = f"""
Você é um assistente inteligente que entende quando usuários querem atualizar informações de forma natural.

MENSAGEM: "{content}"

PERFIL ATUAL:
- Idade: {current_profile.get('age', 'não informado')}
- Peso: {current_profile.get('weight', 'não informado')} kg
- Altura: {current_profile.get('height', 'não informado')} cm
- Objetivo: {current_profile.get('goal', 'não informado')}
- Nível de treino: {current_profile.get('training_level', 'não informado')}
- Restrições: {current_profile.get('restrictions', 'não informado')}

ENTENDA A INTENÇÃO REAL:
O usuário quer alterar alguma informação específica? Seja inteligente e contextual:

• Se mencionar dados específicos → retorne o campo correspondente
• Se não mencionar nada específico → retorne "null"
• Se for conversa geral → retorne "null"

EXEMPLOS DE INTERPRETAÇÃO NATURAL:
- "quero ganhar massa" → "goal" (mudança de objetivo)
- "tenho 25 anos" → "age" (informação de idade)
- "peso 80 kg" → "weight" (informação de peso)
- "sou iniciante" → "training_level" (nível de experiência)
- "não como carne" → "restrictions" (restrição alimentar)
- "oi" → "null" (saudação)
- "não sei" → "null" (incerteza)

Seja inteligente: entenda o contexto e a intenção real por trás das palavras.

Resposta (apenas o campo ou "null"):
"""
            
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=20,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text.strip().lower()
            valid_fields = ["age", "weight", "height", "goal", "training_level", "restrictions"]
            
            if result in valid_fields:
                return result
            return None
            
        except Exception:
            return None
    
    async def _get_current_onboarding_state(self, user_id: str) -> Dict[str, Any]:
        """Recupera estado atual do onboarding"""
        try:
            profile = await self.memory_tool.get_long_term_profile(user_id)
            
            # Determina passo atual baseado nos dados coletados
            if not profile:
                return {"step": "welcome", "data": {}}
            elif "age" not in profile:
                return {"step": "age", "data": profile}
            elif "weight" not in profile:
                return {"step": "weight", "data": profile}
            elif "height" not in profile:
                return {"step": "height", "data": profile}
            elif "goal" not in profile:
                return {"step": "goal", "data": profile}
            elif "training_level" not in profile:
                return {"step": "training_level", "data": profile}
            elif "restrictions" not in profile:
                return {"step": "restrictions", "data": profile}
            else:
                return {"step": "completion", "data": profile}
                
        except Exception:
            return {"step": "welcome", "data": {}}
    
    async def _process_onboarding_step(self, user_id: str, content: str, current_state: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Processa passo específico do onboarding"""
        
        step = current_state.get("step", "welcome")
        existing_data = current_state.get("data", {})
        
        if step == "welcome":
            return await self._handle_welcome_step(user_id, content, existing_data)
        elif step == "age":
            return await self._handle_age_step(user_id, content, existing_data)
        elif step == "weight":
            return await self._handle_weight_step(user_id, content, existing_data)
        elif step == "height":
            return await self._handle_height_step(user_id, content, existing_data)
        elif step == "goal":
            return await self._handle_goal_step(user_id, content, existing_data)
        elif step == "training_level":
            return await self._handle_training_level_step(user_id, content, existing_data)
        elif step == "restrictions":
            return await self._handle_restrictions_step(user_id, content, existing_data)
        elif step == "completion":
            return await self._handle_completion_step(user_id, content, existing_data)
        else:
            return {
                "response": "Erro no processo de cadastro. Vamos recomeçar.",
                "current_step": "welcome",
                "profile_updated": False
            }
    
    async def _handle_welcome_step_with_bodyflow_greeting(self, user_id: str, content: str, existing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Lida com passo de boas-vindas com mensagem especial do BodyFlow.ai"""
        
        # Usuário já foi validado pelo serviço de validação, pode começar onboarding
        return await self._handle_welcome_step(user_id, content, existing_data)
    
    async def _check_user_exists_in_database(self, user_id: str) -> bool:
        """Verifica se o usuário existe no banco de dados"""
        try:
            from app.services.memory import memory_manager
            user = await memory_manager.get_user_by_phone(user_id)
            return user is not None
        except Exception:
            return False
    
    async def _handle_welcome_step(self, user_id: str, content: str, existing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Lida com passo de boas-vindas"""
        
        # Se já tem dados salvos, mostra mensagem de continuidade
        if existing_data:
            continuation_message = f"""
👋 **Bem-vindo de volta ao BodyFlow!**

Vejo que você já começou a criar seu perfil personalizado. Vamos continuar de onde paramos!

📊 **Dados já coletados:**
{self._format_existing_data(existing_data)}

Vamos continuar com as próximas informações:
"""
            
            # Determina próximo passo baseado nos dados existentes
            if "age" not in existing_data:
                next_step = "age"
                next_question = "**Qual sua idade?**"
            elif "weight" not in existing_data:
                next_step = "weight"
                next_question = "**Qual seu peso atual?**"
            elif "height" not in existing_data:
                next_step = "height"
                next_question = "**Qual sua altura?**"
            elif "goal" not in existing_data:
                next_step = "goal"
                next_question = "**Qual seu objetivo principal com fitness e saúde?**"
            elif "training_level" not in existing_data:
                next_step = "training_level"
                next_question = "**Como você descreveria seu nível atual de atividade física?**"
            elif "restrictions" not in existing_data:
                next_step = "restrictions"
                next_question = "**Tem alguma restrição alimentar ou alergia que devo considerar?**"
            else:
                next_step = "completion"
                next_question = "Perfeito! Vamos finalizar seu perfil."
            
            return {
                "response": continuation_message + next_question,
                "current_step": next_step,
                "profile_updated": False
            }
        else:
            # Primeira vez - mensagem de boas-vindas completa
            welcome_message = """
👋 **Bem-vindo ao BodyFlow!**

Vou te ajudar a criar seu perfil personalizado para treinos e dietas.

Vamos começar com algumas informações básicas:

**Qual sua idade?**
"""
            
            return {
                "response": welcome_message,
                "current_step": "age",
                "profile_updated": False
            }
    
    def _format_existing_data(self, data: Dict[str, Any]) -> str:
        """Formata dados existentes para exibição"""
        formatted = []
        
        if "age" in data:
            formatted.append(f"• **Idade:** {data['age']} anos")
        if "weight" in data:
            formatted.append(f"• **Peso:** {data['weight']} kg")
        if "height" in data:
            formatted.append(f"• **Altura:** {data['height']} cm")
        if "goal" in data:
            formatted.append(f"• **Objetivo:** {data['goal']}")
        if "training_level" in data:
            formatted.append(f"• **Nível de treino:** {data['training_level']}")
        if "restrictions" in data:
            formatted.append(f"• **Restrições:** {data['restrictions']}")
        
        return "\n".join(formatted) if formatted else "Nenhum dado coletado ainda."
    
    async def _handle_age_step(self, user_id: str, content: str, existing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Lida com coleta de idade"""
        
        # Extrai idade da mensagem usando LLM
        age = await self._extract_age(content)
        
        if age and 13 <= age <= 100:
            profile_data = {**existing_data, "age": age}
            
            next_message = f"""
✅ Idade registrada: {age} anos

Agora preciso do seu **peso**:

**Qual seu peso atual?**
"""
            
            return {
                "response": next_message,
                "current_step": "weight",
                "profile_updated": True,
                "profile_data": profile_data
            }
        else:
            return {
                "response": "Não consegui entender sua idade. Pode me dizer quantos anos você tem?",
                "current_step": "age",
                "profile_updated": False
            }
    
    async def _handle_weight_step(self, user_id: str, content: str, existing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Lida com coleta de peso"""
        
        # Extrai peso da mensagem usando LLM
        weight = await self._extract_weight(content)
        
        if weight and 30 <= weight <= 200:
            profile_data = {**existing_data, "weight": weight}
            
            next_message = f"""
✅ Peso registrado: {weight} kg

Agora preciso da sua **altura**:

**Qual sua altura?**
"""
            
            return {
                "response": next_message,
                "current_step": "height",
                "profile_updated": True,
                "profile_data": profile_data
            }
        else:
            return {
                "response": "Não consegui entender seu peso. Pode me dizer quanto você pesa?",
                "current_step": "weight",
                "profile_updated": False
            }
    
    async def _handle_height_step(self, user_id: str, content: str, existing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Lida com coleta de altura"""
        
        # Extrai altura da mensagem usando LLM
        height = await self._extract_height(content)
        
        if height and 100 <= height <= 250:
            profile_data = {**existing_data, "height": height}
            
            next_message = f"""
✅ Altura registrada: {height} cm

Agora me conte: **Qual seu principal objetivo?**

🏃‍♂️ Perder peso
💪 Ganhar massa muscular  
🏃‍♀️ Melhorar condicionamento físico
⚖️ Manter peso atual
📊 Reduzir percentual de gordura
"""
            
            return {
                "response": next_message,
                "current_step": "goal",
                "profile_updated": True,
                "profile_data": profile_data
            }
        else:
            return {
                "response": "Não consegui entender sua altura. Pode me dizer qual sua altura?",
                "current_step": "height",
                "profile_updated": False
            }
    
    async def _handle_weight_height_step(self, user_id: str, content: str, existing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Lida com coleta de peso e altura"""
        
        # Extrai peso e altura usando LLM
        measurements = await self._extract_weight_height(content)
        
        profile_data = {**existing_data}
        
        if measurements.get("weight"):
            profile_data["weight"] = measurements["weight"]
        if measurements.get("height"):
            profile_data["height"] = measurements["height"]
        
        # Verifica se ambos foram coletados
        if profile_data.get("weight") and profile_data.get("height"):
            next_message = f"""
✅ Dados registrados:
- Peso: {profile_data['weight']} kg
- Altura: {profile_data['height']} cm

Agora me conte: **Qual seu principal objetivo?**

🏃‍♂️ Perder peso
💪 Ganhar massa muscular  
🏃‍♀️ Melhorar condicionamento físico
⚖️ Manter peso atual
📊 Reduzir percentual de gordura
"""
            
            return {
                "response": next_message,
                "current_step": "goal",
                "profile_updated": True,
                "profile_data": profile_data
            }
        else:
            missing = []
            if not profile_data.get("weight"):
                missing.append("peso")
            if not profile_data.get("height"):
                missing.append("altura")
            
            return {
                "response": f"Ops, não consegui entender. Pode me dizer seu {', '.join(missing)}?",
                "current_step": "weight_height",
                "profile_updated": True,
                "profile_data": profile_data
            }
    
    async def _handle_goal_step(self, user_id: str, content: str, existing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Lida com coleta de objetivo"""
        
        goal = await self._extract_goal(content)
        
        if goal:
            profile_data = {**existing_data, "goal": goal}
            
            next_message = f"""
✅ Objetivo registrado: {goal}

Agora preciso saber seu **nível de treino atual**:

🟢 **Iniciante** - Pouco ou nenhum exercício
🟡 **Intermediário** - Exercício regular há alguns meses
🔴 **Avançado** - Treino intenso há mais de 1 ano

Qual melhor descreve você?
"""
            
            return {
                "response": next_message,
                "current_step": "training_level",
                "profile_updated": True,
                "profile_data": profile_data
            }
        else:
            return {
                "response": "Por favor, escolha um dos objetivos listados ou descreva seu objetivo.",
                "current_step": "goal",
                "profile_updated": False
            }
    
    async def _handle_training_level_step(self, user_id: str, content: str, existing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Lida com coleta de nível de treino"""
        
        training_level = await self._extract_training_level(content)
        
        if training_level:
            profile_data = {**existing_data, "training_level": training_level}
            
            next_message = f"""
✅ Nível de treino registrado: {training_level}

Por último, tem alguma **restrição ou limitação**?

🚫 Lesões ou dores
🚫 Alergias alimentares
🚫 Restrições médicas
🚫 Preferências alimentares
✅ Nenhuma restrição

Descreva suas limitações ou digite "nenhuma".
"""
            
            return {
                "response": next_message,
                "current_step": "restrictions",
                "profile_updated": True,
                "profile_data": profile_data
            }
        else:
            return {
                "response": "Por favor, escolha seu nível de treino atual.",
                "current_step": "training_level",
                "profile_updated": False
            }
    
    async def _handle_restrictions_step(self, user_id: str, content: str, existing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Lida com coleta de restrições"""
        
        restrictions = await self._extract_restrictions(content)
        
        profile_data = {**existing_data, "restrictions": restrictions}
        
        return {
            "response": await self._generate_completion_message(profile_data),
            "current_step": "completion",
            "profile_updated": True,
            "profile_data": profile_data,
            "onboarding_completed": True
        }
    
    async def _handle_completion_step(self, user_id: str, content: str, existing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Lida com passo de conclusão"""
        
        return {
            "response": "Seu perfil já está completo! Como posso ajudar você hoje?",
            "current_step": "completion",
            "profile_updated": False,
            "onboarding_completed": True
        }
    
    async def _extract_age(self, content: str) -> Optional[int]:
        """Extrai idade da mensagem usando LLM"""
        try:
            prompt = f"""
Você é um assistente inteligente especializado em interpretar informações pessoais de forma contextual e natural.

MENSAGEM: "{content}"

ANÁLISE INTELIGENTE:
Identifique se o usuário está fornecendo sua idade. Seja contextualmente inteligente:

• Analise o contexto completo da mensagem
• Procure por números que façam sentido como idade (13-100 anos)
• Entenda variações naturais de linguagem: diretas, com contexto, informais
• Distinga entre idade e outras medidas corporais (peso, altura, etc.)
• Considere o tom e intenção da mensagem
• Se não há idade clara ou é ambíguo, retorne "null"

INTERPRETAÇÃO CONTEXTUAL:
Seja inteligente na interpretação. Entenda a intenção real por trás das palavras, considerando:
- Contexto da conversa
- Padrões naturais de linguagem
- Diferenças entre medidas corporais
- Intenção comunicativa do usuário

Resposta (apenas número ou "null"):
"""
            
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=10,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text.strip()
            if result.lower() != "null" and result.isdigit():
                age = int(result)
                if 13 <= age <= 100:
                    return age
            return None
            
        except Exception:
            return None
    
    async def _extract_weight(self, content: str) -> Optional[int]:
        """Extrai peso da mensagem usando LLM"""
        try:
            prompt = f"""
Você é um assistente inteligente especializado em interpretar informações corporais de forma contextual e natural.

MENSAGEM: "{content}"

ANÁLISE INTELIGENTE:
Identifique se o usuário está fornecendo seu peso. Seja contextualmente inteligente:

• Analise o contexto completo da mensagem
• Procure por números que façam sentido como peso (30-200 kg)
• Entenda variações naturais de linguagem: diretas, com contexto, informais
• Distinga entre peso e outras medidas corporais (idade, altura, etc.)
• Considere o tom e intenção da mensagem
• Se não há peso claro ou é ambíguo, retorne "null"

INTERPRETAÇÃO CONTEXTUAL:
Seja inteligente na interpretação. Entenda a intenção real por trás das palavras, considerando:
- Contexto da conversa
- Padrões naturais de linguagem
- Diferenças entre medidas corporais
- Intenção comunicativa do usuário

Resposta (apenas número ou "null"):
"""
            
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=10,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text.strip()
            if result.lower() != "null" and result.isdigit():
                weight = int(result)
                if 30 <= weight <= 200:
                    return weight
            return None
        except Exception:
            return None
    
    async def _extract_height(self, content: str) -> Optional[int]:
        """Extrai altura da mensagem usando LLM"""
        try:
            prompt = f"""
Você é um assistente inteligente especializado em interpretar informações corporais de forma contextual e natural.

MENSAGEM: "{content}"

ANÁLISE INTELIGENTE:
Identifique se o usuário está fornecendo sua altura. Seja contextualmente inteligente:

• Analise o contexto completo da mensagem
• Procure por números que façam sentido como altura (100-250 cm)
• Entenda variações naturais de linguagem: diretas, com contexto, informais
• Distinga entre altura e outras medidas corporais (idade, peso, etc.)
• Considere o tom e intenção da mensagem
• Se não há altura clara ou é ambíguo, retorne "null"

INTERPRETAÇÃO CONTEXTUAL:
Seja inteligente na interpretação. Entenda a intenção real por trás das palavras, considerando:
- Contexto da conversa
- Padrões naturais de linguagem
- Diferenças entre medidas corporais
- Intenção comunicativa do usuário

Resposta (apenas número ou "null"):
"""
            
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=10,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text.strip()
            if result.lower() != "null" and result.isdigit():
                height = int(result)
                if 100 <= height <= 250:
                    return height
            return None
        except Exception:
            return None
    
    async def _extract_weight_height(self, content: str) -> Dict[str, Any]:
        """Extrai peso e altura da mensagem"""
        try:
            prompt = f"""
Extraia peso e altura da seguinte mensagem. Retorne apenas JSON com "weight" e "height" em números.

Mensagem: "{content}"

Resposta (JSON apenas):
"""
            
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=50,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            import json
            result = response.content[0].text.strip()
            if "{" in result and "}" in result:
                json_start = result.find("{")
                json_end = result.rfind("}") + 1
                json_str = result[json_start:json_end]
                return json.loads(json_str)
            return {}
            
        except Exception:
            return {}
    
    async def _extract_goal(self, content: str) -> Optional[str]:
        """Extrai objetivo da mensagem usando LLM"""
        try:
            prompt = f"""
Você é um assistente inteligente especializado em interpretar objetivos de fitness de forma contextual e natural.

MENSAGEM: "{content}"

ANÁLISE INTELIGENTE:
Identifique o objetivo real do usuário com fitness e saúde. Seja contextualmente inteligente:

• Analise o contexto completo da mensagem
• Entenda variações naturais de linguagem e sinônimos
• Considere o tom e intenção da mensagem
• Se não há objetivo claro ou é ambíguo, retorne "null"

OBJETIVOS DISPONÍVEIS:
• "perder peso" - emagrecer, queimar gordura, perder quilos, ficar mais magro
• "ganhar massa" - hipertrofia, ficar mais forte, ganhar músculos, massa muscular
• "condicionamento" - resistência, cardio, condicionamento físico, endurance
• "manter peso" - estabilizar, manter o peso atual, não mudar
• "reduzir gordura" - definir músculos, secar, reduzir percentual de gordura

INTERPRETAÇÃO CONTEXTUAL:
Seja inteligente na interpretação. Entenda a intenção real por trás das palavras, considerando:
- Contexto da conversa
- Padrões naturais de linguagem
- Sinônimos e variações de expressão
- Intenção comunicativa do usuário

Resposta (apenas o objetivo ou "null"):
"""
            
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=20,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text.strip().lower()
            valid_goals = ["perder peso", "ganhar massa", "condicionamento", "manter peso", "reduzir gordura"]
            
            if result in valid_goals:
                return result
            return None
            
        except Exception:
            return None
    
    async def _extract_training_level(self, content: str) -> Optional[str]:
        """Extrai nível de treino da mensagem usando LLM"""
        try:
            prompt = f"""
Você é um assistente inteligente especializado em interpretar níveis de experiência em fitness de forma contextual e natural.

MENSAGEM: "{content}"

ANÁLISE INTELIGENTE:
Identifique o nível real de experiência do usuário com treino e atividade física. Seja contextualmente inteligente:

• Analise o contexto completo da mensagem
• Entenda variações naturais de linguagem e sinônimos
• Considere o tom e intenção da mensagem
• Se não há nível claro ou é ambíguo, retorne "null"

NÍVEIS DISPONÍVEIS:
• "iniciante" - nunca treinou, começando agora, pouca experiência (até 6 meses)
• "intermediário" - já treina há algum tempo, experiência moderada (6 meses a 2 anos)
• "avançado" - treina há muito tempo, muita experiência (mais de 2 anos)

INTERPRETAÇÃO CONTEXTUAL:
Seja inteligente na interpretação. Entenda a intenção real por trás das palavras, considerando:
- Contexto da conversa
- Padrões naturais de linguagem
- Sinônimos e variações de expressão
- Intenção comunicativa do usuário

Resposta (apenas o nível ou "null"):
"""
            
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=20,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text.strip().lower()
            valid_levels = ["iniciante", "intermediário", "intermediario", "avançado", "avancado"]
            
            if result in valid_levels:
                # Normaliza para formato padrão
                if result in ["intermediário", "intermediario"]:
                    return "intermediário"
                elif result in ["avançado", "avancado"]:
                    return "avançado"
                return result
            return None
            
        except Exception:
            return None
    
    async def _extract_restrictions(self, content: str) -> Optional[str]:
        """Extrai restrições da mensagem usando LLM"""
        try:
            prompt = f"""
Você é um assistente inteligente especializado em interpretar restrições alimentares e de saúde de forma contextual e natural.

MENSAGEM: "{content}"

ANÁLISE INTELIGENTE:
Identifique se o usuário está fornecendo informações sobre restrições alimentares ou de saúde. Seja contextualmente inteligente:

• Analise o contexto completo da mensagem
• Entenda variações naturais de linguagem e sinônimos
• Considere o tom e intenção da mensagem
• Se não há restrições claras ou é ambíguo, retorne "null"

INTERPRETAÇÃO CONTEXTUAL:
Seja inteligente na interpretação. Entenda a intenção real por trás das palavras, considerando:
- Contexto da conversa
- Padrões naturais de linguagem
- Sinônimos e variações de expressão
- Intenção comunicativa do usuário

Resposta (apenas a restrição, "nenhuma" ou "null"):
"""
            
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=30,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text.strip().lower()
            
            if result == "null":
                return None
            elif result == "nenhuma":
                return "nenhuma"
            else:
                return result
                
        except Exception:
            return None
    
    async def _generate_completion_message(self, profile_data: Dict[str, Any]) -> str:
        """Gera mensagem de conclusão do onboarding"""
        
        return f"""
🎉 **Perfil criado com sucesso!**

📋 **Seus dados:**
- Idade: {profile_data.get('age', 'N/A')} anos
- Peso: {profile_data.get('weight', 'N/A')} kg  
- Altura: {profile_data.get('height', 'N/A')} cm
- Objetivo: {profile_data.get('goal', 'N/A')}
- Nível: {profile_data.get('training_level', 'N/A')}
- Restrições: {profile_data.get('restrictions', 'N/A')}

Agora posso te ajudar com:
🏃‍♂️ **Treino sob medida** → Sugestões de exercícios, divisão de treinos e como melhorar performance
🥗 **Alimentação ajustada** → Cardápios, ideias de refeições e ajustes na dieta para seus objetivos  
📊 **Análise corporal** → Feedback sobre evolução, composição e pontos que podemos melhorar
🍽️ **Receitas fitness** → Pratos rápidos, saudáveis e fáceis de incluir na rotina

💪 **Escolha uma opção ou me diga direto seu objetivo que eu preparo algo pra você!**
"""
    
    async def _update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> None:
        """Atualiza perfil do usuário"""
        try:
            await self.memory_tool.update_long_term_profile(user_id, profile_data)
        except Exception:
            pass
    
    async def _complete_onboarding(self, user_id: str) -> None:
        """Marca onboarding como completo"""
        try:
            # Normaliza o user_id para consistência
            normalized_user_id = self.memory_tool.memory_manager._normalize_phone_for_search(user_id)
            
            # Atualiza o perfil com onboarding_completed = True
            await self.memory_tool.update_long_term_profile(normalized_user_id, {"onboarding_completed": True})
            
            # Atualiza também o campo onboarding_completed diretamente na tabela customers
            result = self.memory_tool.memory_manager.supabase.table("customers").update({
                "onboarding_completed": True
            }).eq("whatsapp", normalized_user_id).execute()
            
            print(f"✅ Onboarding completado para {normalized_user_id}: {len(result.data)} registro(s) atualizado(s)")
            
        except Exception as e:
            print(f"❌ Erro ao completar onboarding: {e}")
    
    async def _suggest_next_agent(self, user_id: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Sugere próximo agente baseado no perfil"""
        try:
            long_term = context.get("long_term", {})
            goal = long_term.get("profile", {}).get("goal", "")
            
            if "perder" in goal.lower() or "emagrecer" in goal.lower():
                return {"agent": "super_personal_trainer_agent", "reason": "Objetivo de perda de peso"}
            elif "ganhar" in goal.lower() or "massa" in goal.lower():
                return {"agent": "super_personal_trainer_agent", "reason": "Objetivo de ganho de massa"}
            else:
                return {"agent": "super_personal_trainer_agent", "reason": "Iniciar com orientação geral"}
                
        except Exception:
            return None
