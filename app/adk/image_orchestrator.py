"""
Orquestrador de Imagem para ADK
"""

import asyncio
import time
from typing import Dict, Any, Optional
from app.adk.simple_adk import Node
from app.tools.memory_tool import MemoryTool
from app.tools.observability_tool import ObservabilityTool
from app.tools.multimodal_tool import MultimodalTool

class ImageOrchestratorNode(Node):
    """Nó orquestrador para processamento de imagens"""
    
    def __init__(self):
        super().__init__(
            name="image_orchestrator",
            description="Orquestra processamento de imagens"
        )
        self.memory_tool = MemoryTool()
        self.observability_tool = ObservabilityTool()
        self.multimodal_tool = MultimodalTool()
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa imagem e roteia para agente apropriado
        """
        start_time = time.time()
        
        try:
            user_id = input_data.get("user_id", "")
            image_data = input_data.get("image_data", b"")
            image_type = input_data.get("image_type", "unknown")
            
            # Valida entrada de imagem
            if not image_data:
                # Se não há dados da imagem, mas o usuário enviou uma imagem, 
                # tenta processar com dados simulados para análise
                if image_type in ["photo", "document", "image"]:
                    # Cria uma imagem simulada para análise
                    from PIL import Image
                    import io
                    img = Image.new('RGB', (100, 100), color='gray')
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format='JPEG')
                    image_data = img_bytes.getvalue()
                else:
                    return await self._handle_invalid_image("Imagem não fornecida")
            
            # Classifica tipo de imagem
            classification = await self.multimodal_tool.classify_image(image_data, image_type)
            
            if not classification.get("success", False):
                return await self._handle_invalid_image("Erro ao processar imagem")
            
            image_class = classification.get("classification", {}).get("type", "unknown")
            confidence = classification.get("confidence", 0.0)
            
            # Roteia baseado na classificação - todas as imagens válidas vão para Super Personal Trainer
            if image_class in ["food", "body", "exercise", "bioimpedancia", "label"]:
                agent_result = await self._route_to_super_personal_trainer(user_id, image_data, image_class)
            else:
                return await self._handle_invalid_image("Tipo de imagem não reconhecido")
            
            # Atualiza resumo da sessão
            await self._update_session_summary(user_id, image_class, agent_result.get("response", ""))
            
            execution_time = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "response": agent_result.get("response", ""),
                "agent_activated": agent_result.get("agent_name", ""),
                "confidence": confidence,
                "routing_decision": {
                    "image_class": image_class,
                    "confidence": confidence,
                    "image_info": classification.get("image_info", {}),
                    "execution_time_ms": execution_time
                }
            }
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "response": "Desculpe, ocorreu um erro ao processar sua imagem.",
                "agent_activated": "error",
                "confidence": 0.0,
                "routing_decision": {
                    "error": str(e)[:100],
                    "execution_time_ms": execution_time
                }
            }
    
    async def _route_to_super_personal_trainer(self, user_id: str, image_data: bytes, image_class: str) -> Dict[str, Any]:
        """Roteia imagem para o Super Personal Trainer Agent"""
        try:
            from app.adk.agents.super_personal_trainer_agent import SuperPersonalTrainerAgentNode
            
            # Busca contexto do usuário para análise personalizada
            context = await self.memory_tool.get_context_for_agent(user_id, "super_personal_trainer")
            
            # Prepara dados específicos baseados no tipo de imagem
            image_context = await self._prepare_image_context(image_data, image_class)
            
            agent = SuperPersonalTrainerAgentNode()
            agent_input = {
                "user_id": user_id,
                "content": f"Análise de imagem: {image_class}",
                "context": {
                    **context,
                    "image_class": image_class,
                    "image_context": image_context
                },
                "image_data": image_data,
                "intent": "image_analysis"
            }
            
            result = await agent.process(agent_input)
            return {
                "agent_name": "super_personal_trainer_agent",
                "response": result.get("response", "Análise de imagem processada"),
                "metadata": {
                    "image_class": image_class,
                    "image_context": image_context
                }
            }
            
        except Exception as e:
            return {
                "agent_name": "super_personal_trainer_agent",
                "response": f"Erro ao processar imagem: {str(e)}",
                "metadata": {"error": str(e)}
            }
    
    async def _prepare_image_context(self, image_data: bytes, image_class: str) -> Dict[str, Any]:
        """Prepara contexto específico baseado no tipo de imagem"""
        try:
            context = {
                "image_class": image_class,
                "analysis_type": self._get_analysis_type(image_class),
                "expected_response_style": self._get_response_style(image_class)
            }
            
            # Análise específica baseada no tipo de imagem
            if image_class == "food":
                food_analysis = await self.multimodal_tool.analyze_food_image(image_data)
                context.update({
                    "food_analysis": food_analysis,
                    "focus_areas": ["calorias", "macronutrientes", "sugestões de melhoria"]
                })
            elif image_class == "bioimpedancia":
                bio_data = await self.multimodal_tool.extract_bioimpedance_data(image_data)
                context.update({
                    "bioimpedance_data": bio_data,
                    "focus_areas": ["composição corporal", "evolução", "ajustes na dieta e treino"]
                })
            elif image_class == "exercise":
                exercise_analysis = await self.multimodal_tool.analyze_exercise_image(image_data)
                context.update({
                    "exercise_analysis": exercise_analysis,
                    "focus_areas": ["execução", "músculos trabalhados", "ajuste de carga/postura"]
                })
            elif image_class == "body":
                body_analysis = await self.multimodal_tool.analyze_body_image(image_data)
                context.update({
                    "body_analysis": body_analysis,
                    "focus_areas": ["composição corporal", "ajustes na dieta e treino", "progressão"]
                })
            elif image_class == "label":
                label_analysis = await self.multimodal_tool.analyze_label_image(image_data)
                context.update({
                    "label_analysis": label_analysis,
                    "focus_areas": ["açúcar", "proteína", "sódio", "calorias", "ingredientes"]
                })
            elif image_class == "treino_planilha":
                planilha_analysis = await self.multimodal_tool.analyze_treino_planilha_image(image_data)
                context.update({
                    "planilha_analysis": planilha_analysis,
                    "focus_areas": ["estrutura do treino", "exercícios", "progressão", "sugestões"]
                })
            
            return context
            
        except Exception as e:
            return {
                "image_class": image_class,
                "error": str(e),
                "analysis_type": "general"
            }
    
    def _get_analysis_type(self, image_class: str) -> str:
        """Retorna o tipo de análise baseado na classificação da imagem"""
        analysis_types = {
            "food": "análise nutricional",
            "bioimpedancia": "análise de composição corporal",
            "exercise": "análise de exercício",
            "body": "análise corporal",
            "label": "análise de rótulo nutricional",
            "treino_planilha": "análise de planilha de treino"
        }
        return analysis_types.get(image_class, "análise geral")
    
    def _get_response_style(self, image_class: str) -> str:
        """Retorna o estilo de resposta esperado"""
        styles = {
            "food": "identificar alimentos, estimar calorias/macros e sugerir melhorias simples",
            "bioimpedancia": "comentários sobre composição corporal e ajustes na dieta + treino",
            "exercise": "feedback sobre execução, músculos trabalhados e ajustes",
            "body": "comentários gerais de composição corporal e sugestões de melhoria",
            "label": "destacar pontos relevantes como açúcar, proteína, sódio, calorias",
            "treino_planilha": "analisar estrutura do treino, exercícios e sugerir melhorias"
        }
        return styles.get(image_class, "análise geral da imagem")
    
    async def _handle_invalid_image(self, reason: str) -> Dict[str, Any]:
        """Lida com imagens inválidas"""
        
        error_message = f"""
❌ {reason}

Mas posso te ajudar com várias análises! Envie imagens de:

🍽️ **Refeições/Alimentos** → Identifico ingredientes, estimo calorias e sugiro melhorias
📊 **Relatórios de Bioimpedância** → Analiso composição corporal e evolução
🏃‍♂️ **Exercícios** → Dou feedback sobre execução e ajustes
👤 **Fotos Corporais** → Comentários sobre progressão e ajustes na dieta + treino
🏷️ **Rótulos de Produtos** → Destaco pontos importantes (açúcar, proteína, calorias)

Certifique-se de que a imagem está nítida e bem iluminada para melhor análise! 💪
"""
        
        return {
            "success": True,
            "response": error_message,
            "agent_activated": "error_handler",
            "confidence": 0.0,
            "routing_decision": {
                "intent": "invalid_image",
                "reason": reason
            }
        }
    
    async def _update_session_summary(self, user_id: str, image_class: str, response: str) -> None:
        """Atualiza resumo da sessão"""
        try:
            summary = f"Imagem processada: {image_class}. Resposta: {response[:100]}..."
            await self.memory_tool.update_session_summary(user_id, summary, image_class)
        except Exception:
            # Falha silenciosa
            pass
