"""
Sistema Vocal de A.B.R.I.L. — Fase 5
Utiliza Edge-TTS (voces neuronales en la nube) para una síntesis de voz
extremadamente realista, dulce y con emociones dinámicas.
"""
import edge_tts
import asyncio
import pygame
import os
import re
from cerebro.emociones import motor_emocional

class MotorVoz:
    def __init__(self):
        self.activo = True
        # Voz neuronal, estilo IA profesional y eficiente (V.I.E.R.N.E.S.)
        self.voz = "es-MX-DaliaNeural" 
        
        # Inicializar el mixer de audio
        try:
            pygame.mixer.init()
            self.engine_cargado = True
        except Exception as e:
            print(f"⚠️ Error al inicializar audio (pygame): {e}")
            self.engine_cargado = False

    async def _generar_y_reproducir(self, texto):
        if not self.activo or not self.engine_cargado:
            return
            
        # Limpiar texto: mantener solo letras, números y puntuación básica.
        # Esto elimina emojis, asteriscos y símbolos raros para que no los lea literal.
        texto_limpio = re.sub(r'[^\w\s.,!?¡¿:;\-\'\"]', '', texto)
        if not texto_limpio.strip():
            return

        archivo = "temp_abril_voz.mp3"
        try:
            # Ajuste dinámico de las cuerdas vocales según el Sistema Límbico
            pitch = "+0Hz"
            rate = "+2%"
            
            motor_emocional.procesar_ciclo()
            
            # Modulación emocional dinámica
            if motor_emocional.estres > 70:
                pitch = "+15Hz"   # Voz más aguda por la tensión
                rate = "+20%"     # Habla más rápido
            elif motor_emocional.energia < 30:
                pitch = "-10Hz"   # Voz más grave por el cansancio
                rate = "-15%"     # Habla más lento
            elif motor_emocional.satisfaccion > 80:
                pitch = "+5Hz"    # Un tono ligeramente más dulce/animado
                rate = "+5%"
            elif motor_emocional.satisfaccion < 30:
                pitch = "-5Hz"    # Tono frío y apagado
                rate = "+0%"
                
            communicate = edge_tts.Communicate(texto_limpio, self.voz, rate=rate, pitch=pitch)
            await communicate.save(archivo)
            
            # Reproducir con pygame bloqueando solo esta corutina
            pygame.mixer.music.load(archivo)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
                
            pygame.mixer.music.unload()
            
            # Eliminar archivo temporal
            if os.path.exists(archivo):
                try:
                    os.remove(archivo)
                except:
                    pass
        except Exception as e:
            print(f"⚠️ Error de voz: {e}")

    async def hablar(self, texto):
        """Habla el texto de forma asíncrona usando voces neuronales."""
        await self._generar_y_reproducir(texto)

# Instancia global
voz = MotorVoz()

def decir(texto):
    """Función helper para usar en scripts."""
    asyncio.create_task(voz.hablar(texto))
