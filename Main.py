# main.py - Bot de Ingresos Pasivos 100% Automático
# Recopila contenido → IA procesa → Crea productos → Sube a Gumroad
# ¡Todo completamente automático!

import requests
import json
import openai
import os
import random
import time
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import textwrap
import re

# ================================
# CONFIGURACIÓN INICIAL
# ================================

# Configurar OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY')

# Configuración del bot
CONFIG = {
    'max_content_sources': 3,
    'posts_per_source': 15,
    'min_content_length': 200,
    'max_products_per_run': 2,
    'price_range': [1200, 2500],  # En centavos (€12-25)
    'test_mode': os.getenv('TEST_MODE', 'false').lower() == 'true'
}

# ================================
# FUNCIONES DE RECOPILACIÓN
# ================================

def get_content_sources():
    """Fuentes de contenido público y legal"""
    return [
        {
            'name': 'Entrepreneur Reddit',
            'url': 'https://www.reddit.com/r/entrepreneur/top.json?limit=25&t=week',
            'type': 'reddit',
            'topic': 'emprendimiento'
        },
        {
            'name': 'Small Business Reddit', 
            'url': 'https://www.reddit.com/r/smallbusiness/top.json?limit=20&t=week',
            'type': 'reddit',
            'topic': 'pequeños negocios'
        },
        {
            'name': 'Startups Reddit',
            'url': 'https://www.reddit.com/r/startups/top.json?limit=20&t=week', 
            'type': 'reddit',
            'topic': 'startups'
        },
        {
            'name': 'Business Tips Reddit',
            'url': 'https://www.reddit.com/r/business/top.json?limit=15&t=week',
            'type': 'reddit', 
            'topic': 'consejos de negocio'
        }
    ]

def scrape_reddit_content(source):
    """Recopila contenido de Reddit de forma ética"""
    print(f"🔍 Recopilando de: {source['name']}")
    
    headers = {
        'User-Agent': 'ContentBot/1.0 (Educational Purpose; Passive Income Research)'
    }
    
    try:
        response = requests.get(source['url'], headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Error {response.status_code} en {source['name']}")
            return []
        
        data = response.json()
        posts = data.get('data', {}).get('children', [])
        
        valid_content = []
        for post in posts:
            post_data = post.get('data', {})
            
            title = post_data.get('title', '').strip()
            content = post_data.get('selftext', '').strip()
            score = post_data.get('score', 0)
            
            # Filtros de calidad
            if (len(content) >= CONFIG['min_content_length'] and 
                score > 5 and 
                not content.lower().startswith('[removed]') and
                not content.lower().startswith('[deleted]')):
                
                valid_content.append({
                    'title': title[:200],  # Limitar título
                    'content': content[:1500],  # Limitar contenido
                    'score': score,
                    'source': source['name'],
                    'topic': source['topic'],
                    'scraped_at': datetime.now().isoformat()
                })
        
        print(f"✅ {len(valid_content)} posts válidos de {source['name']}")
        return valid_content
        
    except requests.RequestException as e:
        print(f"❌ Error de conexión con {source['name']}: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON de {source['name']}: {e}")
        return []
    except Exception as e:
        print(f"❌ Error inesperado con {source['name']}: {e}")
        return []

def collect_all_content():
    """Recopila contenido de todas las fuentes"""
    print("📥 Iniciando recopilación de contenido...")
    
    all_content = []
    sources = get_content_sources()[:CONFIG['max_content_sources']]
    
    for source in sources:
        content = scrape_reddit_content(source)
        all_content.extend(content)
        
        # Pausa entre requests para ser respetuoso
        time.sleep(2)
    
    # Ordenar por score y tomar los mejores
    all_content.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"📊 Total contenido recopilado: {len(all_content)} posts")
    return all_content

# ================================
# FUNCIONES DE IA
# ================================

