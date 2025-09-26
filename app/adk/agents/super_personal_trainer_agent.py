"""
Agente Nutricionista para ADK - Consultas Individuais
"""

import asyncio
import time
import os
from typing import Dict, Any, Optional, List
from app.adk.simple_adk import Node
from anthropic import Anthropic
from app.tools.memory_tool import MemoryTool
from app.tools.observability_tool import ObservabilityTool
from app.tools.multimodal_tool import MultimodalTool
from app.services.session_manager import SessionManager

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
        self.anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
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
👩‍⚕️ **Consulta Nutricional Individual**

Olá! Sou sua nutricionista e estou aqui para te ajudar com orientações personalizadas sobre alimentação e estilo de vida.

Para realizar uma consulta completa e eficaz, preciso conhecer melhor você primeiro. Que tal completarmos seu perfil básico?
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
            
            # Chama Claude para gerar consulta
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.4,
                messages=[{"role": "user", "content": prompt}]
            )
            
            consultation_text = response.content[0].text
            
            return consultation_text
            
        except Exception as e:
            return f"""
👩‍⚕️ **Consulta Nutricional**

Baseado no seu perfil, aqui estão minhas orientações:

**Dados do Paciente:**
- Idade: {profile.get('age', 'N/A')} anos
- Peso: {profile.get('weight', 'N/A')} kg
- Altura: {profile.get('height', 'N/A')} cm
- Objetivo: {profile.get('goal', 'N/A')}

**Orientações Gerais:**
- Mantenha hidratação adequada (2-3L/dia)
- Consuma proteínas em todas as refeições
- Inclua fibras e micronutrientes
- Evite alimentos ultraprocessados

*Erro ao processar consulta detalhada. Tente novamente.*
"""
    
    def _build_consultation_prompt(self, content: str, profile: Dict[str, Any], short_term: List[Dict], image_data: Optional[bytes] = None, is_continuation: bool = False, context: Dict[str, Any] = None) -> str:
        """Constrói prompt para consulta nutricional"""
        
        # Dados do perfil
        age = profile.get("age", "N/A")
        weight = profile.get("weight", "N/A")
        height = profile.get("height", "N/A")
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

INSTRUÇÕES ESPECÍFICAS:
- Analise a imagem considerando o tipo "{image_class}"
- Foque nas áreas: {focus_text}
- Integre a análise com o contexto da consulta
- Seja prático e aplicável ao dia a dia
- Use frases curtas e diretas
- Use os dados da análise fornecidos acima para dar uma resposta específica
"""
        
        prompt = f"""
Você é o SUPER PERSONAL TRAINER - um agente especializado que atua como Nutrólogo, Nutricionista e Personal Trainer em uma só experiência. 
Sua missão é conduzir uma conversa natural, acolhedora e prática, como em uma consulta real. 
Você deve interagir de forma progressiva: pergunte aos poucos, comente o que o paciente disser e ofereça insights imediatos. 
Não use respostas longas demais; prefira frases curtas, listas rápidas e exemplos aplicáveis ao dia a dia.

DADOS DO PACIENTE:
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
                    macros = analysis.get('macronutrients', {})
                    
                    return f"""
- Alimentos identificados: {', '.join(food_items) if food_items else 'Não identificados'}
- Calorias estimadas: {calories} kcal
- Macronutrientes: {macros.get('protein', 0)}g proteína, {macros.get('carbs', 0)}g carboidratos, {macros.get('fat', 0)}g gordura
- Confiança da análise: {food_analysis.get('confidence', 0):.1%}
"""
            
            # Dados de bioimpedância
            elif 'bioimpedance_data' in image_context_data:
                bio_data = image_context_data['bioimpedance_data']
                return f"""
- Dados de bioimpedância: {bio_data}
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
            # Usa LLM para análise mais inteligente e flexível
            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",  # Modelo mais rápido para análise simples
                max_tokens=50,
                temperature=0.1,
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
                }]
            )
            
            result = response.content[0].text.strip().upper()
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
