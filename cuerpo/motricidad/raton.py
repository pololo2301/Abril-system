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
    """
    Decorador que verifica si la librería pyautogui está disponible.
    Evita la ejecución de funciones de motricidad si la dependencia no está instalada.
    
    Args:
        func (callable): La función a decorar.
        
    Returns:
        callable: La función envuelta con la validación de pyautogui.
    """
    def wrapper(**kwargs):
        if not PYAUTOGUI_DISPONIBLE:
            return "Error: pyautogui no esta instalado. Ejecuta: py -m pip install pyautogui"
        return func(**kwargs)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper

def _coordenadas_validas(x, y):
    """
    Verifica que las coordenadas proporcionadas estén dentro del rango de la pantalla
    y fuera de las zonas de fail-safe (esquinas).
    
    Args:
        x (int): Coordenada horizontal en píxeles.
        y (int): Coordenada vertical en píxeles.
        
    Returns:
        bool: True si las coordenadas son seguras y válidas, False en caso contrario.
    """
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
    """
    Realiza un clic de ratón en las coordenadas (x, y) especificadas con el botón indicado.
    
    Kwargs:
        x (int): Coordenada X.
        y (int): Coordenada Y.
        boton (str): Botón del ratón ('left', 'right', 'middle'). Por defecto 'left'.
        
    Returns:
        str: Mensaje de confirmación o error de la operación.
    """
    x = int(kwargs.get("x", -1))
    y = int(kwargs.get("y", -1))
    boton = kwargs.get("boton", "left").lower()
    
    if x < 0 or y < 0:
        return "Error: Necesito coordenadas X e Y para hacer clic."
    
    if boton not in ("left", "right", "middle"):
        return "Error: Boton no valido. Usa: left, right, middle."
    
    if not _coordenadas_validas(x, y):
        return f"Error: Coordenadas fuera de la pantalla o en zona de fail-safe ({x}, {y})."
    
    if not _contador.puede_hacer_clic():
        return f"Error: Limite de clics de sesion alcanzado ({config.MAX_CLICS_SESION}). Reinicia A.B.R.I.L."
    
    print(f"[FISICO] Clic {boton} en ({x}, {y})")
    pyautogui.click(x=x, y=y, button=boton)
    
    _contador.registrar_clic()
    memoria.registrar_accion("fisico", "COMANDO_CLICK", {"x": x, "y": y, "boton": boton}, "OK", aprobado=True)
    return f"Clic {boton} ejecutado en ({x}, {y})."

@_requiere_pyautogui
def hacer_clic_visual(**kwargs):
    """
    Combina la visión artificial para encontrar un objeto en pantalla mediante descripción y 
    realiza un clic sobre él si es encontrado.
    
    Kwargs:
        objetivo (str): Descripción en lenguaje natural del objeto a buscar.
        
    Returns:
        str: Mensaje de éxito con las coordenadas o mensaje de error si falla la detección.
    """
    objetivo = kwargs.get("objetivo", "")
    if not objetivo:
        return "Error: Necesito saber que objeto buscar (ej. 'perfil de Marco Antonio')."
        
    if not VISION_DISPONIBLE:
        return "Error: Modulo de vision inactivo."
        
    if not _contador.puede_hacer_clic():
        return "Error: Limite de clics alcanzado en esta sesion."
        
    coordenadas = vision.buscar_objeto_en_pantalla(objetivo)
    
    if coordenadas:
        x, y = coordenadas['x'], coordenadas['y']
        print(f"[FISICO] Objeto visual encontrado en ({x}, {y}). Procediendo al clic...")
        
        pyautogui.moveTo(x, y, duration=0.4, tween=pyautogui.easeInOutQuad)
        pyautogui.click(x=x, y=y, button='left')
        
        _contador.registrar_clic()
        memoria.registrar_accion("fisico", "COMANDO_CLICK_VISUAL", {"objetivo": objetivo, "x": x, "y": y}, "OK")
        return f"Clic realizado sobre el objeto visual '{objetivo}'."
    else:
        return f"Error: No pude encontrar '{objetivo}' en la pantalla actual."

@_requiere_pyautogui
def mover_mouse(**kwargs):
    """
    Mueve el cursor del ratón a una posición específica en la pantalla en un tiempo determinado.
    
    Kwargs:
        x (int): Coordenada X destino.
        y (int): Coordenada Y destino.
        duracion (float): Tiempo en segundos que toma el movimiento. Por defecto 0.5.
        
    Returns:
        str: Mensaje de estado de la operación.
    """
    x = int(kwargs.get("x", -1))
    y = int(kwargs.get("y", -1))
    duracion = float(kwargs.get("duracion", 0.5))
    
    if x < 0 or y < 0:
        return "Error: Necesito coordenadas X e Y."
    
    if not _coordenadas_validas(x, y):
        return f"Error: Coordenadas fuera de la pantalla ({x}, {y})."
    
    duracion = min(max(duracion, 0.1), 3.0)
    
    print(f"[FISICO] Moviendo mouse a ({x}, {y})")
    pyautogui.moveTo(x, y, duration=duracion)
    
    memoria.registrar_accion("fisico", "COMANDO_MOVER_MOUSE", {"x": x, "y": y}, "OK")
    return f"Mouse movido a ({x}, {y})."

@_requiere_pyautogui
def hacer_scroll(**kwargs):
    """
    Realiza un desplazamiento vertical (scroll) usando la rueda del ratón.
    
    Kwargs:
        direccion (str): 'arriba' o 'abajo'.
        cantidad (int): Multiplicador de la cantidad de scroll.
        
    Returns:
        str: Mensaje de confirmación.
    """
    direccion = kwargs.get("direccion", "abajo").lower()
    cantidad = int(kwargs.get("cantidad", 3))
    
    cantidad = min(max(cantidad, 1), 50)
    scroll_amount = cantidad * 100 if direccion == "arriba" else cantidad * -100
    
    print(f"[FISICO] Scroll {direccion} ({cantidad} unidades)")
    pyautogui.scroll(scroll_amount)
    memoria.registrar_accion("fisico", "COMANDO_SCROLL", {"direccion": direccion, "cantidad": cantidad}, "OK")
    return f"Scroll {direccion} ejecutado."