def create_product_with_ai(content_list, attempt=1):
    """Usa IA para crear un producto vendible"""
    print(f"🤖 Creando producto con IA (intento {attempt}/3)...")
    
    if not content_list:
        print("❌ No hay contenido para procesar")
        return None
    
    # Seleccionar el mejor contenido
    selected_content = content_list[:15]  # Top 15 posts
    
    # Crear prompt optimizado
    content_text = "\n\n".join([
        f"CONSEJO {i+1}: {item['title']}\n{item['content'][:600]}"
        for i, item in enumerate(selected_content)
    ])
    
    # Generar tema y nicho específico
    topics = list(set([item.get('topic', 'negocio') for item in selected_content]))
    main_topic = random.choice(topics) if topics else 'emprendimiento'
    
    current_month = datetime.now().strftime('%B %Y')
    
    prompt = f"""Crea un ebook profesional sobre {main_topic} usando estos consejos reales:

{content_text}

IMPORTANTE: 
- Transforma y parafrasea TODO el contenido
- Agrega valor organizando y estructurando
- Crea introducciones y conclusiones originales
- Haz que sea un producto premium vendible

Devuelve SOLO un JSON válido con esta estructura exacta:
{{
    "titulo": "Título atractivo para vender (máx 60 caracteres)",
    "descripcion": "Descripción de venta persuasiva de 150-200 palabras que haga querer comprar",
    "precio": número entre 1200 y 2500 (en centavos),
    "contenido": "Ebook completo con 8-10 capítulos bien estructurados, introducción, conclusión y consejos transformados",
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
    "categoria": "{main_topic}",
    "mes": "{current_month}"
}}

El contenido debe ser completamente reescrito y profesional."""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": "Eres un experto en crear productos digitales vendibles. Siempre devuelves JSON válido y contenido completamente transformado."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=3500,
            temperature=0.8
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Limpiar respuesta
        if ai_response.startswith('```json'):
            ai_response = ai_response[7:]
        if ai_response.endswith('```'):
            ai_response = ai_response[:-3]
        
        ai_response = ai_response.strip()
        
        # Parsear JSON
        product_data = json.loads(ai_response)
        
        # Validar campos requeridos
        required_fields = ['titulo', 'descripcion', 'precio', 'contenido', 'tags']
        for field in required_fields:
            if field not in product_data or not product_data[field]:
                raise ValueError(f"Campo requerido '{field}' faltante o vacío")
        
        # Validaciones adicionales
        if len(product_data['titulo']) > 80:
            product_data['titulo'] = product_data['titulo'][:77] + "..."
        
        if not isinstance(product_data['precio'], int) or product_data['precio'] < 500:
            product_data['precio'] = random.randint(1200, 2500)
        
        if len(product_data['contenido']) < 500:
            raise ValueError("Contenido demasiado corto")
        
        print("✅ Producto creado exitosamente por IA")
        return product_data
        
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON (intento {attempt}): {e}")
        if attempt < 3:
            time.sleep(2)
            return create_product_with_ai(content_list, attempt + 1)
        return create_fallback_product(content_list)
        
    except openai.error.RateLimitError:
        print("❌ Rate limit alcanzado, esperando...")
        time.sleep(60)
        if attempt < 3:
            return create_product_with_ai(content_list, attempt + 1)
        return create_fallback_product(content_list)
        
    except Exception as e:
        print(f"❌ Error con IA (intento {attempt}): {e}")
        if attempt < 3:
            time.sleep(5)
            return create_product_with_ai(content_list, attempt + 1)
        return create_fallback_product(content_list)

