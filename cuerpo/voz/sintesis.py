"""
Sistema Vocal de A.B.R.I.L. — Fase 6: Cuerdas Vocales Clonadas (XTTS v2 Local)
Utiliza Coqui XTTS para síntesis de voz local con clonación a partir del ADN
vocal almacenado en abril6.wav. Incluye bypass de compatibilidad para
PyTorch 2.6+ y torchaudio.

Seguridad:
  - Sanitización de texto antes de síntesis (evita inyección de SSML/caracteres
    de control que podrían causar comportamiento inesperado en el modelo TTS).
  - Manejo robusto de errores con cleanup de archivos temporales.
  - Mutex de reproducción para evitar colisiones de audio.
"""
import sys
# Fix encoding para terminales Windows cp1252
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import time
import os
import re
import threading
import torch
import soundfile as sf
import pygame
from pathlib import Path

# --- HACK PARA PYTORCH 2.6+ ---
# PyTorch 2.6 cambió weights_only=True como default, lo cual rompe la carga
# de modelos XTTS que usan pickle. Este parche lo revierte de forma controlada.
_original_torch_load = torch.load
def _parche_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return _original_torch_load(*args, **kwargs)
torch.load = _parche_load

# --- BYPASS DE AUDIO ---
# XTTS depende de torchaudio.load() que puede fallar en ciertas configuraciones.
# Reemplazamos con soundfile que es más estable en Windows.
import torchaudio
def _parche_audio(filepath):
    audio, sr = sf.read(filepath)
    if len(audio.shape) > 1:
        audio = audio.mean(axis=1)
    tensor = torch.FloatTensor(audio).unsqueeze(0)
    return tensor, sr
torchaudio.load = _parche_audio
# -----------------------

from TTS.api import TTS

# Ruta raíz del proyecto (donde está abril6.wav)
_RUTA_PROYECTO = Path(__file__).resolve().parent.parent.parent

# Caracteres permitidos en texto para síntesis (sanitización)
_PATRON_SANITIZACION = re.compile(r'[^\w\s.,!?¡¿:;\-\'"áéíóúñÁÉÍÓÚÑüÜ]')
# Longitud máxima de texto por llamada (protección contra prompts gigantes)
_MAX_LONGITUD_TEXTO = 500


class VozAbril:
    """
    Motor de síntesis de voz clonada usando XTTS v2.
    Carga el modelo una sola vez en RAM al inicializar y reutiliza la instancia
    para todas las llamadas posteriores, minimizando latencia.

    Atributos:
        activo (bool): Permite desactivar la voz sin destruir la instancia.
        engine_cargado (bool): Indica si el modelo TTS se cargó correctamente.
    """
    def __init__(self):
        print("[SISTEMA] Calentando cuerdas vocales XTTS en RAM (Bypass activo)...")
        self.activo = True
        self.engine_cargado = False
        self._lock = threading.Lock()  # Mutex para evitar colisiones de audio

        # Ruta al ADN vocal y archivo de salida temporal
        self.archivo_muestra = str(_RUTA_PROYECTO / "abril6.wav")
        self.archivo_salida = str(_RUTA_PROYECTO / "respuesta_abril.wav")

        # Validar que el archivo de muestra vocal existe
        if not os.path.exists(self.archivo_muestra):
            print(f"[VOZ ERROR] Archivo de muestra vocal no encontrado: {self.archivo_muestra}")
            print("   Sin este archivo, la clonación de voz no funcionará.")
            return

        try:
            # Carga el modelo XTTS v2 una sola vez (consume ~2GB RAM)
            self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
            pygame.mixer.init()
            self.engine_cargado = True
            print("[SISTEMA OK] Modulo de voz clonada en linea.")
        except Exception as e:
            print(f"[VOZ ERROR] Error al cargar modelo XTTS: {e}")
            print("   La voz estará desactivada esta sesión.")

    def _sanitizar_texto(self, texto):
        """
        Limpia el texto antes de enviarlo al modelo TTS.
        Elimina emojis, caracteres de control, SSML tags y limita longitud.
        Esto previene:
          - Inyección de caracteres que causen errores en el modelo.
          - Textos excesivamente largos que congelen el sistema.
        """
        if not texto:
            return ""
        # Eliminar caracteres no permitidos (emojis, símbolos raros, etc.)
        texto_limpio = _PATRON_SANITIZACION.sub('', texto)
        # Colapsar espacios múltiples
        texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
        # Truncar si excede el límite
        if len(texto_limpio) > _MAX_LONGITUD_TEXTO:
            # Cortar en el último punto o espacio antes del límite
            corte = texto_limpio[:_MAX_LONGITUD_TEXTO].rfind('.')
            if corte == -1:
                corte = texto_limpio[:_MAX_LONGITUD_TEXTO].rfind(' ')
            if corte == -1:
                corte = _MAX_LONGITUD_TEXTO
            texto_limpio = texto_limpio[:corte + 1]
        return texto_limpio

    def hablar(self, texto):
        """
        Genera y reproduce audio a partir del texto proporcionado.
        Bloquea el hilo actual hasta que termine la reproducción para evitar
        que el sistema de escucha capture su propia voz (anti-feedback).

        Args:
            texto (str): El texto a sintetizar y reproducir.
        """
        if not self.activo or not self.engine_cargado:
            return
        
        texto_limpio = self._sanitizar_texto(texto)
        if not texto_limpio:
            return

        # El lock evita que dos hilos intenten hablar al mismo tiempo
        with self._lock:
            try:
                print(f"[SINTETIZANDO]: {texto_limpio[:80]}...")
                self.tts.tts_to_file(
                    text=texto_limpio,
                    file_path=self.archivo_salida,
                    speaker_wav=self.archivo_muestra,
                    language="es"
                )

                pygame.mixer.music.load(self.archivo_salida)
                pygame.mixer.music.play()

                # Bloquea mientras habla (anti-feedback con el micrófono)
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

                pygame.mixer.music.unload()

            except Exception as e:
                print(f"[VOZ ERROR]: {e}")
            finally:
                # Limpieza del archivo temporal
                try:
                    if os.path.exists(self.archivo_salida):
                        os.remove(self.archivo_salida)
                except OSError:
                    pass


# --- Instancia global y helpers compatibles con el sistema existente ---
voz = VozAbril()

def decir(texto):
    """
    Función helper síncrona para usar desde cualquier módulo.
    Mantiene compatibilidad con las llamadas existentes en abril.py.
    """
    voz.hablar(texto)
