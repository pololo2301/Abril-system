"""
Sistema de Visión Artificial de A.B.R.I.L. — Fase 6
Utiliza Pillow, OpenCV y modelos multimodales de Gemini para "ver" la pantalla,
encontrar objetos, perfiles o botones, y devolver sus coordenadas.
"""
import os
import io
from PIL import ImageGrab, Image
import config

try:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=config.CLAVE_API)
except ImportError:
    client = None

def capturar_pantalla_memoria():
    """
    Toma una captura de la pantalla actual en su totalidad y la devuelve
    como un objeto de imagen en memoria utilizando la librería PIL.
    Ideal para análisis en tiempo real sin escritura a disco.
    
    Returns:
        Image: Objeto de imagen PIL.
    """
    return ImageGrab.grab()

def captura_pantalla(**kwargs):
    """
    Toma una captura de pantalla y la guarda en el disco local para 
    uso futuro o revisión del usuario, registrando la acción en memoria.
    
    Returns:
        str: Mensaje con la ruta del archivo generado o un mensaje de error.
    """
    from datetime import datetime
    import memoria
    config.RUTA_SCREENSHOTS.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"screenshot_{timestamp}.png"
    ruta_completa = config.RUTA_SCREENSHOTS / nombre_archivo
    
    try:
        screenshot = ImageGrab.grab()
        screenshot.save(str(ruta_completa))
        memoria.registrar_accion("fisico", "COMANDO_SCREENSHOT", {}, f"Guardado: {ruta_completa}")
        return f"Captura guardada en: {ruta_completa}"
    except Exception as e:
        return f"Error al tomar captura: {e}"

def buscar_objeto_en_pantalla(objetivo, modelo=config.MODELO_VISION):
    """
    Toma una captura de pantalla actual y le pide al modelo multimodal
    que encuentre las coordenadas de un objetivo específico en la pantalla.
    Utiliza Gemini o el modelo configurado para el análisis visual.
    
    Args:
        objetivo (str): Nombre o descripción de lo que se desea buscar en pantalla.
        modelo (str): Nombre del modelo multimodal a utilizar.
        
    Returns:
        dict o None: Diccionario con coordenadas {'x', 'y'} del centro del objeto, 
                     o None si no se encuentra o falla el análisis.
    """
    if not client:
        print("[VISION] Cliente Gemini no disponible para vision.")
        return None
        
    print(f"[VISION] Escaneando la pantalla en busca de: '{objetivo}'...")
    imagen = capturar_pantalla_memoria()
    ancho, alto = imagen.size
    
    # Prompt diseñado para forzar al modelo a actuar como un detector de objetos
    prompt = f"""
    Eres el módulo de visión por computadora de una IA de alto rendimiento.
    La imagen adjunta es una captura de pantalla de {ancho}x{alto} píxeles.
    Tu objetivo es encontrar: "{objetivo}".
    
    Si lo encuentras, calcula sus coordenadas (X, Y) relativas a la resolución y devuelve el centro de ese objeto.
    Responde ÚNICAMENTE con un JSON válido, sin markdown ni texto adicional.
    Formato: {{"encontrado": true, "x": 1024, "y": 768}}
    Si no está en la pantalla, responde: {{"encontrado": false}}
    """
    
    try:
        response = client.models.generate_content(
            model=modelo,
            contents=[imagen, prompt]
        )
        texto_res = response.text.strip()
        
        # Intentar extraer el JSON
        import json
        import re
        
        # Limpieza básica por si trae markdown
        match = re.search(r'\{.*\}', texto_res, re.DOTALL)
        if match:
            datos = json.loads(match.group(0))
            if datos.get("encontrado"):
                return {"x": datos.get("x"), "y": datos.get("y")}
    except Exception as e:
        print(f"[VISION] Error analizando la imagen: {e}")
        
    return None
