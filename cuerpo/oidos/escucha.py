"""
Sistema Auditivo de A.B.R.I.L. — Fase 5.2
Utiliza SpeechRecognition para convertir voz a texto.
"""
import speech_recognition as sr
from cuerpo.voz.sintesis import decir

class Oidos:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microfono = sr.Microphone()
        # Ajustar el umbral de ruido de fondo una sola vez al inicio
        with self.microfono as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

    def escuchar(self, silencioso=False):
        """Activa el micrófono y devuelve el texto reconocido."""
        with self.microfono as source:
            if not silencioso:
                print("\n🎤 [ESCUCHANDO] Habla ahora...")
            try:
                # Tiempo de escucha ajustado para modo continuo
                audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=10)
                if not silencioso:
                    print("⏳ [PROCESANDO VOZ] Entendiendo...")
                
                # Usar Google Web Speech API (Gratis, no requiere key)
                texto = self.recognizer.recognize_google(audio, language="es-ES")
                return texto
                
            except sr.WaitTimeoutError:
                return ""
            except sr.UnknownValueError:
                if not silencioso:
                    print("⚠️ [MIC] No pude entender lo que dijiste.")
                return ""
            except sr.RequestError as e:
                if not silencioso:
                    print(f"❌ [MIC] Error de red con el servicio de voz: {e}")
                return ""
            except Exception as e:
                if not silencioso:
                    print(f"❌ [MIC] Error inesperado: {e}")
                return ""

# Instancia global
oidos = Oidos()
