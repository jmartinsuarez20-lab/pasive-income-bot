# simple_main.py - BOT SIMPLE QUE FUNCIONA GARANTIZADO
import requests
import json
import openai
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import random

# Configurar OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

def test_openai():
    """Prueba básica de OpenAI"""
    print("🧪 Probando OpenAI API...")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Di solo 'funciona'"}],
            max_tokens=10
        )
        result = response.choices[0].message.content.strip()
        print(f"✅ OpenAI responde: {result}")
        return True
    except Exception as e:
        print(f"❌ Error OpenAI: {e}")
        return False

def get_simple_content():
    """Contenido básico para crear producto"""
    print("📝 Generando contenido base...")
    
    topics = [
        "10 secretos de emprendimiento que todo empresario debe conocer",
        "Estrategias de productividad para profesionales exitosos", 
        "Guía completa de marketing digital para principiantes",
        "Técnicas de ventas que realmente funcionan",
        "Como crear un negocio online desde cero"
    ]
    
    selected_topic = random.choice(topics)
    print(f"✅ Tema seleccionado: {selected_topic}")
    return selected_topic

def create_product_simple(topic):
    """Crear producto con IA - versión simple"""
    print("🤖 Creando producto con IA...")
    
    prompt = f"""Crea un ebook corto sobre: "{topic}"

Devuelve SOLO un JSON con esta estructura:
{{
    "titulo": "Título atractivo máximo 60 caracteres",
    "precio": número entre 15 y 25,
    "contenido": "Ebook de 8 capítulos con introducción y conclusión. Mínimo 1000 palabras.",
    "descripcion": "Descripción de venta de 100 palabras"
}}

Solo el JSON, nada más."""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.7
        )
        
        content = response.choices[0].message.content.strip()
        
        # Limpiar respuesta
        if content.startswith('```json'):
            content = content[7:]
        if content.endswith('```'):
            content = content[:-3]
        
        product = json.loads(content)
        print("✅ Producto creado por IA")
        return product
        
    except Exception as e:
        print(f"❌ Error IA: {e}")
        return {
            "titulo": f"Guía Práctica: {topic[:40]}...",
            "precio": random.randint(15, 25),
            "contenido": f"Esta es una guía completa sobre {topic}. Incluye estrategias probadas y consejos prácticos para obtener resultados reales.",
            "descripcion": f"Guía práctica sobre {topic} con consejos de expertos y técnicas probadas."
        }

def create_simple_pdf(product):
    """Crear PDF básico pero funcional"""
    print("📄 Creando PDF...")
    
    filename = f"producto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    try:
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        # Título
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, height-100, product['titulo'][:80])
        
        # Fecha
        c.setFont("Helvetica", 12)
        c.drawString(50, height-130, f"Creado: {datetime.now().strftime('%d/%m/%Y')}")
        c.drawString(50, height-150, f"Precio: €{product['precio']}")
        
        # Contenido
        c.setFont("Helvetica", 10)
        y_position = height - 200
        
        # Dividir contenido en líneas
        content = product['contenido']
        words = content.split()
        line = ""
        
        for word in words[:500]:  # Máximo 500 palabras
            if len(line + word) < 80:
                line += word + " "
            else:
                if y_position < 50:
                    c.showPage()
                    y_position = height - 50
                    c.setFont("Helvetica", 10)
                
                c.drawString(50, y_position, line.strip())
                line = word + " "
                y_position -= 15
        
        # Última línea
        if line:
            c.drawString(50, y_position, line.strip())
        
        c.save()
        print(f"✅ PDF creado: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Error PDF: {e}")
        return None

def create_instructions(product, pdf_file):
    """Crear instrucciones de venta"""
    print("📋 Creando instrucciones...")
    
    instructions_file = f"INSTRUCCIONES_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    content = f"""
🛍️ PRODUCTO LISTO PARA VENDER
==============================

📊 INFORMACIÓN DEL PRODUCTO:
• Título: {product['titulo']}
• Precio sugerido: €{product['precio']}
• Archivo: {pdf_file}
• Creado: {datetime.now().strftime('%d/%m/%Y %H:%M')}

🌐 DÓNDE VENDER:
1. ETSY (Recomendado):
   - Categoría: Digital Downloads
   - Tags: guía, PDF, emprendimiento, negocio, digital
   - Descripción: {product['descripcion']}

2. GUMROAD:
   - Categoría: Business
   - Precio: €{product['precio']}
   - Descarga automática

3. TU PROPIA WEB:
   - Usar PayPal para pagos
   - Envío manual del PDF

📢 MARKETING BÁSICO:
• Publica en LinkedIn, Instagram, Facebook
• Usa hashtags: #emprendimiento #guiaPDF #negociodigital
• Ofrece descuento por lanzamiento

💰 PROYECCIÓN:
• 2-5 ventas/mes = €{product['precio']*2}-€{product['precio']*5}/mes
• Sin costos adicionales = 100% ganancia

🎯 SIGUIENTE PASO:
1. Descargar el PDF del repositorio
2. Subir a Etsy/Gumroad
3. Promocionar en redes sociales
4. ¡Empezar a vender!

==============================
Bot ejecutado: {datetime.now()}
"""
    
    try:
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Instrucciones creadas: {instructions_file}")
        return instructions_file
    except Exception as e:
        print(f"❌ Error instrucciones: {e}")
        return None

def main():
    """Función principal - SIMPLE Y EFECTIVA"""
    print(f"""
🤖 ==========================================
   BOT SIMPLE - INCOME PRODUCTS
   Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🤖 ==========================================
    """)
    
    try:
        # 1. Probar OpenAI
        if not test_openai():
            print("❌ OpenAI no funciona, saliendo...")
            return
        
        # 2. Generar contenido
        topic = get_simple_content()
        
        # 3. Crear producto con IA
        product = create_product_simple(topic)
        print(f"📦 Producto: {product['titulo']}")
        print(f"💰 Precio: €{product['precio']}")
        
        # 4. Crear PDF
        pdf_file = create_simple_pdf(product)
        
        # 5. Crear instrucciones
        instructions_file = create_instructions(product, pdf_file)
        
        # 6. Guardar resumen
        summary = {
            "timestamp": datetime.now().isoformat(),
            "producto": product['titulo'],
            "precio": product['precio'],
            "archivos": [pdf_file, instructions_file],
            "estado": "completado"
        }
        
        with open('ultimo_producto.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"""
🎉 ==========================================
   ¡PRODUCTO CREADO EXITOSAMENTE!
   
   📄 PDF: {pdf_file}
   📋 Instrucciones: {instructions_file}
   💰 Valor: €{product['precio']}
   
   🚀 LISTO PARA VENDER EN ETSY/GUMROAD
🎉 ==========================================
        """)
        
    except Exception as e:
        print(f"💥 Error crítico: {e}")
        
        # Crear archivo de error
        with open('error_log.txt', 'w') as f:
            f.write(f"Error: {e}\nFecha: {datetime.now()}\n")

if __name__ == "__main__":
    main()
