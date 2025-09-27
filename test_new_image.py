#!/usr/bin/env python3
"""
Teste com nova imagem para verificar JSON parsing
"""

import asyncio
import sys
import os
from PIL import Image
import io

# Adiciona o diretório atual ao path
sys.path.append(os.getcwd())

async def test_new_image():
    try:
        from app.tools.multimodal_tool import MultimodalTool
        
        print("🧪 TESTE COM NOVA IMAGEM - VERIFICAÇÃO DE JSON PARSING")
        print("=" * 60)
        
        # Cria uma imagem de teste mais complexa
        print("📸 Criando imagem de teste complexa...")
        img = Image.new('RGB', (500, 400), color='white')
        
        # Converte para bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='JPEG')
        image_data = img_buffer.getvalue()
        
        print(f"📊 Tamanho da imagem: {len(image_data)} bytes")
        
        # Cria instância do MultimodalTool
        multimodal_tool = MultimodalTool()
        
        print("📤 Iniciando análise de imagem...")
        print("🔍 Verificando se JSON parsing está funcionando...")
        
        # Chama o método de análise
        result = await multimodal_tool.analyze_food_image(image_data)
        
        print("✅ Análise concluída!")
        print("📊 Resultado:")
        print(f"   Success: {result.get('success', False)}")
        
        if result.get("success"):
            analysis = result.get("analysis", {})
            print(f"   🍽️ Food items: {len(analysis.get('food_items', []))} itens")
            print(f"   🔥 Calories: {analysis.get('estimated_calories', 0)}")
            print(f"   📊 Calorie range: {analysis.get('calorie_range', {})}")
            print(f"   🥩 Macronutrients: {analysis.get('macronutrients', {})}")
            print(f"   🎯 Confidence: {analysis.get('confidence', 0)}")
            print(f"   🔧 Method: {analysis.get('analysis_method', 'unknown')}")
            print(f"   💭 Reasoning: {analysis.get('reasoning', 'N/A')[:100]}...")
            
            # Verifica se é o fallback
            if analysis.get('food_items') == ['unknown']:
                print("\n⚠️  ATENÇÃO: Sistema caiu no fallback")
                print("   Isso significa que houve erro de JSON parsing")
                print("   Vamos investigar o problema...")
            else:
                print("\n✅ SUCESSO: JSON parsing funcionando!")
                print("   LLM processou a imagem com sucesso!")
                
                # Mostra detalhes dos alimentos
                food_items = analysis.get('food_items', [])
                print(f"\n🍽️ ALIMENTOS IDENTIFICADOS ({len(food_items)} itens):")
                for i, item in enumerate(food_items, 1):
                    if isinstance(item, dict):
                        name = item.get("name", "Desconhecido")
                        quantity = item.get("quantity_grams", "N/A")
                        calories = item.get("calories", 0)
                        print(f"      {i}. {name} ({quantity}g, {calories} kcal)")
                    else:
                        print(f"      {i}. {item}")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Executa o teste
    asyncio.run(test_new_image())
