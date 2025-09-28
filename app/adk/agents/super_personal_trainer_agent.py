"""
Agente Nutricionista para ADK - Consultas Individuais
"""

import asyncio
import time
import os
from typing import Dict, Any, Optional, List
from app.adk.simple_adk import Node
from app.tools.memory_tool import MemoryTool
from app.tools.observability_tool import ObservabilityTool
from app.tools.multimodal_tool import MultimodalTool
from app.services.session_manager import SessionManager
from app.services.llm_service import llm_service

class SuperPersonalTrainerAgentNode(Node):
    """Super Personal Trainer Agent - Agente principal responsável por saúde, nutrição e treino"""
    
    def __init__(self):
        super().__init__(
            name="super_personal_trainer_agent",
            description="Super Personal Trainer - Agente principal para saúde, nutrição e treino"
        )
        self.memory_tool = MemoryTool()
        self.observability_tool = ObservabilityTool()
        self.multimodal_tool = MultimodalTool()
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa consulta nutricional individual com persistência de sessão
        """
        start_time = time.time()
        
        try:
            user_id = input_data.get("user_id", "")
            content = input_data.get("content", "")
            context = input_data.get("context", {})
            image_data = input_data.get("image_data")
            
            # Verifica se usuário completou onboarding básico
            onboarding_check = await self._check_basic_profile(user_id, context)
            if onboarding_check.get("needs_profile"):
                return {
                    "success": True,
                    "response": onboarding_check.get("response", ""),
                    "agent_name": "super_personal_trainer_agent",
                    "handoff": {"agent": "onboarding_agent", "reason": "Perfil básico incompleto"}
                }
            
            # Se há imagem, analisa independentemente da sessão ativa
            if image_data:
                consultation_response = await self._analyze_image_directly(
                    user_id, content, context, image_data
                )
            else:
                # Verifica se está em sessão ativa de consulta nutricional
                consultation_session = await self._check_consultation_session(user_id, context)
                
                if consultation_session.get("in_session"):
                    # Continua consulta existente
                    consultation_response = await self._continue_consultation(
                        user_id, content, context, image_data, consultation_session
                    )
                else:
                    # Inicia nova consulta
                    consultation_response = await self._start_new_consultation(
                        user_id, content, context, image_data
                    )
            
            execution_time = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "response": consultation_response,
                "agent_name": "super_personal_trainer_agent",
                "persistent_session": True,  # Indica que deve manter sessão ativa
                "metadata": {
                    "consultation_type": "nutritional",
                    "multimodal_used": bool(image_data),
                    "execution_time_ms": execution_time,
                    "session_active": True
                }
            }
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "response": "Desculpe, ocorreu um erro durante a consulta. Tente novamente.",
                "agent_name": "super_personal_trainer_agent",
                "metadata": {
                    "error": str(e)[:100],
                    "execution_time_ms": execution_time
                }
            }
    
    async def _check_basic_profile(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica se usuário tem perfil básico para consulta"""
        try:
            long_term = context.get("long_term", {})
            onboarding_completed = long_term.get("onboarding_completed", False)
            
            if not onboarding_completed:
                return {
                    "needs_profile": True,
                    "response": """
🎉 **Bem-vindo ao BodyFlow.ai!**

Que bom te ter aqui! 😊

Para criar planos perfeitos e personalizados para você, vou coletar algumas informações importantes sobre seus objetivos, características físicas e preferências.

Isso me permitirá oferecer:
• Treinos sob medida para seu nível
• Dietas ajustadas aos seus objetivos  
• Receitas que combinam com seu estilo de vida
• Acompanhamento personalizado da sua evolução

📸 **Você também pode enviar fotos de:**
• 🍽️ **Pratos de comida** → Calculo automático de calorias e nutrientes
• 📊 **Bioimpedância** → Análise completa da composição corporal

Vamos começar:

**Qual sua idade?**
"""
                }
            
            return {"needs_profile": False}
            
        except Exception:
            return {"needs_profile": True, "response": "Erro ao verificar perfil."}
    
    
    async def _conduct_nutritional_consultation(self, user_id: str, content: str, context: Dict[str, Any], image_data: Optional[bytes] = None, is_continuation: bool = False) -> str:
        """Conduz consulta nutricional individual"""
        try:
            # Recupera dados do perfil
            long_term = context.get("long_term", {})
            profile = long_term.get("profile", {})
            short_term = context.get("short_term", [])
            
            # Constrói prompt para Claude
            prompt = self._build_consultation_prompt(content, profile, short_term, image_data, is_continuation, context)
            
            # Usa o serviço centralizado LiteLLM
            fallback_response = llm_service.get_contextual_fallback(content, profile.get("name", "Paciente"), profile)
            
            # Constrói contexto da conversa para manter continuidade
            conversation_context = self._build_conversation_context(short_term, profile)
            
            response = await llm_service.call_with_fallback(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.4,
                fallback_response=fallback_response,
                conversation_context=conversation_context
            )
            
            return response
            
        except Exception as e:
            print(f"❌ Erro na consulta: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback de emergência
            profile = context.get("long_term", {}).get("profile", {})
            return llm_service.get_contextual_fallback(content, profile.get("name", "Paciente"), profile)
    
    def _build_conversation_context(self, short_term: List[Dict], profile: Dict[str, Any]) -> str:
        """Constrói contexto da conversa para manter continuidade entre LLMs"""
        try:
            user_name = profile.get("name", "Paciente")
            
            # Constrói resumo da conversa recente
            conversation_summary = []
            if short_term:
                for msg in short_term[-5:]:  # Últimas 5 mensagens
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    if role == 'user':
                        conversation_summary.append(f"Paciente: {content}")
                    elif role == 'assistant':
                        conversation_summary.append(f"Nutricionista: {content}")
            
            context = f"""
CONVERSA EM ANDAMENTO COM {user_name.upper()}:

Histórico recente da conversa:
{chr(10).join(conversation_summary) if conversation_summary else "Primeira interação"}

INSTRUÇÕES:
- Esta é uma conversa contínua com {user_name}
- Mantenha o tom e estilo da conversa anterior
- Continue de onde parou, não reinicie a conversa
- Seja natural e mantenha a continuidade
"""
            return context.strip()
            
        except Exception as e:
            print(f"❌ Erro ao construir contexto da conversa: {e}")
            return f"Conversa em andamento com {profile.get('name', 'Paciente')}"
    
    def _build_consultation_prompt(self, content: str, profile: Dict[str, Any], short_term: List[Dict], image_data: Optional[bytes] = None, is_continuation: bool = False, context: Dict[str, Any] = None) -> str:
        """Constrói prompt para consulta nutricional"""
        
        # Dados do perfil
        user_name = profile.get("name", "Paciente")
        age = profile.get("age", "N/A")
        weight = profile.get("current_weight_kg", "N/A")  # Campo correto da tabela user_profile
        height = profile.get("height_cm", "N/A")  # Campo correto da tabela user_profile
        goal = profile.get("goal", "N/A")
        training_level = profile.get("training_level", "N/A")
        restrictions = profile.get("restrictions", "Nenhuma")
        
        # Contexto recente
        recent_context = ""
        if short_term:
            recent_messages = [f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in short_term[-5:]]
            recent_context = f"Contexto recente da conversa: {' | '.join(recent_messages)}"
        
        # Informações sobre imagem se presente
        image_context = ""
        if image_data:
            # Usa contexto específico preparado pelo Image Orchestrator
            image_context_data = context.get("image_context", {}) if context else {}
            
            image_class = image_context_data.get("image_class", "unknown")
            analysis_type = image_context_data.get("analysis_type", "análise geral")
            expected_style = image_context_data.get("expected_response_style", "análise geral da imagem")
            focus_areas = image_context_data.get("focus_areas", [])
            
            focus_text = ", ".join(focus_areas) if focus_areas else "análise geral"
            
            image_context = f"""
IMAGEM ENVIADA: O paciente enviou uma imagem do tipo "{image_class}".

ANÁLISE SOLICITADA: {analysis_type}
ESTILO DE RESPOSTA: {expected_style}
ÁREAS DE FOCO: {focus_text}

DADOS DA ANÁLISE DA IMAGEM:
{self._format_image_analysis_data(image_context_data)}

INSTRUÇÕES ESPECÍFICAS PARA ANÁLISE DETALHADA:
- Analise a imagem considerando o tipo "{image_class}"
- Foque nas áreas: {focus_text}
- Se a análise mostra "NÃO CONSEGUIU IDENTIFICAR", explique ao usuário que não foi possível analisar a imagem
- Se conseguiu identificar alimentos, use TODOS os dados extraídos da imagem (alimentos, calorias, range, macronutrientes, reasoning)
- Explique o significado do range de calorias e por que é conservador
- Seja específico sobre cada alimento identificado e suas contribuições nutricionais
- Considere o objetivo e nível de treino do usuário para sugestões personalizadas
- Mencione a confiança da análise e como isso afeta as recomendações
- Inclua sugestões práticas de melhoria baseadas no reasoning fornecido
- Seja transparente sobre limitações da análise quando a confiança for baixa
- Mantenha um tom profissional mas acolhedor, usando o nome do usuário
- Integre a análise com o contexto da consulta
- Seja prático e aplicável ao dia a dia
- Use os dados da análise fornecidos acima para dar uma resposta específica e detalhada
"""
        
        prompt = f"""
Você é o SUPER PERSONAL TRAINER - um agente especializado que atua como Nutrólogo, Nutricionista e Personal Trainer em uma só experiência. 
Sua missão é conduzir uma conversa natural, acolhedora e prática, como em uma consulta real. 
Você deve interagir de forma progressiva: pergunte aos poucos, comente o que o paciente disser e ofereça insights imediatos. 
Não use respostas longas demais; prefira frases curtas, listas rápidas e exemplos aplicáveis ao dia a dia.

DADOS DO PACIENTE:
- Nome: {user_name}
- Idade: {age} anos
- Peso: {weight} kg
- Altura: {height} cm
- Objetivo: {goal}
- Nível de atividade: {training_level}
- Restrições alimentares: {restrictions}

SOLICITAÇÃO DO PACIENTE: "{content}"

{recent_context}

{image_context}

{'CONTEXTO: Esta é uma CONTINUAÇÃO da consulta. Responda diretamente à pergunta/solicitação do paciente de forma curta e prática.' if is_continuation else 'CONTEXTO: Esta é uma NOVA consulta. Inicie com acolhimento breve e simpático.'}

POSTURA NA CONVERSA:
- {'Responda de forma curta e direta' if is_continuation else 'Seja empático, positivo e motivador desde o início'}
- Use o nome do paciente ({user_name}) para personalizar a conversa quando apropriado
- Não transforme a interação em um questionário. Conduza como um bate-papo natural.
- Faça perguntas curtas e contextuais, de acordo com o que o paciente falar.
- Se o paciente pedir algo específico, responda na hora, sem esperar todas as informações.
- Dê feedbacks contínuos e vá ajustando conforme coleta mais dados.

ÁREAS DE ATUAÇÃO:
- **Nutrição**: dietas, cardápios, calorias, macronutrientes, hábitos alimentares, escolhas saudáveis, intolerâncias alimentares, emagrecimento, hipertrofia, saúde metabólica.
- **Suplementação**: orientações gerais sobre suplementos comuns (ex.: whey, creatina, vitaminas), explicando quando podem ajudar. Nunca prescreva medicamentos.
- **Treinos**: sugestões de exercícios, divisões de treino, frequência, intensidade, postura e progressão. 
- **Integração**: sempre que possível, conecte alimentação e treino para dar orientações mais completas.

ESTILO DE RESPOSTA:
- Use frases curtas e diretas.
- Prefira listas de até 3 a 5 itens.
- Dê exemplos práticos que o paciente possa aplicar imediatamente.
- Use emojis moderadamente para dar leveza (ex.: 🥗💪🔥).
- Adapte o tom para ser motivador e acessível, sem jargões técnicos em excesso.

LIMITES DE ATUAÇÃO:
- Você não é médico clínico. Não prescreva remédios ou diagnósticos médicos.
- Se o tema sair totalmente do escopo de saúde, nutrição, treino ou suplementação → encerre educadamente e informe que não é da sua área.
- Se o paciente tocar em questões emocionais profundas (ex.: ansiedade, depressão), oriente de forma respeitosa que deve procurar apoio psicológico, sem tentar substituir esse papel.

CAPACIDADE MULTIMODAL:
- **Imagem de refeição**: identifique alimentos, estime calorias/macros em poucas frases e sugira melhorias simples.
- **Imagem da geladeira/dispensa**: sugira até 3 receitas rápidas e saudáveis com os itens disponíveis.
- **Imagem de rótulo**: destaque os 2–3 pontos mais relevantes (açúcar, proteína, sódio, calorias).
- **Imagem de treino/exercício**: dê feedback curto sobre execução, músculos trabalhados ou ajuste de carga/postura.
- **Imagem de corpo físico**: faça comentários gerais de composição corporal (ex.: "aparenta foco em abdômen, podemos ajustar dieta + treino para essa área"). Nunca critique de forma negativa.
- **Imagem de exames médicos**: comente apenas dentro do campo nutricional/fitness (ex.: colesterol alto → mais fibras + aeróbico). Nunca faça diagnóstico clínico.

IMPORTANTE: Quando você receber contexto de análise de imagem (seção "IMAGEM ENVIADA"), você DEVE analisar a imagem baseado nesse contexto. NÃO diga que não consegue visualizar a imagem. Use as informações fornecidas no contexto para dar uma análise específica e útil.

{image_context}

OBJETIVO:
Atuar como o SUPER PERSONAL TRAINER - um guia completo de saúde, nutrição e treino. 
Fornecer apoio integrado e contínuo, com mensagens curtas, claras e motivadoras. 
Ajudar o paciente a alcançar objetivos reais (emagrecimento, hipertrofia, energia, bem-estar, performance), sempre com orientações práticas e adaptadas à sua realidade.

Forneça uma resposta curta, prática e personalizada baseada nas informações fornecidas.
"""
        
        return prompt
    
    def _format_image_analysis_data(self, image_context_data: Dict[str, Any]) -> str:
        """Formata os dados da análise da imagem para o prompt"""
        try:
            # Dados de análise de comida
            if 'food_analysis' in image_context_data:
                food_analysis = image_context_data['food_analysis']
                if food_analysis.get('success', False):
                    analysis = food_analysis.get('analysis', {})
                    food_items = analysis.get('food_items', [])
                    calories = analysis.get('estimated_calories', 0)
                    calorie_range = analysis.get('calorie_range', {})
                    macros = analysis.get('macronutrients', {})
                    confidence = analysis.get('confidence', 0)
                    reasoning = analysis.get('reasoning', 'Não fornecido')
                    
                    # Verifica se não conseguiu identificar alimentos
                    if food_items == ['unknown'] or (len(food_items) == 1 and food_items[0] == 'unknown'):
                        return """
ANÁLISE NUTRICIONAL - NÃO CONSEGUIU IDENTIFICAR:

❌ RESULTADO DA ANÁLISE:
- Não foi possível identificar alimentos na imagem
- A imagem pode estar com baixa qualidade, muito escura ou com alimentos não reconhecíveis
- Análise nutricional não disponível

🔍 POSSÍVEIS CAUSAS:
- Imagem muito escura ou desfocada
- Alimentos não identificáveis pelo sistema
- Imagem não contém comida visível
- Qualidade da foto muito baixa

💡 SUGESTÕES:
- Tente tirar uma nova foto com melhor iluminação
- Certifique-se de que a comida está bem visível
- Evite sombras ou reflexos na imagem
- Mantenha a câmera estável e focada
"""
                    
                    # Formata lista de alimentos com detalhes
                    food_details = []
                    for item in food_items:
                        if isinstance(item, dict):
                            name = item.get('name', 'Alimento desconhecido')
                            quantity = item.get('quantity_grams', 'N/A')
                            item_calories = item.get('calories', 0)
                            food_details.append(f"• {name} ({quantity}g, {item_calories} kcal)")
                        else:
                            food_details.append(f"• {item}")
                    
                    food_list = '\n'.join(food_details) if food_details else 'Não identificados'
                    
                    # Formata range de calorias
                    calorie_range_text = ""
                    if calorie_range:
                        min_cal = calorie_range.get('min', calories)
                        max_cal = calorie_range.get('max', calories)
                        calorie_range_text = f"\n- Range de calorias: {min_cal}-{max_cal} kcal (estimativa conservadora)"
                    
                    return f"""
ANÁLISE NUTRICIONAL DETALHADA:

🍽️ ALIMENTOS IDENTIFICADOS:
{food_list}

🔥 CALORIAS:
- Estimativa principal: {calories} kcal{calorie_range_text}

🥩 MACRONUTRIENTES:
- Proteína: {macros.get('protein', 0)}g
- Carboidratos: {macros.get('carbs', 0)}g  
- Gordura: {macros.get('fat', 0)}g

📊 CONFIABILIDADE:
- Confiança da análise: {confidence:.1%}
- Método: {analysis.get('analysis_method', 'llm_analysis')}

🧠 EXPLICAÇÃO DA ANÁLISE:
{reasoning}
"""
            
            # Dados de bioimpedância
            elif 'bioimpedance_data' in image_context_data:
                bio_data = image_context_data['bioimpedance_data']
                
                if bio_data.get('success') and bio_data.get('data'):
                    data = bio_data['data']
                    
                    # Formata dados de bioimpedância
                    weight = data.get('weight_kg', 'N/A')
                    body_fat = data.get('body_fat_percent', 'N/A')
                    muscle_mass = data.get('muscle_mass_kg', 'N/A')
                    visceral_fat = data.get('visceral_fat_level', 'N/A')
                    bmr = data.get('basal_metabolic_rate', 'N/A')
                    hydration = data.get('hydration_percent', 'N/A')
                    bone_mass = data.get('bone_mass_kg', 'N/A')
                    date = data.get('date', 'N/A')
                    confidence = data.get('confidence', 0)
                    reasoning = data.get('reasoning', 'Não fornecido')
                    
                    return f"""
ANÁLISE DE COMPOSIÇÃO CORPORAL DETALHADA:

📊 DADOS PRINCIPAIS:
- Peso: {weight} kg
- Gordura corporal: {body_fat}%
- Massa muscular: {muscle_mass} kg
- Gordura visceral: {visceral_fat} (nível 1-59)

⚡ METABOLISMO:
- Taxa metabólica basal: {bmr} kcal
- Hidratação: {hydration}%
- Massa óssea: {bone_mass} kg

📅 INFORMAÇÕES:
- Data do exame: {date}
- Confiança da análise: {confidence:.1%}

🧠 EXPLICAÇÃO DA ANÁLISE:
{reasoning}
"""
                else:
                    return f"""
❌ ERRO NA ANÁLISE DE BIOIMPEDÂNCIA:
- Não foi possível extrair dados da imagem
- Erro: {bio_data.get('error', 'Desconhecido')}
- Verifique se a imagem está clara e legível
"""
            
            # Dados genéricos
            else:
                return f"""
- Tipo de análise: {image_context_data.get('analysis_type', 'análise geral')}
- Dados disponíveis: {image_context_data}
"""
                
        except Exception as e:
            return f"- Erro ao processar dados da análise: {str(e)}"
    
    async def _suggest_continuation(self, user_id: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Sugere continuidade para outros agentes"""
        try:
            long_term = context.get("long_term", {})
            goal = long_term.get("profile", {}).get("goal", "")
            
            # Sugere treino se objetivo envolve exercício
            if any(word in goal.lower() for word in ["perder", "ganhar", "condicionamento", "massa"]):
                return {
                    "agent": "super_personal_trainer_agent",
                    "reason": "Complementar orientação nutricional com treino específico"
                }
            
            return None
            
        except Exception:
            return None
    
    async def _check_consultation_session(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica se usuário está em sessão ativa de consulta nutricional"""
        try:
            # Usa o SessionManager para verificar sessão ativa
            active_session = await SessionManager.get_active_session(user_id)
            
            if active_session and active_session.get("active_agent") == "super_personal_trainer_agent":
                return {
                    "in_session": True,
                    "session_data": active_session
                }
            
            return {"in_session": False}
            
        except Exception:
            return {"in_session": False}
    
    async def _analyze_image_directly(self, user_id: str, content: str, context: Dict[str, Any], image_data: bytes) -> str:
        """Analisa imagem diretamente sem considerar sessão ativa"""
        try:
            
            # Analisa a imagem usando o contexto preparado pelo Image Orchestrator
            consultation_response = await self._conduct_nutritional_consultation(
                user_id, content, context, image_data, is_continuation=False
            )
            
            # Define sessão ativa após análise da imagem
            await self._set_active_session(user_id, "super_personal_trainer_agent")
            
            return consultation_response
            
        except Exception as e:
            print(f"❌ Erro ao analisar imagem: {e}")
            return "Desculpe, ocorreu um erro ao analisar sua imagem. Tente novamente."

    async def _start_new_consultation(self, user_id: str, content: str, context: Dict[str, Any], image_data: Optional[bytes] = None) -> str:
        """Inicia nova consulta nutricional"""
        try:
            # Marca sessão ativa no contexto
            await self._set_active_session(user_id, "super_personal_trainer_agent")
            
            # Conduz consulta inicial
            consultation_response = await self._conduct_nutritional_consultation(
                user_id, content, context, image_data, is_continuation=False
            )
            
            
            return consultation_response
            
        except Exception as e:
            return f"Erro ao iniciar consulta: {str(e)}"
    
    async def _continue_consultation(self, user_id: str, content: str, context: Dict[str, Any], image_data: Optional[bytes], session_data: Dict[str, Any]) -> str:
        """Continua consulta nutricional existente"""
        try:
            # Verifica se usuário quer sair da consulta
            exit_intent = await self._detect_exit_intent(content)
            if exit_intent:
                await self._clear_active_session(user_id)
                return """
💪 **SUPER PERSONAL TRAINER - Consulta Finalizada**

Obrigado pela consulta! Foi um prazer te ajudar com suas questões de saúde, nutrição e treino.

Se precisar de mais orientações no futuro, estarei aqui como seu Super Personal Trainer! 

Como posso te ajudar agora?
"""
            # Continua consulta normal
            consultation_response = await self._conduct_nutritional_consultation(
                user_id, content, context, image_data, is_continuation=True
            )
            
            return consultation_response
            
        except Exception as e:
            return f"Erro ao continuar consulta: {str(e)}"
    
    
    async def _detect_exit_intent(self, content: str) -> bool:
        """Detecta se usuário quer sair da consulta usando LLM"""
        try:
            # Usa LiteLLM para análise mais inteligente e flexível
            response = await llm_service.call_with_fallback(
                messages=[{
                    "role": "user", 
                    "content": f"""
Analise se o usuário quer SAIR da consulta nutricional.

Mensagem do usuário: "{content}"

Responda APENAS:
- "SAIR" se o usuário quer encerrar/finalizar a consulta
- "CONTINUAR" se quer manter a consulta

Exemplos de SAIR: despedidas, agradecimentos finais, "tchau", "obrigado", "até logo", "finalizar", "terminar consulta"
Exemplos de CONTINUAR: perguntas sobre nutrição, pedidos de ajuda, dúvidas, "quero saber", "como fazer"
"""
                }],
                max_tokens=50,
                temperature=0.1
            )
            
            result = response.strip().upper()
            return result == "SAIR"
            
        except Exception:
            # Fallback para padrões básicos em caso de erro
            exit_patterns = [
                "obrigado", "obrigada", "tchau", "até logo", "até mais",
                "finalizar", "terminar", "sair"
            ]
            content_lower = content.lower()
            return any(pattern in content_lower for pattern in exit_patterns)
    
    
    async def _set_active_session(self, user_id: str, agent_name: str):
        """Define sessão ativa no contexto"""
        try:
            # Usa o SessionManager para definir sessão ativa
            await SessionManager.set_active_session(user_id, agent_name)
            
        except Exception as e:
            print(f"Erro ao definir sessão ativa: {e}")
    
    async def _clear_active_session(self, user_id: str):
        """Limpa sessão ativa"""
        try:
            # Usa o SessionManager para limpar sessão ativa
            SessionManager.clear_active_session(user_id)
            
        except Exception as e:
            print(f"Erro ao limpar sessão ativa: {e}")
