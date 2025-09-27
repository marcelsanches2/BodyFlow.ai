#!/usr/bin/env python3
"""
Teste real com imagem de comida para verificar formato de envio
"""

import asyncio
import sys
import os
from PIL import Image, ImageDraw
import io
import base64

# Adiciona o diretório atual ao path
sys.path.append(os.getcwd())

async def test_real_food_image():
    try:
        from app.tools.multimodal_tool import MultimodalTool
        
        print("🧪 TESTE REAL COM IMAGEM DE COMIDA")
        print("=" * 45)
        
        # Cria uma imagem que simula um prato de comida
        print("📸 Criando imagem simulando prato de comida...")
        
        img = Image.new('RGB', (500, 400), color='white')
        draw = ImageDraw.Draw(img)
        
        # Desenha elementos que simulam comida
        # Prato (círculo)
        draw.ellipse([50, 50, 450, 350], fill='lightgray', outline='black', width=2)
        
        # Carne (retângulo marrom)
        draw.rectangle([100, 100, 200, 150], fill='brown', outline='black')
        
        # Arroz (retângulo branco)
        draw.rectangle([250, 100, 350, 150], fill='white', outline='black')
        
        # Batata (retângulo amarelo)
        draw.rectangle([150, 200, 250, 250], fill='yellow', outline='black')
        
        # Vegetal (retângulo verde)
        draw.rectangle([300, 200, 400, 250], fill='green', outline='black')
        
        # Adiciona texto para identificar
        try:
            draw.text((10, 10), "PRATO DE COMIDA", fill='black')
        except:
            pass
        
        print(f"📊 Imagem criada: {img.size[0]}x{img.size[1]} pixels")
        
        # Converte para bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='JPEG', quality=90)
        image_data = img_buffer.getvalue()
        
        print(f"📊 Tamanho da imagem: {len(image_data)} bytes")
        
        # Testa com MultimodalTool
        multimodal_tool = MultimodalTool()
        
        print("📤 Iniciando análise com MultimodalTool...")
        
        # Chama o método de análise
        result = await multimodal_tool.analyze_food_image(image_data)
        
        print("✅ Análise concluída!")
        print("📊 Resultado:")
        print(f"   Success: {result.get('success', False)}")
        
        if result.get("success"):
            analysis = result.get("analysis", {})
            food_items = analysis.get('food_items', [])
            
            print(f"   🍽️ Food items: {len(food_items)} itens")
            print(f"   🔥 Calories: {analysis.get('estimated_calories', 0)}")
            print(f"   📊 Calorie range: {analysis.get('calorie_range', {})}")
            print(f"   🥩 Macronutrients: {analysis.get('macronutrients', {})}")
            print(f"   🎯 Confidence: {analysis.get('confidence', 0)}")
            print(f"   🔧 Method: {analysis.get('analysis_method', 'unknown')}")
            print(f"   💭 Reasoning: {analysis.get('reasoning', 'N/A')[:100]}...")
            
            # Verifica se identificou alimentos
            if analysis.get('food_items') == ['unknown']:
                print("\n⚠️  PROBLEMA: Sistema não identificou alimentos")
                print("   Isso indica que o LLM não está vendo a imagem corretamente")
                print("   Possíveis causas:")
                print("   - Formato de envio incorreto")
                print("   - LLM não consegue processar a imagem")
                print("   - Problema na conversão base64")
            else:
                print("\n✅ SUCESSO: Sistema identificou alimentos!")
                print("   Formato de envio está funcionando corretamente")
                
                # Mostra detalhes dos alimentos
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
    asyncio.run(test_real_food_image())
