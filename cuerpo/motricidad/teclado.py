"""
Sistema de Motricidad Fina (Teclado) — A.B.R.I.L.
Maneja la escritura de texto y atajos de teclado con múltiples capas de seguridad.
"""
import config
import memoria

try:
    import pyautogui
    PYAUTOGUI_DISPONIBLE = True
except ImportError:
    PYAUTOGUI_DISPONIBLE = False

# Instancia global del contador para mantener coherencia en la sesión
_contador = memoria.ContadorSeguridad()

def _requiere_pyautogui(func):
    """
    Decorador que asegura que el módulo pyautogui está instalado.
    Si no está, previene que se lance una excepción durante la ejecución.
    
    Args:
        func (callable): La función que controla el teclado.
        
    Returns:
        callable: Función decorada con validación.
    """
    def wrapper(**kwargs):
        if not PYAUTOGUI_DISPONIBLE:
            return "Error: pyautogui no esta instalado. Ejecuta: py -m pip install pyautogui"
        return func(**kwargs)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper

def _texto_es_seguro(texto):
    """
    Verifica que el texto provisto no contenga comandos peligrosos 
    o palabras clave bloqueadas en la configuración.
    
    Args:
        texto (str): La cadena a evaluar.
        
    Returns:
        tuple: (bool, str) donde el bool indica si es seguro, 
               y el str proporciona la razón en caso de fallo.
    """
    texto_lower = texto.lower()
    for prohibida in config.PALABRAS_PROHIBIDAS_TEXTO:
        if prohibida.lower() in texto_lower:
            return False, f"Palabra prohibida detectada: '{prohibida}'"
    return True, ""

def _atajo_es_seguro(teclas_str):
    """
    Verifica que la combinación de teclas (atajo) provista sea segura de ejecutar,
    evaluándola contra una lista negra (prohibidos) y una lista blanca (permitidos).
    
    Args:
        teclas_str (str): Cadena representando el atajo, ej 'ctrl+c'.
        
    Returns:
        tuple: (bool o None, str). True si está en la lista blanca, 
               False si está prohibido, y None si requiere confirmación del usuario.
    """
    teclas_norm = teclas_str.lower().strip()
    
    # Blacklist absoluta — nunca se ejecuta
    if teclas_norm in config.ATAJOS_PROHIBIDOS:
        return False, f"Atajo PROHIBIDO por seguridad: {teclas_str}"
    
    # Whitelist — si está en la lista, pasa directo
    if teclas_norm in config.ATAJOS_PERMITIDOS:
        return True, ""
    
    # Si no está en whitelist ni blacklist, requiere confirmación
    return None, f"Atajo no reconocido: {teclas_str}"

@_requiere_pyautogui
def escribir_texto(**kwargs):
    """
    Escribe texto físicamente con el teclado, simulando a un humano.
    Cuenta con validación de longitud, seguridad del contenido y límite de sesión.
    
    Kwargs:
        texto (str): Cadena de texto a teclear.
        
    Returns:
        str: Confirmación de ejecución o mensaje de bloqueo.
    """
    texto = kwargs.get("texto", "")
    
    if not texto:
        return "Error: No se proporciono texto para escribir."
    
    # Capa de seguridad: longitud máxima
    if len(texto) > config.MAX_LARGO_TEXTO:
        return f"Error: Texto demasiado largo ({len(texto)} chars). Maximo: {config.MAX_LARGO_TEXTO}"
    
    # Capa de seguridad: contenido peligroso
    seguro, razon = _texto_es_seguro(texto)
    if not seguro:
        memoria.registrar_accion("fisico", "COMANDO_ESCRIBIR", {"texto": texto}, f"BLOQUEADO: {razon}", aprobado=False)
        return f"[BLOQUEADO] {razon}"
    
    # Capa de seguridad: límite de sesión
    if not _contador.puede_escribir(len(texto)):
        return f"Error: Limite de escritura de sesion alcanzado ({config.MAX_TECLAS_SESION} teclas). Reinicia A.B.R.I.L. para continuar."
    
    print(f"[FISICO] Escribiendo: '{texto[:50]}{'...' if len(texto) > 50 else ''}'")
    pyautogui.write(texto, interval=0.04)
    
    _contador.registrar_escritura(len(texto))
    memoria.registrar_accion("fisico", "COMANDO_ESCRIBIR", {"texto": texto}, "OK")
    return f"Texto escrito ({len(texto)} caracteres)."

@_requiere_pyautogui
def presionar_atajo(**kwargs):
    """
    Presiona una combinación de teclas específica.
    Implementa capas de seguridad verificando listas blancas, negras 
    y limitando el número de atajos por sesión.
    
    Kwargs:
        teclas (str): Atajo de teclado, ej. 'win+r' o 'enter'.
        
    Returns:
        str: Mensaje indicando el éxito, prohibición o requerimiento de confirmación.
    """
    teclas_str = kwargs.get("teclas", "")
    
    if not teclas_str:
        return "Error: No se proporciono un atajo para presionar."
    
    # Capa de seguridad: validar contra whitelist/blacklist
    resultado_seguridad, razon = _atajo_es_seguro(teclas_str)
    
    if resultado_seguridad is False:
        memoria.registrar_accion("fisico", "COMANDO_ATAJO", {"teclas": teclas_str}, f"PROHIBIDO: {razon}", aprobado=False)
        return f"[PROHIBIDO] {razon}"
    
    if resultado_seguridad is None:
        # Atajo desconocido — en modo copiloto se pide confirmación
        memoria.registrar_accion("fisico", "COMANDO_ATAJO", {"teclas": teclas_str}, f"REQUIERE_CONFIRMACION: {razon}", aprobado=False)
        return f"[REQUIERE CONFIRMACION] {razon}. Atajo no esta en la whitelist."
    
    # Capa de seguridad: límite de sesión
    if not _contador.puede_presionar_atajo():
        return f"Error: Limite de atajos de sesion alcanzado ({config.MAX_ATAJOS_SESION}). Reinicia A.B.R.I.L."
    
    print(f"[FISICO] Atajo: {teclas_str}")
    teclas = teclas_str.lower().split('+')
    pyautogui.hotkey(*teclas)
    
    _contador.registrar_atajo()
    memoria.registrar_accion("fisico", "COMANDO_ATAJO", {"teclas": teclas_str}, "OK")
    return f"Atajo '{teclas_str}' ejecutado."