def create_fallback_product(content_list):
    """Producto de respaldo si falla la IA"""
    print("🔄 Creando producto de respaldo...")
    
    topics = ['Emprendimiento', 'Negocios', 'Startups', 'Marketing', 'Ventas']
    topic = random.choice(topics)
    month = datetime.now().strftime('%B %Y')
    
    # Combinar contenido manualmente
    combined_content = []
    for i, item in enumerate(content_list[:10]):
        combined_content.append(f"""
CAPÍTULO {i+1}: {item['title']}

{item['content'][:500]}

Puntos clave:
- Implementa esta estrategia paso a paso
- Mide los resultados regularmente  
- Ajusta según tu situación específica

""")
    
    return {
        "titulo": f"Guía Completa {topic} {month}",
        "descripcion": f"Guía completa de {topic.lower()} con estrategias probadas y casos reales. Consejos prácticos recopilados de expertos y emprendedores exitosos. Perfecto para quien quiere resultados reales en {topic.lower()}.",
        "precio": random.randint(1500, 2200),
        "contenido": "\n".join(combined_content),
        "tags": [topic.lower(), "guia", "estrategias", "negocio", "exito"],
        "categoria": topic.lower(),
        "mes": month
    }

# ================================
# FUNCIONES DE CREACIÓN PDF
# ================================

def create_professional_pdf(product_data):
    """Crea un PDF profesional del producto"""
    print("📄 Creando PDF profesional...")
    
    # Nombre de archivo único
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"ebook_{timestamp}.pdf"
    
    try:
        # Configurar documento
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Estilos
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Centrado
            textColor='#2C3E50'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=24,
            textColor='#34495E'
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=0,  # Justificado
            textColor='#2C3E50'
        )
        
        # Contenido del PDF
        story = []
        
        # Título
        title = Paragraph(product_data['titulo'], title_style)
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        # Información del producto
        info = f"Creado automáticamente • {datetime.now().strftime('%B %Y')}"
        info_para = Paragraph(info, styles['Normal'])
        story.append(info_para)
        story.append(Spacer(1, 0.5*inch))
        
        # Introducción
        intro_title = Paragraph("Introducción", heading_style)
        story.append(intro_title)
        
        intro_text = f"""Bienvenido a esta guía completa sobre {product_data.get('categoria', 'emprendimiento')}. 
        En las siguientes páginas encontrarás estrategias, consejos y técnicas probadas que te ayudarán 
        a alcanzar tus objetivos. Todo el contenido ha sido cuidadosamente seleccionado y organizado 
        para maximizar tu aprendizaje."""
        
        intro_para = Paragraph(intro_text, body_style)
        story.append(intro_para)
        story.append(Spacer(1, 0.3*inch))
        
        # Contenido principal
        content_title = Paragraph("Contenido Principal", heading_style)
        story.append(content_title)
        
        # Dividir contenido en párrafos manejables
        content = product_data['contenido']
        
        # Limpiar y formatear contenido
        content = re.sub(r'\n\s*\n', '\n\n', content)  # Normalizar saltos de línea
        paragraphs = content.split('\n\n')
        
        for para in paragraphs[:50]:  # Limitar a 50 párrafos
            if para.strip():
                # Detectar si es un título/heading
                if (para.strip().startswith('CAPÍTULO') or 
                    para.strip().startswith('TEMA') or
                    len(para.strip()) < 100 and para.strip().isupper()):
                    para_obj = Paragraph(para.strip(), heading_style)
                else:
                    para_obj = Paragraph(para.strip(), body_style)
                
                story.append(para_obj)
                story.append(Spacer(1, 0.1*inch))
        
        # Conclusión
        conclusion_title = Paragraph("Conclusión", heading_style)
        story.append(conclusion_title)
        
        conclusion_text = """Has completado esta guía completa. Ahora tienes las herramientas 
        y conocimientos necesarios para implementar estas estrategias en tu situación específica. 
        Recuerda que el éxito viene de la acción consistente. ¡Es hora de implementar lo aprendido!"""
        
        conclusion_para = Paragraph(conclusion_text, body_style)
        story.append(conclusion_para)
        
        # Construir PDF
        doc.build(story)
        
        print(f"✅ PDF creado exitosamente: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Error creando PDF: {e}")
        return create_simple_pdf(product_data)

