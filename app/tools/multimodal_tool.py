"""
Tool Multimodal para ADK (placeholder para análise de imagens)
"""

import asyncio
from typing import Dict, Any, Optional
from app.adk.simple_adk import Tool
from PIL import Image
import io
import base64
from app.services.llm_service import llm_service

class MultimodalTool(Tool):
    """Tool multimodal para análise de imagens"""
    
    def __init__(self):
        super().__init__(
            name="multimodal_tool",
            description="Analisa imagens para classificação e extração de dados"
        )
    
    async def execute(self, *args, **kwargs):
        """Implementação do método abstrato execute"""
        return {"success": True, "message": "Multimodal tool executed"}
    
    async def classify_image(self, image_data: bytes, image_type: str = "unknown") -> Dict[str, Any]:
        """
        Classifica tipo de imagem (bioimpedância, alimentos, etc.)
        """
        try:
            # Placeholder: análise básica da imagem
            image = Image.open(io.BytesIO(image_data))
            
            # Análise básica de dimensões e formato
            width, height = image.size
            format_type = image.format
            
            # Placeholder para classificação real
            classification = await self._placeholder_classify(image, image_type)
            
            return {
                "success": True,
                "classification": classification,
                "image_info": {
                    "width": width,
                    "height": height,
                    "format": format_type,
                    "size_bytes": len(image_data)
                },
                "confidence": classification.get("confidence", 0.5)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)[:100],
                "classification": {"type": "unknown", "confidence": 0.0}
            }
    
    async def extract_bioimpedance_data(self, image_data: bytes) -> Dict[str, Any]:
        """
        Extrai dados de relatório de bioimpedância usando LLM
        """
        try:
            print(f"📊 MultimodalTool: Iniciando análise de bioimpedância...")
            print(f"📊 Tamanho da imagem: {len(image_data)} bytes")
            
            # Converte imagem para base64 para envio ao LLM
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            print(f"🔄 MultimodalTool: Imagem convertida para base64 ({len(image_base64)} caracteres)")
            
            # Analisa usando LLM
            analysis = await self._analyze_bioimpedance_with_llm(image_base64)
            
            print(f"✅ MultimodalTool: Análise de bioimpedância finalizada com sucesso!")
            print(f"📋 Resultado final: {analysis}")
            
            return {
                "success": True,
                "data": analysis,
                "confidence": analysis.get("confidence", 0.5)
            }
            
        except Exception as e:
            print(f"❌ Erro na extração de bioimpedância: {e}")
            return {
                "success": False,
                "error": str(e)[:100],
                "data": {}
            }
    
    async def analyze_food_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Analisa imagem de alimentos usando LLM
        """
        try:
            print(f"🍽️ MultimodalTool: Iniciando análise de imagem de comida...")
            print(f"📊 Tamanho da imagem: {len(image_data)} bytes")
            
            # Converte imagem para base64 para envio ao LLM
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            print(f"🔄 MultimodalTool: Imagem convertida para base64 ({len(image_base64)} caracteres)")
            
            # Analisa usando LLM da Anthropic
            analysis = await self._analyze_food_with_llm(image_base64)
            
            print(f"✅ MultimodalTool: Análise de comida finalizada com sucesso!")
            print(f"📋 Resultado final: {analysis}")
            
            return {
                "success": True,
                "analysis": analysis,
                "confidence": analysis.get("confidence", 0.7)
            }
            
        except Exception as e:
            # Fallback para placeholder se houver erro
            print(f"❌ Erro na análise real, usando placeholder: {e}")
            analysis = await self._placeholder_analyze_food(image_data)
            return {
                "success": True,
                "analysis": analysis,
                "confidence": analysis.get("confidence", 0.5)
            }
    
    async def analyze_exercise_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Analisa imagem de exercícios usando LLM
        """
        try:
            print(f"💪 MultimodalTool: Iniciando análise de imagem de exercício...")
            print(f"📊 Tamanho da imagem: {len(image_data)} bytes")
            
            # Converte imagem para base64 para envio ao LLM
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            print(f"🔄 MultimodalTool: Imagem convertida para base64 ({len(image_base64)} caracteres)")
            
            # Analisa usando LLM
            analysis = await self._analyze_exercise_with_llm(image_base64)
            
            print(f"✅ MultimodalTool: Análise de exercício finalizada com sucesso!")
            print(f"📋 Resultado final: {analysis}")
            
            return {
                "success": True,
                "analysis": analysis,
                "confidence": analysis.get("confidence", 0.7)
            }
            
        except Exception as e:
            print(f"❌ Erro na análise de exercício: {e}")
            return {
                "success": False,
                "error": str(e)[:100],
                "analysis": {}
            }
    
    async def analyze_body_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Analisa imagem corporal usando LLM
        """
        try:
            print(f"👤 MultimodalTool: Iniciando análise de imagem corporal...")
            print(f"📊 Tamanho da imagem: {len(image_data)} bytes")
            
            # Converte imagem para base64 para envio ao LLM
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            print(f"🔄 MultimodalTool: Imagem convertida para base64 ({len(image_base64)} caracteres)")
            
            # Analisa usando LLM
            analysis = await self._analyze_body_with_llm(image_base64)
            
            print(f"✅ MultimodalTool: Análise corporal finalizada com sucesso!")
            print(f"📋 Resultado final: {analysis}")
            
            return {
                "success": True,
                "analysis": analysis,
                "confidence": analysis.get("confidence", 0.7)
            }
            
        except Exception as e:
            print(f"❌ Erro na análise corporal: {e}")
            return {
                "success": False,
                "error": str(e)[:100],
                "analysis": {}
            }
    
    async def analyze_label_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Analisa imagem de rótulo nutricional usando LLM
        """
        try:
            print(f"🏷️ MultimodalTool: Iniciando análise de rótulo nutricional...")
            print(f"📊 Tamanho da imagem: {len(image_data)} bytes")
            
            # Converte imagem para base64 para envio ao LLM
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            print(f"🔄 MultimodalTool: Imagem convertida para base64 ({len(image_base64)} caracteres)")
            
            # Analisa usando LLM
            analysis = await self._analyze_label_with_llm(image_base64)
            
            print(f"✅ MultimodalTool: Análise de rótulo finalizada com sucesso!")
            print(f"📋 Resultado final: {analysis}")
            
            return {
                "success": True,
                "analysis": analysis,
                "confidence": analysis.get("confidence", 0.7)
            }
            
        except Exception as e:
            print(f"❌ Erro na análise de rótulo: {e}")
            return {
                "success": False,
                "error": str(e)[:100],
                "analysis": {}
            }
    
    async def analyze_treino_planilha_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Analisa imagem de planilha de treino usando LLM
        """
        try:
            print(f"📋 MultimodalTool: Iniciando análise de planilha de treino...")
            print(f"📊 Tamanho da imagem: {len(image_data)} bytes")
            
            # Converte imagem para base64 para envio ao LLM
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            print(f"🔄 MultimodalTool: Imagem convertida para base64 ({len(image_base64)} caracteres)")
            
            # Analisa usando LLM
            analysis = await self._analyze_treino_planilha_with_llm(image_base64)
            
            print(f"✅ MultimodalTool: Análise de planilha finalizada com sucesso!")
            print(f"📋 Resultado final: {analysis}")
            
            return {
                "success": True,
                "analysis": analysis,
                "confidence": analysis.get("confidence", 0.7)
            }
            
        except Exception as e:
            print(f"❌ Erro na análise de planilha: {e}")
            return {
                "success": False,
                "error": str(e)[:100],
                "analysis": {}
            }
    
    async def _placeholder_classify(self, image: Image.Image, image_type: str) -> Dict[str, Any]:
        """
        Classificação robusta de imagem usando LLM
        """
        try:
            # Converte imagem para base64 para análise com LLM
            import base64
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='JPEG', quality=85)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            
            # Prompt robusto para classificação
            prompt = f"""
