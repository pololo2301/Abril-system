"""
Sistema de Motricidad (Ratón) — A.B.R.I.L.
Maneja el movimiento del cursor, los clics físicos y el scroll.
"""
import config
import memoria

try:
    import pyautogui
    PYAUTOGUI_DISPONIBLE = True
except ImportError:
    PYAUTOGUI_DISPONIBLE = False

try:
    from cuerpo.vista import vision_core as vision
    VISION_DISPONIBLE = True
except ImportError:
    VISION_DISPONIBLE = False

_contador = memoria.ContadorSeguridad()

def _requiere_pyautogui(func):
    """Decorador que verifica si pyautogui está disponible."""
    def wrapper(**kwargs):
        if not PYAUTOGUI_DISPONIBLE:
            return "❌ pyautogui no está instalado. Ejecuta: py -m pip install pyautogui"
        return func(**kwargs)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper

def _coordenadas_validas(x, y):
    """Verifica que las coordenadas estén dentro de la pantalla."""
    if not (0 <= x <= config.PANTALLA_ANCHO and 0 <= y <= config.PANTALLA_ALTO):
        return False
    # Zona de peligro: esquinas (fail-safe de pyautogui)
    margen = 5
    if (x <= margen or x >= config.PANTALLA_ANCHO - margen) and \
       (y <= margen or y >= config.PANTALLA_ALTO - margen):
        return False
    return True

@_requiere_pyautogui
def hacer_clic(**kwargs):
    """Hace clic en coordenadas específicas de la pantalla."""
    x = int(kwargs.get("x", -1))
    y = int(kwargs.get("y", -1))
    boton = kwargs.get("boton", "left").lower()
    
    if x < 0 or y < 0:
        return "⚠️ Necesito coordenadas X e Y para hacer clic."
    
    if boton not in ("left", "right", "middle"):
        return "⚠️ Botón no válido. Usa: left, right, middle."
    
    if not _coordenadas_validas(x, y):
        return f"🚫 Coordenadas fuera de la pantalla o en zona de fail-safe ({x}, {y})."
    
    if not _contador.puede_hacer_clic():
        return f"🚫 Límite de clics de sesión alcanzado ({config.MAX_CLICS_SESION}). Reinicia A.B.R.I.L."
    
    print(f"🖱️ [FÍSICO] Clic {boton} en ({x}, {y})")
    pyautogui.click(x=x, y=y, button=boton)
    
    _contador.registrar_clic()
    memoria.registrar_accion("fisico", "COMANDO_CLICK", {"x": x, "y": y, "boton": boton}, "OK", aprobado=True)
    return f"✅ Clic {boton} ejecutado en ({x}, {y})."

@_requiere_pyautogui
def hacer_clic_visual(**kwargs):
    """Fase 6: Combina visión artificial para encontrar un objeto en pantalla y hacerle clic."""
    objetivo = kwargs.get("objetivo", "")
    if not objetivo:
        return "⚠️ Necesito saber qué objeto buscar (ej. 'perfil de Marco Antonio')."
        
    if not VISION_DISPONIBLE:
        return "❌ Módulo de visión inactivo."
        
    if not _contador.puede_hacer_clic():
        return "🚫 Límite de clics alcanzado en esta sesión."
        
    coordenadas = vision.buscar_objeto_en_pantalla(objetivo)
    
    if coordenadas:
        x, y = coordenadas['x'], coordenadas['y']
        print(f"🎯 [FÍSICO] Objeto visual encontrado en ({x}, {y}). Procediendo al clic...")
        
        pyautogui.moveTo(x, y, duration=0.4, tween=pyautogui.easeInOutQuad)
        pyautogui.click(x=x, y=y, button='left')
        
        _contador.registrar_clic()
        memoria.registrar_accion("fisico", "COMANDO_CLICK_VISUAL", {"objetivo": objetivo, "x": x, "y": y}, "OK")
        return f"✅ Clic realizado sobre el objeto visual '{objetivo}'."
    else:
        return f"❌ No pude encontrar '{objetivo}' en la pantalla actual."

@_requiere_pyautogui
def mover_mouse(**kwargs):
    """Mueve el cursor del ratón a una posición específica."""
    x = int(kwargs.get("x", -1))
    y = int(kwargs.get("y", -1))
    duracion = float(kwargs.get("duracion", 0.5))
    
    if x < 0 or y < 0:
        return "⚠️ Necesito coordenadas X e Y."
    
    if not _coordenadas_validas(x, y):
        return f"🚫 Coordenadas fuera de la pantalla ({x}, {y})."
    
    duracion = min(max(duracion, 0.1), 3.0)
    
    print(f"🖱️ [FÍSICO] Moviendo mouse a ({x}, {y})")
    pyautogui.moveTo(x, y, duration=duracion)
    
    memoria.registrar_accion("fisico", "COMANDO_MOVER_MOUSE", {"x": x, "y": y}, "OK")
    return f"✅ Mouse movido a ({x}, {y})."

@_requiere_pyautogui
def hacer_scroll(**kwargs):
    """Hace scroll arriba o abajo."""
    direccion = kwargs.get("direccion", "abajo").lower()
    cantidad = int(kwargs.get("cantidad", 3))
    
    cantidad = min(max(cantidad, 1), 50)
    scroll_amount = cantidad * 100 if direccion == "arriba" else cantidad * -100
    
    print(f"🖱️ [FÍSICO] Scroll {direccion} ({cantidad} unidades)")
    pyautogui.scroll(scroll_amount)
    memoria.registrar_accion("fisico", "COMANDO_SCROLL", {"direccion": direccion, "cantidad": cantidad}, "OK")
    return f"✅ Scroll {direccion} ejecutado."
