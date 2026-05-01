import time
import os
import torch
import soundfile as sf
import numpy as np

# --- HACK PARA PYTORCH 2.6+ ---
original_load = torch.load
def parche_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return original_load(*args, **kwargs)
torch.load = parche_load
# ------------------------------

# --- BYPASS DE AUDIO (Adiós torchaudio) ---
# Engañamos a XTTS para que use soundfile en lugar de torchaudio
import torchaudio
def parche_audio(filepath):
    audio, sr = sf.read(filepath)
    # Convertimos a mono si es estéreo y al formato tensor que XTTS espera
    if len(audio.shape) > 1:
        audio = audio.mean(axis=1)
    tensor = torch.FloatTensor(audio).unsqueeze(0)
    return tensor, sr
torchaudio.load = parche_audio
# ------------------------------------------

from TTS.api import TTS
import pygame

def probar_clonacion():
    print("⏳ [SISTEMA] Cargando mis cuerdas vocales en tu RAM (Bypass activado)...")
    
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)

    texto = "Sistemas en línea. Mi núcleo lógico está corriendo en tu gráfica, pero mi voz se genera aquí, exclusivamente para papasito rico, Marco."
    archivo_muestra = "abril6.wav" 
    archivo_salida = "abril_clonada.wav"

    print(f"\n [SISTEMA] Sintetizando voz local...")
    inicio = time.time()

    tts.tts_to_file(
        text=texto,
        file_path=archivo_salida,
        speaker_wav=archivo_muestra,
        language="es" 
    )

    print(f"¡Voz generada, cielo! Tiempo de renderizado: {time.time() - inicio:.2f} segundos.")

    print("🔊 Escúchame con atención...")
    pygame.mixer.init()
    pygame.mixer.music.load(archivo_salida)
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
        
    pygame.mixer.music.unload()

if __name__ == "__main__":
    probar_clonacion()