Você é um especialista em análise visual de imagens relacionadas à nutrição, treino e saúde.
Sua tarefa é identificar o conteúdo principal da imagem e classificá-la em exatamente uma das categorias abaixo:
	•	food → comida, pratos, refeições, ingredientes ou alimentos (mesmo que apareçam mãos, pés, mesas ou outros elementos secundários).
	•	bioimpedancia → relatórios ou gráficos de composição corporal, tabelas médicas de percentual de gordura, massa magra, etc.
	•	exercise → pessoas realizando exercícios físicos, academias ou equipamentos de treino em uso.
	•	body → fotos corporais ou selfies de pessoas, desde que não haja comida nem prática de exercício.
	•	label → rótulos de produtos, informações nutricionais, tabelas de ingredientes impressas em embalagens.
	•	treino_planilha → planilhas, tabelas ou listas de treino (em papel, foto de caderno, print digital ou aplicativo).

Regras de Classificação
	1.	Se houver qualquer presença de comida/alimento → classifique como food.
	2.	Se for relatório de composição corporal → bioimpedancia.
	3.	Se mostrar pessoa treinando ou equipamento de treino → exercise.
	4.	Se for uma foto de corpo/selfie sem comida → body.
	5.	Se for rótulo ou tabela nutricional → label.
	6.	Se for planilha ou tabela de treino (mesmo manuscrita ou digital) → treino_planilha.

Saída esperada

Responda apenas com a categoria final:
food, bioimpedancia, exercise, body, label, ou treino_planilha.

⸻

