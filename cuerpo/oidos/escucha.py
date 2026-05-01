"""
Sistema Auditivo de A.B.R.I.L. — Fase 6: Modo Llamada
Utiliza SpeechRecognition para convertir voz a texto.
Soporta dos modos:
  1. Escucha puntual (una sola frase).
  2. Escucha continua tipo "llamada" (wake-word: "abril").

Seguridad:
  - Timeout en la escucha para no bloquear indefinidamente.
  - Calibración automática de ruido ambiental.
  - Manejo robusto de errores de red y micrófono.
"""
import speech_recognition as sr
import time


class Oidos:
    """
    Motor de reconocimiento de voz que convierte audio del micrófono a texto.
    Usa Google Web Speech API (gratis, sin key).
    """
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microfono = sr.Microphone()
        self._calibrado = False
        # Calibración inicial del ruido ambiental
        try:
            with self.microfono as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self._calibrado = True
        except Exception as e:
            print(f"⚠️ [OIDOS] Error al calibrar micrófono: {e}")

    def recalibrar(self):
        """Recalibra el umbral de ruido ambiental (útil si cambia el entorno)."""
        try:
            with self.microfono as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self._calibrado = True
        except Exception as e:
            print(f"⚠️ [OIDOS] Error al recalibrar: {e}")

    def escuchar(self, silencioso=False, timeout=5, phrase_limit=15):
        """
        Activa el micrófono y devuelve el texto reconocido.

        Args:
            silencioso (bool): Si True, no imprime mensajes en consola.
            timeout (int): Segundos máximos esperando que el usuario empiece a hablar.
            phrase_limit (int): Segundos máximos de duración de la frase.

        Returns:
            str: Texto reconocido, o cadena vacía si no se detectó nada.
        """
        with self.microfono as source:
            if not silencioso:
                print("\n🎤 [ESCUCHANDO] Habla ahora...")
            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_limit
                )
                if not silencioso:
                    print("⏳ [PROCESANDO VOZ] Entendiendo...")

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

    def escuchar_continuo(self, wake_word="abril", callback=None, on_stop=None):
        """
        Modo llamada: escucha continuamente en segundo plano.
        Cuando detecta el wake-word, captura la frase completa y la pasa al callback.

        Args:
            wake_word (str): Palabra clave para activar la escucha.
            callback (callable): Función a llamar con el texto reconocido.
                                 Firma: callback(texto: str) -> None
            on_stop (callable): Función que retorna True si se debe detener el bucle.

        Returns:
            None (bucle infinito hasta que on_stop() retorne True).
        """
        print(f"\n📞 [MODO LLAMADA] Escucha continua activada.")
        print(f"   Di '{wake_word}' seguido de tu petición.")
        print(f"   Ejemplo: '{wake_word}, abre la calculadora'")
        print(f"   Di 'apagar' o 'desconectar' para salir.\n")

        while True:
            # Verificar condición de parada
            if on_stop and on_stop():
                break

            texto = self.escuchar(silencioso=True, timeout=2, phrase_limit=15)

            if not texto:
                continue

            texto_lower = texto.lower().strip()

            # Comandos de salida directa
            if texto_lower in ["apagar", "desconectar", "salir", "desactiva modo llamada"]:
                print("\n📞 [MODO LLAMADA] Desconectando...")
                break

            # Detectar wake-word en cualquier parte de la frase
            if wake_word.lower() in texto_lower:
                print(f"\n  Tú: {texto}")
                if callback:
                    callback(texto)
            else:
                # Si no tiene wake-word, ignorar silenciosamente
                pass

            time.sleep(0.05)  # Micro-pausa para no saturar CPU


# Instancia global
oidos = Oidos()