def create_simple_pdf(product_data):
    """PDF simple como respaldo"""
    print("🔄 Creando PDF simple como respaldo...")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"ebook_simple_{timestamp}.pdf"
    
    try:
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        # Título
        c.setFont("Helvetica-Bold", 20)
        title = product_data['titulo'][:60]
        c.drawString(72, height-100, title)
        
        # Fecha
        c.setFont("Helvetica", 12)
        c.drawString(72, height-130, f"Creado: {datetime.now().strftime('%B %Y')}")
        
        # Contenido
        c.setFont("Helvetica", 10)
        y_position = height - 180
        margin = 72
        
        content = product_data['contenido']
        words = content.split()
        
        line = ""
        for word in words[:1000]:  # Limitar palabras
            test_line = line + word + " "
            if len(test_line) > 85:  # Caracteres por línea
                if y_position < 72:  # Nueva página
                    c.showPage()
                    y_position = height - 72
                    c.setFont("Helvetica", 10)
                
                c.drawString(margin, y_position, line.strip())
                line = word + " "
                y_position -= 14
            else:
                line = test_line
        
        # Última línea
        if line and y_position > 72:
            c.drawString(margin, y_position, line.strip())
        
        c.save()
        print(f"✅ PDF simple creado: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Error creando PDF simple: {e}")
        return None

# ================================
# FUNCIONES DE GUMROAD
# ================================

def upload_to_gumroad(pdf_file, product_data, attempt=1):
    """Sube producto a Gumroad automáticamente"""
    print(f"🏪 Subiendo a Gumroad (intento {attempt}/3)...")
    
    token = os.getenv('GUMROAD_ACCESS_TOKEN')
    if not token:
        print("❌ Token de Gumroad no encontrado")
        return None
    
    # Datos del producto optimizados para ventas
    product_payload = {
        'name': product_data['titulo'],
        'price': product_data['precio'],  # En centavos
        'description': product_data['descripcion'],
        'tags': ','.join(product_data.get('tags', [])),
        'published': 'true' if not CONFIG['test_mode'] else 'false',
        'require_shipping': 'false',
        'content_type': 'digital'
    }
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }
    
    try:
        # Crear producto
        print("📤 Creando producto en Gumroad...")
        response = requests.post(
            'https://api.gumroad.com/v2/products',
            headers=headers,
            data=product_payload,
            timeout=30
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            product_info = response.json()
            
            if 'product' in product_info:
                product_id = product_info['product']['id']
                product_url = product_info['product'].get('short_url', 'URL no disponible')
                
                print(f"✅ Producto creado: {product_id}")
                print(f"🔗 URL: {product_url}")
                
                # Subir archivo PDF si existe
                if pdf_file and os.path.exists(pdf_file):
                    print("📎 Subiendo archivo PDF...")
                    
                    try:
                        with open(pdf_file, 'rb') as f:
                            files = {'content_file': f}
                            upload_response = requests.post(
                                f'https://api.gumroad.com/v2/products/{product_id}/content',
                                headers={'Authorization': f'Bearer {token}'},
                                files=files,
                                timeout=60
                            )
                        
                        if upload_response.status_code == 200:
                            print("✅ PDF subido correctamente")
                        else:
                            print(f"⚠️ Error subiendo PDF: {upload_response.status_code}")
                            print(upload_response.text)
                    
                    except Exception as e:
                        print(f"⚠️ Error subiendo archivo: {e}")
                
                return {
                    'id': product_id,
                    'url': product_url,
                    'title': product_data['titulo'],
                    'price': product_data['precio'] / 100,  # Convertir a euros
                    'created_at': datetime.now().isoformat(),
                    'status': 'published' if not CONFIG['test_mode'] else 'draft'
                }
            else:
                print(f"❌ Respuesta inesperada: {product_info}")
                return None
        else:
            print(f"❌ Error creando producto: {response.status_code}")
            print(f"Response: {response.text}")
            
            # Reintentar en caso de error temporal
            if response.status_code in [429, 500, 502, 503, 504] and attempt < 3:
                wait_