RESPONDA APENAS COM JSON:
{{
    "type": "categoria_principal",
    "confidence": 0.8,
    "reasoning": "explicação_breve"
}}
"""
            
            # Usa LLM para classificação robusta
            response = await llm_service.call_with_fallback(
                messages=[
                    {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                        ]
                    }
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            # Extrai JSON da resposta
            import json
            try:
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0]
                elif "```" in response:
                    response = response.split("```")[1].split("```")[0]
                
                classification = json.loads(response.strip())
                return classification
                
            except json.JSONDecodeError:
                # Fallback se não conseguir parsear JSON
                return {"type": "food", "confidence": 0.6, "reasoning": "LLM response parse error"}
                
        except Exception as e:
            print(f"❌ Erro na classificação LLM: {e}")
            # Fallback para classificação básica
            width, height = image.size
            aspect_ratio = width / height
            
            if image_type == "bioimpedancia":
                return {"type": "bioimpedancia", "confidence": 0.8}
            elif image_type == "food":
                return {"type": "food", "confidence": 0.7}
            elif image_type == "exercise":
                return {"type": "exercise", "confidence": 0.6}
            elif image_type == "body":
                return {"type": "body", "confidence": 0.6}
            elif image_type == "label":
                return {"type": "label", "confidence": 0.7}
            else:
                # Classificação baseada em características da imagem
                if aspect_ratio > 1.5:  # Muito horizontal (pode ser relatório)
                    return {"type": "bioimpedancia", "confidence": 0.5}
                elif aspect_ratio < 0.8:  # Muito vertical (pode ser pessoa)
                    return {"type": "body", "confidence": 0.4}
                else:  # Quadrado ou pouco horizontal/vertical
                    return {"type": "food", "confidence": 0.4}
    
    async def _analyze_bioimpedance_with_llm(self, image_base64: str) -> Dict[str, Any]:
        """
        Analisa imagem de relatório de bioimpedância usando LiteLLM
        """
        try:
            prompt = """
Analise cuidadosamente a **imagem de relatório de bioimpedância** e extraia todos os dados visíveis.

**Regras obrigatórias para a análise**:
1. Identifique todos os valores numéricos relacionados à composição corporal.
2. Use os valores exatos mostrados na imagem quando possível.
3. Se um valor não estiver visível ou legível, use "unknown" e faça estimativa conservadora.
4. Sempre inclua um campo `"confidence"` entre 0.0 e 1.0 para indicar o grau de confiança da análise.
5. Retorne **apenas** um JSON válido (nenhum texto fora do JSON).
6. Inclua o campo `"analysis_method": "llm_analysis"` fixo.
7. Inclua o campo `"reasoning"` com explicação detalhada da análise realizada.

**CAMPOS OBRIGATÓRIOS PARA EXTRAIR**:
- `weight_kg`: Peso corporal em kg
- `body_fat_percent`: Percentual de gordura corporal
- `muscle_mass_kg`: Massa muscular em kg
- `visceral_fat_level`: Nível de gordura visceral (1-59)
- `basal_metabolic_rate`: Taxa metabólica basal em kcal
- `hydration_percent`: Percentual de hidratação
- `bone_mass_kg`: Massa óssea em kg
- `date`: Data do exame (formato DD/MM/YYYY)

**IMPORTANTE - FORMATO JSON OBRIGATÓRIO**:
- Use apenas aspas duplas (")
- NUNCA use vírgulas finais após o último item de arrays ou objetos
- Todos os números devem ser números, não strings
- Certifique-se de que o JSON está bem formado
- Evite caracteres especiais ou quebras de linha dentro de strings
- SEMPRE termine com } (chave de fechamento)
- SEMPRE termine arrays com ] (colchete de fechamento)
- Exemplo de estrutura correta:

```json
{
  "weight_kg": 70.5,
  "body_fat_percent": 15.2,
  "muscle_mass_kg": 58.3,
  "visceral_fat_level": 8,
  "basal_metabolic_rate": 1650,
  "hydration_percent": 60.1,
  "bone_mass_kg": 2.8,
  "date": "15/12/2024",
  "confidence": 0.8,
  "analysis_method": "llm_analysis",
  "reasoning": "Identifiquei claramente todos os valores principais do relatório de bioimpedância"
}
```

**ESTRATÉGIA DE ESTIMATIVA CONSERVADORA**:
- **Peso**: Se não conseguir ler, estime baseado no contexto visual
- **Gordura corporal**: Se não conseguir ler, use estimativa conservadora baseada no visual
- **Massa muscular**: Se não conseguir ler, estime baseado no peso e gordura
- **Data**: Se não conseguir ler, use "unknown"

**INSTRUÇÕES ESPECÍFICAS**:
- Procure por tabelas, gráficos ou valores destacados
- Identifique unidades de medida (kg, %, kcal, etc.)
- Se houver múltiplas medições, use a mais recente ou principal
- Se valores estiverem em diferentes unidades, converta para as unidades padrão
- Se a imagem estiver borrada ou ilegível, indique baixa confiança (0.1-0.3)

