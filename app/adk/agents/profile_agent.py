"""
Profile Agent para ADK - Gerenciamento completo de perfil do usuário
"""

import asyncio
import os
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, date
from app.adk.simple_adk import Node
from app.tools.memory_tool import MemoryTool
from app.tools.observability_tool import ObservabilityTool
from app.services.llm_service import llm_service

class ProfileAgentNode(Node):
    """Agente responsável pelo gerenciamento completo do perfil do usuário"""
    
    def __init__(self):
        super().__init__(
            name="profile_agent",
            description="Gerencia perfil do usuário, onboarding e atualizações de dados"
        )
        self.memory_tool = MemoryTool()
        self.observability_tool = ObservabilityTool()
        
        # Estados do onboarding
        self.onboarding_steps = [
            "welcome",
            "age",
            "height", 
            "weight",
            "goal",
            "training_level",
            "restrictions",
            "completion"
        ]
        
        # Campos do perfil com validações
        self.profile_fields = {
            "age": {
                "type": "integer",
                "required": True,
                "validation": lambda x: 13 <= x <= 100,
                "error_msg": "Idade deve estar entre 13 e 100 anos"
            },
            "height_cm": {
                "type": "decimal",
                "required": True,
                "validation": lambda x: 100 <= x <= 250,
                "error_msg": "Altura deve estar entre 100 e 250 cm"
            },
            "current_weight_kg": {
                "type": "decimal",
                "required": True,
                "validation": lambda x: 30 <= x <= 300,
                "error_msg": "Peso deve estar entre 30 e 300 kg"
            },
            "goal": {
                "type": "choice",
                "required": True,
                "options": ["emagrecimento", "hipertrofia", "condicionamento", "manutencao"],
                "validation": lambda x: x in ["emagrecimento", "hipertrofia", "condicionamento", "manutencao"],
                "error_msg": "Objetivo deve ser: emagrecimento, hipertrofia, condicionamento ou manutencao"
            },
            "training_level": {
                "type": "choice",
                "required": True,
                "options": ["iniciante", "intermediario", "avancado"],
                "validation": lambda x: x in ["iniciante", "intermediario", "avancado"],
                "error_msg": "Nível deve ser: iniciante, intermediario ou avancado"
            },
            "restrictions": {
                "type": "jsonb",
                "required": False,
                "validation": lambda x: isinstance(x, dict),
                "error_msg": "Restrições devem ser um objeto JSON válido"
            }
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa mensagem no contexto do gerenciamento de perfil
        """
        start_time = time.time()
        
        try:
            user_id = input_data.get("user_id", "")
            content = input_data.get("content", "")
            context = input_data.get("context", {})
            force_welcome = input_data.get("force_welcome", False)
            update_intent = input_data.get("update_intent", None)
            
            # Verifica se onboarding está completo na tabela customers
            from app.services.memory import MemoryManager
            memory_manager = MemoryManager()
            customer_result = memory_manager.supabase.table("customers").select("onboarding_completed").eq("id", user_id).execute()
            onboarding_completed = customer_result.data[0].get("onboarding_completed", False) if customer_result.data else False
            
            # SEPARAÇÃO COMPLETA: Onboarding vs Atualização
            if onboarding_completed:
                # FLUXO DE ATUALIZAÇÃO DE PERFIL - APENAS para usuários com onboarding completo
                return await self._handle_profile_update_flow(user_id, content, update_intent)
            else:
                # FLUXO DE ONBOARDING - APENAS para usuários sem onboarding completo
                return await self._handle_onboarding_flow(user_id, content, context, force_welcome)
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "response": "Erro no processo de cadastro. Tente novamente.",
                "agent_name": "profile_agent",
                "metadata": {
                    "error": str(e)[:100],
                    "execution_time_ms": execution_time
                }
            }
    
    async def _handle_onboarding_flow(self, user_id: str, content: str, context: Dict[str, Any], force_welcome: bool) -> Dict[str, Any]:
        """
        FLUXO DE ONBOARDING - Apenas para usuários que não completaram o onboarding
        """
        try:
            # Se for welcome forçado, mostra mensagem de boas-vindas
            if force_welcome:
                return await self._handle_welcome_step(user_id, content)
            
            # Processa onboarding passo a passo
            result = await self._process_onboarding_flow(user_id, content)
            
            # Se onboarding foi completado, sugere próximo agente
            if result.get("onboarding_completed"):
                result["handoff"] = await self._suggest_next_agent(user_id, context)
            
            return {
                "success": True,
                "response": result.get("response", ""),
                "agent_name": "profile_agent",
                "handoff": result.get("handoff"),
                "metadata": {
                    "current_step": result.get("current_step"),
                    "onboarding_completed": result.get("onboarding_completed", False),
                    "profile_updated": result.get("profile_updated", False)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": "Erro no processo de cadastro. Tente novamente.",
                "agent_name": "profile_agent",
                "metadata": {
                    "error": str(e)[:100]
                }
            }
    
    async def _handle_profile_update_flow(self, user_id: str, content: str, update_intent: str) -> Dict[str, Any]:
        """
        FLUXO DE ATUALIZAÇÃO DE PERFIL - Apenas para usuários que completaram o onboarding
        """
        try:
            # Busca perfil atual do usuário na tabela user_profile
            profile_data = await self._get_user_profile_from_table(user_id)
            
            # Se é uma solicitação de atualização específica
            if update_intent:
                return await self._handle_specific_update(user_id, content, update_intent, profile_data)
            
            # Detecta se o usuário quer atualizar algo específico
            detected_intent = await self._detect_update_intent(content)
            if detected_intent:
                return await self._handle_specific_update(user_id, content, detected_intent, profile_data)
            
            # Se não detectou intenção específica, mostra opções de atualização
            return await self._handle_profile_update_request(user_id, content, profile_data)
            
        except Exception as e:
            return {
                "success": False,
                "response": "Erro na atualização de perfil. Tente novamente.",
                "agent_name": "profile_agent",
                "metadata": {
                    "error": str(e)[:100]
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
            
            response = await llm_service.call_with_fallback(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20,
                temperature=0.1
            )
            
            result = response.strip().lower()
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

📸 **Dica:** Você também pode enviar fotos de:
• 🍽️ **Pratos de comida** → Cálculo automático de calorias e nutrientes
• 📊 **Bioimpedância** → Análise completa da composição corporal
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
            
            response = await llm_service.call_with_fallback(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1
            )
            
            result = response.strip()
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
            
            response = await llm_service.call_with_fallback(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1
            )
            
            result = response.strip()
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
            
            response = await llm_service.call_with_fallback(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1
            )
            
            result = response.strip()
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
            
            response = await llm_service.call_with_fallback(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.1
            )
            
            import json
            result = response.strip()
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
            
            response = await llm_service.call_with_fallback(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20,
                temperature=0.1
            )
            
            result = response.strip().lower()
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
            
            response = await llm_service.call_with_fallback(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20,
                temperature=0.1
            )
            
            result = response.strip().lower()
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
            
            response = await llm_service.call_with_fallback(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=30,
                temperature=0.1
            )
            
            result = response.strip().lower()
            
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
    
    async def _get_user_profile_from_table(self, user_id: str) -> Dict[str, Any]:
        """Busca perfil do usuário na tabela user_profile"""
        try:
            from app.services.memory import MemoryManager
            memory_manager = MemoryManager()
            result = memory_manager.supabase.table("user_profile").select("*").eq("user_id", user_id).execute()
            if result.data:
                return result.data[0]
            return {}
        except Exception as e:
            print(f"❌ Erro ao buscar perfil na tabela user_profile: {e}")
            return {}
    
    async def _update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Atualiza perfil do usuário na tabela user_profile"""
        try:
            from app.services.memory import MemoryManager
            memory_manager = MemoryManager()
            
            # Verifica se já existe registro
            existing = memory_manager.supabase.table("user_profile").select("*").eq("user_id", user_id).execute()
            
            if existing.data:
                # Atualiza registro existente
                result = memory_manager.supabase.table("user_profile").update({
                    **profile_data,
                    "updated_at": "NOW()"
                }).eq("user_id", user_id).execute()
            else:
                # Cria novo registro
                result = memory_manager.supabase.table("user_profile").insert({
                    "user_id": user_id,
                    **profile_data
                }).execute()
            
            return len(result.data) > 0
        except Exception as e:
            print(f"❌ Erro ao atualizar perfil na tabela user_profile: {e}")
            return False
    
    async def _complete_onboarding(self, user_id: str) -> None:
        """Marca onboarding como completo"""
        try:
            # user_id já é o customer_id (UUID), atualiza diretamente
            from app.services.memory import MemoryManager
            memory_manager = MemoryManager()
            result = memory_manager.supabase.table("customers").update({
                "onboarding_completed": True
            }).eq("id", user_id).execute()
            
            print(f"✅ Onboarding completado para customer_id {user_id}: {len(result.data)} registro(s) atualizado(s)")
            
        except Exception as e:
            print(f"❌ Erro ao completar onboarding: {e}")
    
    def _extract_height_value(self, content: str) -> float:
        """Extrai altura em cm de várias formas de entrada"""
        import re
        
        content = content.lower().strip()
        
        # Padrões para diferentes formas de entrada
        patterns = [
            # 1 metro e 80
            r'(\d+)\s*metro\s*e\s*(\d+)',
            # 1,80m, 1.80m
            r'(\d+)[,.](\d+)\s*m',
            # 1m80
            r'(\d+)m(\d+)',
            # 180cm, 180 cm
            r'(\d+)\s*cm',
            # 1,80, 1.80 (assume metros se < 3)
            r'^(\d+)[,.](\d+)$',
            # 180 (assume cm se >= 100)
            r'^(\d+)$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                groups = match.groups()
                
                if len(groups) == 2 and groups[1]:  # 1 metro e 80 ou 1,80m
                    meters = int(groups[0])
                    cm = int(groups[1])
                    if cm < 100:  # 1,80 -> 180cm
                        return meters * 100 + cm
                    else:  # 1 metro e 80 -> 180cm
                        return meters * 100 + cm
                elif len(groups) == 1:  # 180 ou 180cm
                    value = int(groups[0])
                    if value >= 100:  # Assume cm
                        return float(value)
                    else:  # Assume metros
                        return float(value) * 100
        
        return None
    
    def _extract_weight_value(self, content: str) -> float:
        """Extrai peso em kg de várias formas de entrada"""
        import re
        
        content = content.lower().strip()
        
        # Padrões para diferentes formas de entrada
        patterns = [
            # 75kg, 75 kg, 75kgs
            r'(\d+(?:\.\d+)?)\s*kg?s?',
            # 75 (assume kg)
            r'^(\d+(?:\.\d+)?)$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return float(match.group(1))
        
        return None
    
    async def _extract_goal_value(self, content: str) -> str:
        """Extrai objetivo usando LLM para interpretar diferentes expressões"""
        try:
            prompt = f"""
Analise a seguinte expressão do usuário sobre seu objetivo fitness e classifique em uma das categorias abaixo:

EXPRESSÃO DO USUÁRIO: "{content}"

CATEGORIAS DISPONÍVEIS:
1. "emagrecimento" - para quem quer perder peso, queimar gordura, ficar mais magro, secar, definir o corpo
2. "hipertrofia" - para quem quer ganhar massa muscular, ficar maromba, crescer, ficar forte, malhar
3. "condicionamento" - para quem quer melhorar condicionamento físico, saúde, bem-estar, resistência
4. "manutencao" - para quem quer manter o peso atual, equilibrar, não mudar muito

EXEMPLOS DE INTERPRETAÇÃO:
- "ganho de massa" → hipertrofia
- "ficar maromba" → hipertrofia  
- "ficar fininha" → emagrecimento
- "perder barriga" → emagrecimento
- "melhorar fôlego" → condicionamento
- "manter peso" → manutencao

Responda APENAS com uma das 4 categorias (emagrecimento, hipertrofia, condicionamento, manutencao) ou "null" se não conseguir classificar.
"""

            response = await llm_service.call_with_fallback(
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                max_tokens=50,
                temperature=0.1
            )
            
            result = response.strip().lower()
            
            # Valida se o resultado é uma categoria válida
            valid_goals = ["emagrecimento", "hipertrofia", "condicionamento", "manutencao"]
            if result in valid_goals:
                return result
            else:
                return None
                
        except Exception as e:
            print(f"❌ Erro ao extrair objetivo com LLM: {e}")
            return None
    
    def _extract_training_level_value(self, content: str) -> str:
        """Extrai nível de treino de várias formas de entrada"""
        content = content.lower().strip()
        
        # Mapeamento de sinônimos para níveis
        level_mapping = {
            "iniciante": ["iniciante", "começando", "novato", "primeira vez", "nunca treinei", "sou novo"],
            "intermediario": ["intermediário", "intermediario", "já treino", "tenho experiência", "meio termo"],
            "avancado": ["avançado", "avancado", "experiente", "treino há anos", "sou forte"]
        }
        
        for level, synonyms in level_mapping.items():
            for synonym in synonyms:
                if synonym in content:
                    return level
        
        return None
    
    # =====================================================
    # MÉTODOS PARA GERENCIAMENTO DE PERFIL
    # =====================================================
    
    def _is_profile_complete(self, profile_data: Dict[str, Any]) -> bool:
        """Verifica se o perfil está completo"""
        required_fields = ["age", "height_cm", "current_weight_kg", "goal", "training_level"]
        return all(profile_data.get(field) for field in required_fields)
    
    async def _handle_specific_update(self, user_id: str, content: str, update_intent: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Lida com atualizações específicas de campos do perfil"""
        try:
            # Extrai o valor do campo
            field_value = await self._extract_field_value(content, update_intent)
            
            if not field_value:
                return {
                    "response": f"Não consegui entender o valor para {update_intent}. Tente novamente.",
                    "current_step": "update_requested"
                }
            
            # Valida o valor
            validation_result = self._validate_field_value(update_intent, field_value)
            if not validation_result["valid"]:
                return {
                    "response": f"❌ {validation_result['error']}",
                    "current_step": "update_requested"
                }
            
            # Atualiza o perfil
            updated_profile = {**profile_data, update_intent: field_value}
            success = await self._update_user_profile(user_id, updated_profile)
            
            if success:
                return {
                    "response": f"✅ {update_intent.replace('_', ' ').title()} atualizado para: **{field_value}**",
                    "profile_updated": True,
                    "profile_data": updated_profile,
                    "current_step": "update_completed"
                }
            else:
                return {
                    "response": f"❌ Erro ao atualizar {update_intent}. Tente novamente.",
                    "current_step": "update_requested"
                }
                
        except Exception as e:
            return {
                "response": f"❌ Erro ao processar atualização: {str(e)[:100]}",
                "current_step": "update_requested"
            }
    
    async def _handle_profile_update_request(self, user_id: str, content: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Lida com solicitações de atualização de perfil de usuários já cadastrados"""
        try:
            # Detecta qual campo o usuário quer atualizar
            update_intent = await self._detect_update_intent(content)
            
            if update_intent:
                return await self._handle_specific_update(user_id, content, update_intent, profile_data)
            
            # Se não detectou intenção específica, mostra opções
            return {
                "response": f"""
👤 **Atualização de Perfil**

Seu perfil atual:
• Idade: {profile_data.get('age', 'N/A')} anos
• Altura: {profile_data.get('height_cm', 'N/A')} cm
• Peso: {profile_data.get('current_weight_kg', 'N/A')} kg
• Objetivo: {profile_data.get('goal', 'N/A')}
• Nível: {profile_data.get('training_level', 'N/A')}

Para atualizar, digite:
• "Atualizar peso" ou "Mudar peso"
• "Atualizar objetivo" ou "Mudar objetivo"
• etc.

Ou digite diretamente o novo valor, como "80 kg" para peso.
""",
                "current_step": "update_options"
            }
            
        except Exception as e:
            return {
                "response": f"❌ Erro ao processar solicitação: {str(e)[:100]}",
                "current_step": "update_requested"
            }
    
    
    async def _process_onboarding_flow(self, user_id: str, content: str) -> Dict[str, Any]:
        """Processa fluxo de onboarding"""
        try:
            # Busca perfil atual do usuário na tabela user_profile
            profile_data = await self._get_user_profile_from_table(user_id)
            
            # Determina próximo passo
            next_step = self._get_next_onboarding_step(profile_data)
            
            if next_step == "welcome":
                return await self._handle_welcome_step(user_id, content)
            elif next_step == "age":
                return await self._handle_age_step(user_id, content, profile_data)
            elif next_step == "height":
                return await self._handle_height_step(user_id, content, profile_data)
            elif next_step == "weight":
                return await self._handle_weight_step(user_id, content, profile_data)
            elif next_step == "goal":
                return await self._handle_goal_step(user_id, content, profile_data)
            elif next_step == "training_level":
                return await self._handle_training_level_step(user_id, content, profile_data)
            elif next_step == "restrictions":
                return await self._handle_restrictions_step(user_id, content, profile_data)
            elif next_step == "completion":
                return await self._handle_completion_step(user_id, content, profile_data)
            else:
                return await self._handle_welcome_step(user_id, content)
                
        except Exception as e:
            return {
                "response": f"Erro no fluxo de onboarding: {str(e)[:100]}",
                "current_step": "error"
            }
    
    def _get_next_onboarding_step(self, profile_data: Dict[str, Any]) -> str:
        """Determina o próximo passo do onboarding"""
        # Pula welcome, vai direto para age
        if not profile_data.get("age"):
            return "age"
        elif not profile_data.get("height_cm"):
            return "height"
        elif not profile_data.get("current_weight_kg"):
            return "weight"
        elif not profile_data.get("goal"):
            return "goal"
        elif not profile_data.get("training_level"):
            return "training_level"
        elif not profile_data.get("restrictions"):
            return "restrictions"
        else:
            return "completion"
    
    async def _extract_field_value(self, content: str, field_name: str) -> Any:
        """Extrai valor de um campo específico da mensagem do usuário"""
        try:
            if field_name == "age":
                # Extrai número da mensagem
                import re
                numbers = re.findall(r'\d+', content)
                return int(numbers[0]) if numbers else None
            elif field_name == "height_cm":
                return self._extract_height_value(content)
            elif field_name == "current_weight_kg":
                return self._extract_weight_value(content)
            elif field_name == "goal":
                return await self._extract_goal_value(content)
            elif field_name == "training_level":
                return self._extract_training_level_value(content)
            elif field_name == "restrictions":
                return await self._extract_restrictions(content)
            else:
                return content.strip()
                
        except Exception:
            return None
    
    def _validate_field_value(self, field_name: str, value: Any) -> Dict[str, Any]:
        """Valida valor de um campo"""
        try:
            field_config = self.profile_fields.get(field_name, {})
            
            if not field_config:
                return {"valid": False, "error": f"Campo {field_name} não encontrado"}
            
            # Validação básica
            if field_config.get("required") and not value:
                return {"valid": False, "error": f"{field_name} é obrigatório"}
            
            # Validação específica
            validation_func = field_config.get("validation")
            if validation_func and not validation_func(value):
                return {"valid": False, "error": field_config.get("error_msg", f"Valor inválido para {field_name}")}
            
            return {"valid": True, "error": None}
            
        except Exception as e:
            return {"valid": False, "error": f"Erro na validação: {str(e)}"}
    
    async def _detect_update_intent(self, content: str) -> Optional[str]:
        """Detecta intenção de atualização de campo específico"""
        try:
            content_lower = content.lower()
            
            # Mapeamento de palavras-chave para campos
            field_mappings = {
                "idade": "age",
                "age": "age",
                "altura": "height_cm",
                "height": "height_cm",
                "peso": "current_weight_kg",
                "weight": "current_weight_kg",
                "objetivo": "goal",
                "goal": "goal",
                "nível": "training_level",
                "level": "training_level",
                "treino": "training_level",
                "restrições": "restrictions",
                "restrictions": "restrictions"
            }
            
            # Palavras que indicam atualização
            update_keywords = ["atualizar", "mudar", "alterar", "update", "change", "modify"]
            
            # Verifica se há intenção de atualização
            has_update_intent = any(keyword in content_lower for keyword in update_keywords)
            
            if has_update_intent:
                # Procura por campo específico
                for keyword, field in field_mappings.items():
                    if keyword in content_lower:
                        return field
            
            # Se não há palavras de atualização, mas há um valor específico, tenta detectar
            if not has_update_intent:
                # Detecta por padrões de valor (apenas com unidades explícitas)
                import re
                
                # Peso (ex: "80 kg", "80kg") - com unidade
                if re.search(r'\d+(?:\.\d+)?\s*kg', content_lower):
                    return "current_weight_kg"
                
                # Altura (ex: "175 cm", "175cm") - com unidade
                if re.search(r'\d+(?:\.\d+)?\s*cm', content_lower):
                    return "height_cm"
                
                # Idade (ex: "30 anos") - apenas com palavra "anos"
                if re.search(r'\d+\s*anos?', content_lower):
                    return "age"
            
            return None
            
        except Exception:
            return None
    
    # =====================================================
    # MÉTODOS DE ONBOARDING ESPECÍFICOS
    # =====================================================
    
    async def _handle_welcome_step(self, user_id: str, content: str) -> Dict[str, Any]:
        """Lida com o passo de boas-vindas"""
        return {
            "response": """
🎉 **Bem-vindo ao BodyFlow.ai!**

Que bom te ter aqui! 

Para criar planos perfeitos e personalizados para você, vou coletar algumas informações importantes sobre seus objetivos, características físicas e preferências.

Isso me permitirá oferecer:
• Treinos sob medida para seu nível
• Dietas ajustadas aos seus objetivos  
• Receitas que combinam com seu estilo de vida
• Acompanhamento personalizado da sua evolução

Vamos começar:

**Qual sua idade?**
""",
            "current_step": "age",
            "profile_updated": False
        }
    
    
    async def _handle_age_step(self, user_id: str, content: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Lida com coleta da idade"""
        try:
            import re
            numbers = re.findall(r'\d+', content)
            if not numbers:
                return {
                    "response": """
🎉 **Bem-vindo ao BodyFlow.ai!**

Que bom te ter aqui! 

Para criar planos perfeitos e personalizados para você, vou coletar algumas informações importantes sobre seus objetivos, características físicas e preferências.

Isso me permitirá oferecer:
• Treinos sob medida para seu nível
• Dietas ajustadas aos seus objetivos  
• Receitas que combinam com seu estilo de vida
• Acompanhamento personalizado da sua evolução

Vamos começar:

**Qual sua idade?**
""",
                    "current_step": "age",
                    "profile_updated": False
                }
            
            age = int(numbers[0])
            if not (13 <= age <= 100):
                return {
                    "response": "Idade deve estar entre 13 e 100 anos. Tente novamente:",
                    "current_step": "age",
                    "profile_updated": False
                }
            
            updated_profile = {**profile_data, "age": age}
            success = await self._update_user_profile(user_id, updated_profile)
            
            if success:
                return {
                    "response": f"✅ Idade salva: **{age} anos**\n\n**Qual sua altura?**",
                    "current_step": "height",
                    "profile_updated": True,
                    "profile_data": updated_profile
                }
            else:
                return {
                    "response": "Erro ao salvar idade. Tente novamente:",
                    "current_step": "age",
                    "profile_updated": False
                }
                
        except Exception:
            return {
                "response": "Por favor, digite sua idade:",
                "current_step": "age",
                "profile_updated": False
            }
    
    async def _handle_height_step(self, user_id: str, content: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Lida com coleta da altura"""
        try:
            height_cm = self._extract_height_value(content)
            
            if height_cm is None:
                return {
                    "response": "Por favor, digite sua altura:",
                    "current_step": "height",
                    "profile_updated": False
                }
            
            if not (100 <= height_cm <= 250):
                return {
                    "response": "Altura deve estar entre 100 e 250 cm. Tente novamente:",
                    "current_step": "height",
                    "profile_updated": False
                }
            
            updated_profile = {**profile_data, "height_cm": height_cm}
            success = await self._update_user_profile(user_id, updated_profile)
            
            if success:
                return {
                    "response": f"✅ Altura salva: **{height_cm} cm**\n\n**Qual seu peso?**",
                    "current_step": "weight",
                    "profile_updated": True,
                    "profile_data": updated_profile
                }
            else:
                return {
                    "response": "Erro ao salvar altura. Tente novamente:",
                    "current_step": "height",
                    "profile_updated": False
                }
                
        except Exception:
            return {
                "response": "Por favor, digite sua altura:",
                "current_step": "height",
                "profile_updated": False
            }
    
    async def _handle_weight_step(self, user_id: str, content: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Lida com coleta do peso"""
        try:
            weight_kg = self._extract_weight_value(content)
            
            if weight_kg is None:
                return {
                    "response": "Por favor, digite seu peso:",
                    "current_step": "weight",
                    "profile_updated": False
                }
            
            if not (30 <= weight_kg <= 300):
                return {
                    "response": "Peso deve estar entre 30 e 300 kg. Tente novamente:",
                    "current_step": "weight",
                    "profile_updated": False
                }
            
            updated_profile = {**profile_data, "current_weight_kg": weight_kg}
            success = await self._update_user_profile(user_id, updated_profile)
            
            if success:
                return {
                    "response": f"✅ Peso salvo: **{weight_kg} kg**\n\n**Qual seu objetivo principal?**\n\n• Emagrecimento\n• Hipertrofia\n• Condicionamento\n• Manutenção",
                    "current_step": "goal",
                    "profile_updated": True,
                    "profile_data": updated_profile
                }
            else:
                return {
                    "response": "Erro ao salvar peso. Tente novamente:",
                    "current_step": "weight",
                    "profile_updated": False
                }
                
        except Exception:
            return {
                "response": "Por favor, digite seu peso:",
                "current_step": "weight",
                "profile_updated": False
            }
    
    async def _handle_goal_step(self, user_id: str, content: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Lida com coleta do objetivo"""
        goal = await self._extract_goal_value(content)
        
        if not goal or goal not in ["emagrecimento", "hipertrofia", "condicionamento", "manutencao"]:
            return {
                "response": "Por favor, escolha um objetivo válido:\n\n• Emagrecimento\n• Hipertrofia\n• Condicionamento\n• Manutenção",
                "current_step": "goal",
                "profile_updated": False
            }
        
        updated_profile = {**profile_data, "goal": goal}
        success = await self._update_user_profile(user_id, updated_profile)
        
        if success:
            return {
                "response": f"✅ Objetivo salvo: **{goal}**\n\n**Qual seu nível de treino?**\n\n• Iniciante\n• Intermediário\n• Avançado",
                "current_step": "training_level",
                "profile_updated": True,
                "profile_data": updated_profile
            }
        else:
            return {
                "response": "Erro ao salvar objetivo. Tente novamente:",
                "current_step": "goal",
                "profile_updated": False
            }
    
    async def _handle_training_level_step(self, user_id: str, content: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Lida com coleta do nível de treino"""
        training_level = self._extract_training_level_value(content)
        
        if not training_level or training_level not in ["iniciante", "intermediario", "avancado"]:
            return {
                "response": "Por favor, escolha um nível válido:\n\n• Iniciante\n• Intermediário\n• Avançado",
                "current_step": "training_level",
                "profile_updated": False
            }
        
        updated_profile = {**profile_data, "training_level": training_level}
        success = await self._update_user_profile(user_id, updated_profile)
        
        if success:
            return {
                "response": f"✅ Nível salvo: **{training_level}**\n\n**Tem alguma restrição alimentar ou de saúde?**",
                "current_step": "restrictions",
                "profile_updated": True,
                "profile_data": updated_profile
            }
        else:
            return {
                "response": "Erro ao salvar nível. Tente novamente:",
                "current_step": "training_level",
                "profile_updated": False
            }
    
    async def _handle_restrictions_step(self, user_id: str, content: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Lida com coleta de restrições"""
        restrictions = await self._extract_restrictions(content)
        
        if restrictions == "null" or restrictions in ["nenhuma", "não", "nao", "none"]:
            restrictions = {}
        
        updated_profile = {**profile_data, "restrictions": restrictions}
        success = await self._update_user_profile(user_id, updated_profile)
        
        if success:
            # Marca onboarding como completo no banco de dados
            await self._complete_onboarding(user_id)
            
            return {
                "response": f"✅ Restrições salvas: **{restrictions if restrictions else 'Nenhuma'}**\n\n**Perfil completo!** 🎉\n\n🤝 **Como posso te ajudar?**\n\nPosso te auxiliar com:\n\n🏃‍♂️ **Treino sob medida** → Sugestões de exercícios, divisão de treinos e como melhorar performance\n🥗 **Alimentação ajustada** → Cardápios, ideias de refeições e ajustes na dieta para seus objetivos  \n📊 **Análise corporal** → Feedback sobre evolução, composição e pontos que podemos melhorar\n🍽️ **Receitas fitness** → Pratos rápidos, saudáveis e fáceis de incluir na rotina\n\n💪 **Escolha uma opção ou me diga direto seu objetivo que eu preparo algo pra você!**",
                "current_step": "completion",
                "profile_updated": True,
                "profile_data": updated_profile,
                "onboarding_completed": True
            }
        else:
            return {
                "response": "❌ Erro ao salvar restrições. Tente novamente:",
                "current_step": "restrictions",
                "profile_updated": False
            }
    
    async def _handle_completion_step(self, user_id: str, content: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Lida com conclusão do onboarding"""
        return {
            "response": """
🎉 **Perfil criado com sucesso!**

Agora você pode acessar todos os serviços do BodyFlow:

🏃‍♂️ **Treino sob medida** → Sugestões de exercícios, divisão de treinos e como melhorar performance
🥗 **Alimentação ajustada** → Cardápios, ideias de refeições e ajustes na dieta para seus objetivos
📊 **Análise corporal** → Feedback sobre evolução, composição e pontos que podemos melhorar
🍽️ **Receitas fitness** → Pratos rápidos, saudáveis e fáceis de incluir na rotina

💪 Escolha uma opção ou me diga direto seu objetivo que eu preparo algo pra você.
""",
            "current_step": "completed",
            "profile_updated": False,
            "onboarding_completed": True
        }
    
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
