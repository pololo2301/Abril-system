"""
Configuración central de A.B.R.I.L.
Todas las constantes y la conexión con la API se manejan desde aquí.
"""
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Si dotenv no está instalado, usamos env vars directamente

# ==========================================
# API KEY (opcional — solo para funciones cloud futuras)
# ==========================================
CLAVE_API = os.environ.get("ABRIL_API_KEY")
if not CLAVE_API:
    # Ya no es crítico: el cerebro principal corre en LM Studio (local).
    # Solo se necesitaría para funciones cloud futuras (visión, imagen, etc.)
    CLAVE_API = None

# ==========================================
# MODELOS (LM Studio — Local GPU)
# ==========================================
MODELO_PRIMARIO = "llama-3.2-3b-instruct"  # Modelo principal en LM Studio (RX 580)
MODELO_FALLBACK = "llama-3.2-3b-instruct"  # Fallback (mismo modelo por ahora)
# Los siguientes son para funciones cloud futuras (requieren CLAVE_API):
MODELO_PRO = "gemini-3.1-pro"
MODELO_VISION = "gemini-2.5-pro"
MODELO_IMAGEN = "imagen-3.0-generate-001"

# ==========================================
# UMBRALES DE SEGURIDAD DE HARDWARE
# ==========================================
UMBRAL_PELIGRO = 85.0        # % máximo antes de entrar en OVERLOADED
UMBRAL_RECUPERACION = 60.0   # % mínimo para salir de OVERLOADED

# ==========================================
# RUTAS DEL SISTEMA
# ==========================================
RUTA_BASE = Path(__file__).parent
RUTA_DESCARGAS = Path.home() / "Downloads"
RUTA_PAPELERA = RUTA_BASE / "_papelera"
RUTA_ESCRITORIO = Path.home() / "Desktop"

# ==========================================
# CONFIGURACIÓN DEL AGENTE
# ==========================================
MAX_REINTENTOS_API = 3
INTERVALO_REINTENTO = 15      # segundos base entre reintentos
MAX_RESULTADOS_BUSQUEDA = 15
MAX_CHARS_LECTURA = 5000

# ==========================================
# FASE 3: SEGURIDAD DE CONTROL FÍSICO
# ==========================================

# --- Modo de operación ---
# True = A.B.R.I.L. pide confirmación antes de acciones físicas peligrosas
# False = Modo piloto automático (solo para usuarios avanzados)
MODO_COPILOTO = True

# --- Límites por sesión (fusibles) ---
MAX_TECLAS_SESION = 500        # Máximo de caracteres a escribir por sesión
MAX_CLICS_SESION = 100         # Máximo de clics por sesión
MAX_ATAJOS_SESION = 80         # Máximo de atajos por sesión
MAX_LARGO_TEXTO = 200          # Máximo de caracteres en un solo COMANDO_ESCRIBIR

# --- Pausa de seguridad entre acciones físicas (segundos) ---
PAUSA_ENTRE_ACCIONES = 0.3

# --- Atajos PERMITIDOS (whitelist) ---
# Solo estos atajos pueden ejecutarse sin confirmación del usuario
ATAJOS_PERMITIDOS = {
    # Navegación básica
    "win", "enter", "tab", "escape", "esc", "space",
    "up", "down", "left", "right",
    "backspace", "home", "end", "pageup", "pagedown",
    # Atajos de ventana
    "alt+tab", "win+d", "win+e", "win+r", "win+l",
    "win+tab", "win+shift+s",
    "win+ctrl+d", "win+ctrl+left", "win+ctrl+right",
    "ctrl+z", "ctrl+y",
    "ctrl+c", "ctrl+v", "ctrl+x",
    "ctrl+a", "ctrl+s", "ctrl+n", "ctrl+w",
    "ctrl+t", "ctrl+shift+t",
    "ctrl+f", "ctrl+h",
    "ctrl+p",
    # Función
    "f1", "f2", "f3", "f4", "f5", "f6",
    "f7", "f8", "f9", "f10", "f11", "f12",
    # Alt combos seguros
    "alt+f4",  # Se permite pero con confirmación en modo copiloto
}

# --- Atajos PROHIBIDOS (blacklist absoluta, nunca se ejecutan) ---
ATAJOS_PROHIBIDOS = {
    "ctrl+alt+del", "ctrl+alt+delete",
    "alt+shift+del", "alt+shift+delete",
}

# --- Palabras prohibidas en texto a escribir ---
# Si el texto contiene alguna de estas, se bloquea completamente
PALABRAS_PROHIBIDAS_TEXTO = {
    "format", "rm -rf", "del /f", "del /s", "rmdir",
    "shutdown", "restart", ":(){:|:&};:",
    "reg delete", "taskkill /f",
    "net user", "net localgroup",
    "powershell -enc", "invoke-expression",
    "remove-item -recurse",
}

# --- Rutas protegidas (nunca se navega ni se escribe en ellas) ---
RUTAS_PROTEGIDAS = {
    "C:\\Windows",
    "C:\\Program Files",
    "C:\\Program Files (x86)",
    "C:\\ProgramData",
    "C:\\$Recycle.Bin",
    "C:\\System Volume Information",
    "C:\\Boot",
    "C:\\Recovery",
}

# --- Resolución de pantalla para validar coordenadas ---
# Se detecta automáticamente al inicio, estos son fallback
PANTALLA_ANCHO = 1920
PANTALLA_ALTO = 1080

# --- Ruta de screenshots ---
RUTA_SCREENSHOTS = RUTA_BASE / "_screenshots"