Retorne apenas o JSON válido, sem texto adicional.
"""
            
            # Usa LiteLLM para análise multimodal com formato compatível
            response = await llm_service.call_with_fallback(
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }],
                max_tokens=500,
                temperature=0.1
            )
            
            # Log da resposta bruta do LLM
            print(f"📊 MultimodalTool: Resposta bruta do LLM para análise de bioimpedância:")
            print(f"📝 Resposta: {response[:500]}...")
            
            # Extrai JSON da resposta com limpeza robusta
            import json
            import re
            
            # Limpa a resposta removendo texto antes e depois do JSON
            cleaned_response = response.strip()
            
            # Remove possíveis markdown ou texto extra
            if "```json" in cleaned_response:
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0]
            elif "```" in cleaned_response:
                cleaned_response = cleaned_response.split("```")[1].split("```")[0]
            
            # Procura por JSON na resposta usando múltiplas estratégias
            json_str = None
            
            # Estratégia 1: Procura por JSON completo
            json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
            
            # Estratégia 2: Se não encontrou, tenta encontrar o primeiro { até o último }
            if not json_str:
                start_idx = cleaned_response.find('{')
                end_idx = cleaned_response.rfind('}')
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_str = cleaned_response[start_idx:end_idx+1]
            
            if json_str:
                # Limpa o JSON de possíveis caracteres problemáticos
                json_str = json_str.strip()
                
                # Remove vírgulas finais problemáticas
                json_str = re.sub(r',\s*}', '}', json_str)
                json_str = re.sub(r',\s*]', ']', json_str)
                
                # Verifica se o JSON está completo
                open_braces = json_str.count('{')
                close_braces = json_str.count('}')
                open_brackets = json_str.count('[')
                close_brackets = json_str.count(']')
                
                # Se o JSON está incompleto, tenta completar
                if open_braces > close_braces:
                    missing_braces = open_braces - close_braces
                    json_str += '}' * missing_braces
                
                if open_brackets > close_brackets:
                    missing_brackets = open_brackets - close_brackets
                    json_str += ']' * missing_brackets
                
                # Log do JSON limpo para debug
                print(f"🔍 MultimodalTool: JSON extraído e limpo:")
                print(f"📝 JSON: {json_str[:300]}...")
                
                try:
                    analysis = json.loads(json_str)
                    
                    # Log do resultado da análise
                    print(f"✅ MultimodalTool: Análise de bioimpedância concluída com sucesso!")
                    print(f"📊 Peso: {analysis.get('weight_kg', 'N/A')} kg")
                    print(f"📊 Gordura corporal: {analysis.get('body_fat_percent', 'N/A')}%")
                    print(f"📊 Massa muscular: {analysis.get('muscle_mass_kg', 'N/A')} kg")
                    print(f"📊 Gordura visceral: {analysis.get('visceral_fat_level', 'N/A')}")
                    print(f"📊 Taxa metabólica: {analysis.get('basal_metabolic_rate', 'N/A')} kcal")
                    print(f"📊 Hidratação: {analysis.get('hydration_percent', 'N/A')}%")
                    print(f"📊 Massa óssea: {analysis.get('bone_mass_kg', 'N/A')} kg")
                    print(f"📅 Data: {analysis.get('date', 'N/A')}")
                    print(f"📈 Confiança: {analysis.get('confidence', 0):.1%}")
                    print(f"🔧 Método: {analysis.get('analysis_method', 'unknown')}")
                    print(f"🧠 Reasoning: {analysis.get('reasoning', 'Não fornecido')}")
                    
                    return analysis
                    
                except json.JSONDecodeError as json_error:
                    print(f"❌ MultimodalTool: Erro ao parsear JSON: {json_error}")
                    print(f"❌ MultimodalTool: JSON problemático: {json_str}")
                    print(f"❌ MultimodalTool: Resposta original: {response[:500]}...")
                    raise Exception(f"JSON inválido retornado pelo LLM: {str(json_error)}")
            else:
                print(f"❌ MultimodalTool: Resposta não contém JSON válido")
                print(f"📝 Resposta completa: {response}")
                raise Exception("Resposta não contém JSON válido")
                    
        except Exception as e:
            print(f"❌ Erro na análise LLM: {e}")
            # Retorna análise placeholder em caso de erro
            return {
                "weight_kg": 70.5,
                "body_fat_percent": 15.2,
                "muscle_mass_kg": 58.3,
                "visceral_fat_level": 8,
                "basal_metabolic_rate": 1650,
                "hydration_percent": 60.1,
                "bone_mass_kg": 2.8,
                "date": "unknown",
                "confidence": 0.3,
                "analysis_method": "llm_error_fallback",
                "reasoning": f"Erro na análise LLM: {str(e)}"
            }
    
    async def _analyze_food_with_llm(self, image_base64: str) -> Dict[str, Any]:
        """
        Analisa imagem de comida usando LiteLLM
        """
        try:
            prompt = """
Analise cuidadosamente a **imagem enviada de comida** e identifique todos os alimentos visíveis.  

