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
    """Decorador que verifica si pyautogui está disponible."""
    def wrapper(**kwargs):
        if not PYAUTOGUI_DISPONIBLE:
            return "❌ pyautogui no está instalado. Ejecuta: py -m pip install pyautogui"
        return func(**kwargs)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper

def _texto_es_seguro(texto):
    """Verifica que el texto no contenga comandos peligrosos."""
    texto_lower = texto.lower()
    for prohibida in config.PALABRAS_PROHIBIDAS_TEXTO:
        if prohibida.lower() in texto_lower:
            return False, f"Palabra prohibida detectada: '{prohibida}'"
    return True, ""

def _atajo_es_seguro(teclas_str):
    """Verifica que el atajo de teclado esté en la whitelist."""
    teclas_norm = teclas_str.lower().strip()
    
    # Blacklist absoluta — nunca se ejecuta
    if teclas_norm in config.ATAJOS_PROHIBIDOS:
        return False, f"🚫 Atajo PROHIBIDO por seguridad: {teclas_str}"
    
    # Whitelist — si está en la lista, pasa directo
    if teclas_norm in config.ATAJOS_PERMITIDOS:
        return True, ""
    
    # Si no está en whitelist ni blacklist, requiere confirmación
    return None, f"Atajo no reconocido: {teclas_str}"

@_requiere_pyautogui
def escribir_texto(**kwargs):
    """Escribe texto físicamente con el teclado, como un humano."""
    texto = kwargs.get("texto", "")
    
    if not texto:
        return "⚠️ No se proporcionó texto para escribir."
    
    # Capa de seguridad: longitud máxima
    if len(texto) > config.MAX_LARGO_TEXTO:
        return f"🚫 Texto demasiado largo ({len(texto)} chars). Máximo: {config.MAX_LARGO_TEXTO}"
    
    # Capa de seguridad: contenido peligroso
    seguro, razon = _texto_es_seguro(texto)
    if not seguro:
        memoria.registrar_accion("fisico", "COMANDO_ESCRIBIR", {"texto": texto}, f"BLOQUEADO: {razon}", aprobado=False)
        return f"🚫 [BLOQUEADO] {razon}"
    
    # Capa de seguridad: límite de sesión
    if not _contador.puede_escribir(len(texto)):
        return f"🚫 Límite de escritura de sesión alcanzado ({config.MAX_TECLAS_SESION} teclas). Reinicia A.B.R.I.L. para continuar."
    
    print(f"⌨️ [FÍSICO] Escribiendo: '{texto[:50]}{'...' if len(texto) > 50 else ''}'")
    pyautogui.write(texto, interval=0.04)
    
    _contador.registrar_escritura(len(texto))
    memoria.registrar_accion("fisico", "COMANDO_ESCRIBIR", {"texto": texto}, "OK")
    return f"✅ Texto escrito ({len(texto)} caracteres)."

@_requiere_pyautogui
def presionar_atajo(**kwargs):
    """Presiona una combinación de teclas (ej: win+r, ctrl+c, enter)."""
    teclas_str = kwargs.get("teclas", "")
    
    if not teclas_str:
        return "⚠️ No se proporcionó un atajo para presionar."
    
    # Capa de seguridad: validar contra whitelist/blacklist
    resultado_seguridad, razon = _atajo_es_seguro(teclas_str)
    
    if resultado_seguridad is False:
        memoria.registrar_accion("fisico", "COMANDO_ATAJO", {"teclas": teclas_str}, f"PROHIBIDO: {razon}", aprobado=False)
        return f"🚫 [PROHIBIDO] {razon}"
    
    if resultado_seguridad is None:
        # Atajo desconocido — en modo copiloto se pide confirmación
        memoria.registrar_accion("fisico", "COMANDO_ATAJO", {"teclas": teclas_str}, f"REQUIERE_CONFIRMACION: {razon}", aprobado=False)
        return f"⚠️ [REQUIERE CONFIRMACIÓN] {razon}. Atajo no está en la whitelist."
    
    # Capa de seguridad: límite de sesión
    if not _contador.puede_presionar_atajo():
        return f"🚫 Límite de atajos de sesión alcanzado ({config.MAX_ATAJOS_SESION}). Reinicia A.B.R.I.L."
    
    print(f"⌨️ [FÍSICO] Atajo: {teclas_str}")
    teclas = teclas_str.lower().split('+')
    pyautogui.hotkey(*teclas)
    
    _contador.registrar_atajo()
    memoria.registrar_accion("fisico", "COMANDO_ATAJO", {"teclas": teclas_str}, "OK")
    return f"✅ Atajo '{teclas_str}' ejecutado."