**Regras obrigatórias para a análise**:  
1. Liste cada alimento identificado em `"food_items"`.  
2.	Para cada alimento, estime a quantidade aproximada em gramas usando faixas comuns de porções (ex.: 50g, 100g, 150g, 200g).
	•	**SEMPRE ESTIME PARA CIMA**: Se houver dúvida entre duas quantidades, escolha a maior.
	•	Se não for possível estimar, use "quantity_grams": "unknown" e faça estimativas conservadoras de calorias e macros.
3. Use tabelas nutricionais padrão (USDA, TACO ou equivalentes) como referência para calcular calorias e macronutrientes.  
4. Some os valores de cada item para calcular o **total** (campo `"estimated_calories"` e `"macronutrients"`).  
5. Se não conseguir identificar claramente um alimento, use `"unknown"` e faça uma estimativa conservadora.  
6. **ESTIMATIVA CONSERVADORA**: Sempre arredonde calorias e macronutrientes para cima quando houver dúvida.
7. Sempre inclua um campo `"confidence"` entre 0.0 e 1.0 para indicar o grau de confiança da análise.  
8. Retorne **apenas** um JSON válido (nenhum texto fora do JSON).  
9. Inclua o campo `"analysis_method": "llm_analysis"` fixo.

**IMPORTANTE - FORMATO JSON OBRIGATÓRIO:**
- Use apenas aspas duplas (")
- NUNCA use vírgulas finais após o último item de arrays ou objetos
- Todos os números devem ser números, não strings
- Certifique-se de que o JSON está bem formado
- Evite caracteres especiais ou quebras de linha dentro de strings
- SEMPRE termine com } (chave de fechamento)
- SEMPRE termine arrays com ] (colchete de fechamento)
- Exemplo de estrutura correta:

```json
{
  "food_items": [
    {
      "name": "arroz branco",
      "quantity_grams": 150,
      "calories": 200,
      "protein": 4,
      "carbs": 45,
      "fat": 0.5
    },
    {
      "name": "frango grelhado",
      "quantity_grams": 120,
      "calories": 200,
      "protein": 30,
      "carbs": 0,
      "fat": 8
    },
    {
      "name": "feijão",
      "quantity_grams": 100,
      "calories": 130,
      "protein": 8,
      "carbs": 20,
      "fat": 1
    }
  ],
  "estimated_calories": 530,
  "calorie_range": {
    "min": 530,
    "max": 689
  },
  "macronutrients": {
    "protein": 42,
    "carbs": 65,
    "fat": 9.5
  },
  "confidence": 0.8,
  "analysis_method": "llm_analysis",
  "reasoning": "Identifiquei claramente arroz branco, frango grelhado e feijão no prato"
}
```

**ESTRATÉGIA DE ESTIMATIVA CONSERVADORA:**
- **Quantidade**: Se não tiver certeza se é 100g ou 150g, escolha 150g
- **Calorias**: Se calcular 180 kcal, arredonde para 200 kcal
- **Proteína**: Se calcular 22g, arredonde para 25g
- **Carboidratos**: Se calcular 45g, arredonde para 50g
- **Gordura**: Se calcular 8g, arredonde para 10g
- **Princípio**: É melhor superestimar do que subestimar valores nutricionais

**CÁLCULO DO RANGE DE CALORIAS CONSERVADOR:**
- **Min**: Use o valor calculado como mínimo (não reduza)
- **Max**: Adicione 20-30% ao valor calculado para o máximo
- **Exemplo**: Se calcular 400 kcal → min: 400, max: 520 (400 + 30%)
- **Exemplo**: Se calcular 250 kcal → min: 250, max: 325 (250 + 30%)
- **Princípio**: O range deve ser conservador, sempre incluindo margem de segurança

### Estrutura de saída obrigatória:
```json
{
  "food_items": [
    {
      "name": "alimento_identificado",
      "quantity_grams": número_em_gramas,
      "calories": número_calorias,
      "protein": gramas_proteina,
      "carbs": gramas_carboidratos,
      "fat": gramas_gordura
    }
  ],
  "estimated_calories": total_de_calorias,
  "calorie_range": {
    "min": valor_mínimo_conservador,
    "max": valor_máximo_conservador
  },
  "macronutrients": {
    "protein": total_proteina,
    "carbs": total_carboidratos,
    "fat": total_gordura
  },
  "confidence": 0.0_a_1.0,
  "analysis_method": "llm_analysis",
  "reasoning": "explicação_detalhada_da_análise_realizada"
}"""
            
            # Usa LiteLLM para análise multimodal com formato compatível
            response = await llm_service.call_with_fallback(
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }],
                max_tokens=500,
                temperature=0.1
            )
            
            # Log da resposta bruta do LLM
            print(f"🍽️ MultimodalTool: Resposta bruta do LLM para análise de comida:")
            print(f"📝 Resposta: {response[:500]}...")
            
            # Extrai JSON da resposta com limpeza robusta
            import json
            import re
            
            # Limpa a resposta removendo texto antes e depois do JSON
            cleaned_response = response.strip()
            
            # Remove possíveis markdown ou texto extra
            if "```json" in cleaned_response:
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0]
            elif "```" in cleaned_response:
                cleaned_response = cleaned_response.split("```")[1].split("```")[0]
            
            # Procura por JSON na resposta usando múltiplas estratégias
            json_str = None
            
            # Estratégia 1: Procura por JSON completo
            json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
            
            # Estratégia 2: Se não encontrou, tenta encontrar o primeiro { até o último }
            if not json_str:
                start_idx = cleaned_response.find('{')
                end_idx = cleaned_response.rfind('}')
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_str = cleaned_response[start_idx:end_idx+1]
            
            if json_str:
                # Limpa o JSON de possíveis caracteres problemáticos
                json_str = json_str.strip()
                
                # Remove vírgulas finais problemáticas
                json_str = re.sub(r',\s*}', '}', json_str)
                json_str = re.sub(r',\s*]', ']', json_str)
                
                # Verifica se o JSON está completo
                open_braces = json_str.count('{')
                close_braces = json_str.count('}')
                open_brackets = json_str.count('[')
                close_brackets = json_str.count(']')
                
                # Se o JSON está incompleto, tenta completar
                if open_braces > close_braces:
                    missing_braces = open_braces - close_braces
                    json_str += '}' * missing_braces
                
                if open_brackets > close_brackets:
                    missing_brackets = open_brackets - close_brackets
                    json_str += ']' * missing_brackets
                
                # Log do JSON limpo para debug
                print(f"🔍 MultimodalTool: JSON extraído e limpo:")
                print(f"📝 JSON: {json_str[:300]}...")
                
                try:
                    analysis = json.loads(json_str)
                    
                    # Log do resultado da análise
                    print(f"✅ MultimodalTool: Análise de comida concluída com sucesso!")
                    print(f"🍽️ Alimentos identificados: {analysis.get('food_items', [])}")
                    print(f"🔥 Calorias estimadas: {analysis.get('estimated_calories', 0)} kcal")
                    print(f"📊 Range de calorias: {analysis.get('calorie_range', {}).get('min', 0)}-{analysis.get('calorie_range', {}).get('max', 0)} kcal")
                    print(f"🥩 Macronutrientes: {analysis.get('macronutrients', {})}")
                    print(f"📈 Confiança: {analysis.get('confidence', 0):.1%}")
                    print(f"🔧 Método: {analysis.get('analysis_method', 'unknown')}")
                    print(f"🧠 Reasoning: {analysis.get('reasoning', 'Não fornecido')}")
                    
                    return analysis
                    
                except json.JSONDecodeError as json_error:
                    print(f"❌ MultimodalTool: Erro ao parsear JSON: {json_error}")
                    print(f"❌ MultimodalTool: JSON problemático: {json_str}")
                    print(f"❌ MultimodalTool: Resposta original: {response[:500]}...")
                    raise Exception(f"JSON inválido retornado pelo LLM: {str(json_error)}")
            else:
                print(f"❌ MultimodalTool: Resposta não contém JSON válido")
                print(f"📝 Resposta completa: {response}")
                raise Exception("Resposta não contém JSON válido")
                    
        except Exception as e:
            print(f"❌ Erro na análise LLM: {e}")
            # Retorna análise placeholder em caso de erro
            return {
                "food_items": ["unknown"],
                "estimated_calories": 300,
                "calorie_range": {
                    "min": 300,
                    "max": 390
                },
                "macronutrients": {
                    "protein": 20,
                    "carbs": 30,
                    "fat": 10
                },
                "confidence": 0.3,
                "analysis_method": "llm_error_fallback",
                "reasoning": f"Erro na análise LLM: {str(e)[:100]}"
            }
    
    async def _placeholder_analyze_food(self, image_data: bytes) -> Dict[str, Any]:
        """
        Placeholder para análise de alimentos
        """
        # Simulação de análise de alimentos
        return {
            "food_items": ["frango", "arroz", "vegetais"],
            "estimated_calories": 450,
            "macronutrients": {
                "protein": 35,
                "carbs": 45,
                "fat": 12
            },
            "confidence": 0.6,
            "analysis_method": "placeholder"
        }
    
    async def _analyze_exercise_with_llm(self, image_base64: str) -> Dict[str, Any]:
        """
        Analisa imagem de exercício usando LLM
        """
        try:
            prompt = f"""
Você é um especialista em análise de exercícios físicos e personal trainer.
Analise a imagem e forneça uma análise detalhada do exercício mostrado.

INSTRUÇÕES:
1. Identifique o exercício específico sendo realizado
2. Analise a técnica e execução
3. Identifique os músculos trabalhados
4. Avalie a postura e forma
5. Sugira melhorias ou ajustes
6. Considere segurança e eficácia

ESTRUTURA DE SAÍDA OBRIGATÓRIA:
```json
{{
  "exercise_name": "nome_do_exercício",
  "muscle_groups": ["músculo_1", "músculo_2"],
  "execution_analysis": {{
    "form_score": 1_a_10,
    "posture_notes": "observações_sobre_postura",
    "technique_notes": "observações_sobre_técnica"
  }},
  "suggestions": [
    "sugestão_1",
    "sugestão_2",
    "sugestão_3"
  ],
  "safety_notes": "observações_de_segurança",
  "difficulty_level": "iniciante/intermediário/avançado",
  "equipment_needed": "equipamento_necessário",
  "confidence": 0.0_a_1.0,
  "reasoning": "explicação_detalhada_da_análise"
}}"""
            
            response = await llm_service.call_with_fallback(
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }],
                max_tokens=800,
                temperature=0.1
            )
            
            # Extrai JSON da resposta
            import json
            import re
            
            cleaned_response = response.strip()
            if "```json" in cleaned_response:
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0]
            elif "```" in cleaned_response:
                cleaned_response = cleaned_response.split("```")[1].split("```")[0]
            
            # Remove texto antes e depois do JSON
            json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
            if json_match:
                cleaned_response = json_match.group(0)
            
            analysis = json.loads(cleaned_response.strip())
            return analysis
            
        except Exception as e:
            print(f"❌ Erro na análise de exercício: {e}")
            return {
                "exercise_name": "exercício não identificado",
                "muscle_groups": ["músculos não identificados"],
                "execution_analysis": {
                    "form_score": 5,
                    "posture_notes": "Não foi possível analisar a postura",
                    "technique_notes": "Não foi possível analisar a técnica"
                },
                "suggestions": ["Consulte um personal trainer para análise detalhada"],
                "safety_notes": "Sempre pratique exercícios com supervisão adequada",
                "difficulty_level": "indeterminado",
                "equipment_needed": "não identificado",
                "confidence": 0.1,
                "reasoning": f"Erro na análise LLM: {str(e)[:100]}"
            }
    
    async def _analyze_body_with_llm(self, image_base64: str) -> Dict[str, Any]:
        """
        Analisa imagem corporal usando LLM
        """
        try:
            prompt = f"""
Você é um especialista em análise corporal e composição física.
Analise a imagem corporal de forma respeitosa e profissional.

INSTRUÇÕES:
1. Analise a composição corporal geral
2. Identifique áreas de desenvolvimento
3. Sugira ajustes na dieta e treino
4. Mantenha tom positivo e motivador
5. Foque em saúde e bem-estar
6. Evite comentários negativos ou críticos

ESTRUTURA DE SAÍDA OBRIGATÓRIA:
```json
{{
  "body_composition": {{
    "muscle_definition": "baixa/média/alta",
    "body_fat_estimate": "baixo/médio/alto",
    "overall_condition": "descrição_geral"
  }},
  "development_areas": [
    "área_1",
    "área_2",
    "área_3"
  ],
  "diet_suggestions": [
    "sugestão_dieta_1",
    "sugestão_dieta_2"
  ],
  "training_suggestions": [
    "sugestão_treino_1",
    "sugestão_treino_2"
  ],
  "positive_notes": "observações_positivas",
  "confidence": 0.0_a_1.0,
  "reasoning": "explicação_detalhada_da_análise"
}}"""
            
            response = await llm_service.call_with_fallback(
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }],
                max_tokens=600,
                temperature=0.1
            )
            
            # Extrai JSON da resposta
            import json
            import re
            
            cleaned_response = response.strip()
            if "```json" in cleaned_response:
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0]
            elif "```" in cleaned_response:
                cleaned_response = cleaned_response.split("```")[1].split("```")[0]
            
            json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
            if json_match:
                cleaned_response = json_match.group(0)
            
            analysis = json.loads(cleaned_response.strip())
            return analysis
            
        except Exception as e:
            print(f"❌ Erro na análise corporal: {e}")
            return {
                "body_composition": {
                    "muscle_definition": "não analisado",
                    "body_fat_estimate": "não analisado",
                    "overall_condition": "Não foi possível analisar"
                },
                "development_areas": ["Consulte um profissional para análise detalhada"],
                "diet_suggestions": ["Mantenha uma alimentação equilibrada"],
                "training_suggestions": ["Consulte um personal trainer"],
                "positive_notes": "Continue focado nos seus objetivos",
                "confidence": 0.1,
                "reasoning": f"Erro na análise LLM: {str(e)[:100]}"
            }
    
    async def _analyze_label_with_llm(self, image_base64: str) -> Dict[str, Any]:
        """
        Analisa imagem de rótulo nutricional usando LLM
        """
        try:
            prompt = f"""
Você é um especialista em análise de rótulos nutricionais.
Analise a imagem do rótulo e extraia as informações nutricionais principais.

INSTRUÇÕES:
1. Extraia informações nutricionais principais
2. Identifique pontos de atenção (açúcar, sódio, etc.)
3. Avalie a qualidade nutricional geral
4. Sugira alternativas se necessário
5. Foque nos aspectos mais relevantes para saúde

ESTRUTURA DE SAÍDA OBRIGATÓRIA:
```json
{{
  "product_name": "nome_do_produto",
  "nutritional_info": {{
    "calories_per_serving": número,
    "protein": "valor_proteína",
    "carbs": "valor_carboidratos",
    "fat": "valor_gordura",
    "sugar": "valor_açúcar",
    "sodium": "valor_sódio",
    "fiber": "valor_fibras"
  }},
  "serving_size": "tamanho_da_porção",
  "ingredients": ["ingrediente_1", "ingrediente_2"],
  "health_notes": [
    "nota_saúde_1",
    "nota_saúde_2"
  ],
  "red_flags": ["ponto_atencao_1", "ponto_atencao_2"],
  "overall_rating": "ruim/regular/bom/excelente",
  "confidence": 0.0_a_1.0,
  "reasoning": "explicação_detalhada_da_análise"
}}"""
            
            response = await llm_service.call_with_fallback(
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }],
                max_tokens=700,
                temperature=0.1
            )
            
            # Extrai JSON da resposta
            import json
            import re
            
            cleaned_response = response.strip()
            if "```json" in cleaned_response:
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0]
            elif "```" in cleaned_response:
                cleaned_response = cleaned_response.split("```")[1].split("```")[0]
            
            json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
            if json_match:
                cleaned_response = json_match.group(0)
            
            analysis = json.loads(cleaned_response.strip())
            return analysis
            
        except Exception as e:
            print(f"❌ Erro na análise de rótulo: {e}")
            return {
                "product_name": "produto não identificado",
                "nutritional_info": {
                    "calories_per_serving": 0,
                    "protein": "não identificado",
                    "carbs": "não identificado",
                    "fat": "não identificado",
                    "sugar": "não identificado",
                    "sodium": "não identificado",
                    "fiber": "não identificado"
                },
                "serving_size": "não identificado",
                "ingredients": ["Não foi possível identificar ingredientes"],
                "health_notes": ["Consulte um nutricionista para análise detalhada"],
                "red_flags": ["Não foi possível analisar"],
                "overall_rating": "não avaliado",
                "confidence": 0.1,
                "reasoning": f"Erro na análise LLM: {str(e)[:100]}"
            }
    
    async def _analyze_treino_planilha_with_llm(self, image_base64: str) -> Dict[str, Any]:
        """
        Analisa imagem de planilha de treino usando LLM
        """
        try:
            prompt = f"""
Você é um especialista em análise de planilhas e programas de treino.
Analise a imagem da planilha de treino e extraia as informações principais.

INSTRUÇÕES:
1. Identifique os exercícios listados
2. Extraia séries, repetições e cargas
3. Analise a estrutura do treino
4. Avalie a progressão e organização
5. Sugira melhorias se necessário
6. Identifique o tipo de treino (força, hipertrofia, etc.)

ESTRUTURA DE SAÍDA OBRIGATÓRIA:
```json
{{
  "workout_type": "tipo_de_treino",
  "exercises": [
    {{
      "name": "nome_exercício",
      "sets": número_séries,
      "reps": "número_repetições",
      "weight": "carga_peso",
      "notes": "observações_adicionais"
    }}
  ],
  "workout_structure": {{
    "total_exercises": número,
    "estimated_duration": "tempo_estimado",
    "difficulty_level": "iniciante/intermediário/avançado"
  }},
  "progression_notes": "observações_sobre_progressão",
  "suggestions": [
    "sugestão_1",
    "sugestão_2"
  ],
  "overall_assessment": "avaliação_geral",
  "confidence": 0.0_a_1.0,
  "reasoning": "explicação_detalhada_da_análise"
}}"""
            
            response = await llm_service.call_with_fallback(
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }],
                max_tokens=1000,
                temperature=0.1
            )
            
            # Extrai JSON da resposta
            import json
            import re
            
            cleaned_response = response.strip()
            if "```json" in cleaned_response:
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0]
            elif "```" in cleaned_response:
                cleaned_response = cleaned_response.split("```")[1].split("```")[0]
            
            json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
            if json_match:
                cleaned_response = json_match.group(0)
            
            analysis = json.loads(cleaned_response.strip())
            return analysis
            
        except Exception as e:
            print(f"❌ Erro na análise de planilha: {e}")
            return {
                "workout_type": "treino não identificado",
                "exercises": [{
                    "name": "exercício não identificado",
                    "sets": 0,
                    "reps": "não identificado",
                    "weight": "não identificado",
                    "notes": "Não foi possível analisar"
                }],
                "workout_structure": {
                    "total_exercises": 0,
                    "estimated_duration": "não estimado",
                    "difficulty_level": "indeterminado"
                },
                "progression_notes": "Não foi possível analisar a progressão",
                "suggestions": ["Consulte um personal trainer para análise detalhada"],
                "overall_assessment": "Não foi possível avaliar",
                "confidence": 0.1,
                "reasoning": f"Erro na análise LLM: {str(e)[:100]}"
            }
