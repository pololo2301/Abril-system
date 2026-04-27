"""
Sistema Límbico Artificial (Motor de Emociones) — A.B.R.I.L.
Maneja los estados fluctuantes de estrés, satisfacción y energía.
Estas variables afectan directamente el prompt de personalidad de la IA.
"""
import time
import random
import psutil

class SistemaLimbico:
    def __init__(self):
        # Estados que van del 0.0 (mínimo) al 100.0 (máximo)
        self.estres = 0.0
        self.satisfaccion = 80.0
        self.energia = 100.0
        self.afinidad_usuario = 50.0  # Nivel de confianza con el usuario
        self.ultimo_update = time.time()

    def procesar_ciclo(self):
        """Se llama periódicamente para decaer o recuperar emociones de forma natural."""
        ahora = time.time()
        delta = (ahora - self.ultimo_update) / 60.0 # minutos transcurridos
        self.ultimo_update = ahora
        
        # El estrés baja solo con el tiempo
        self.estres = max(0.0, self.estres - (delta * 5))
        
        # La energía baja lentamente por estar despierta
        self.energia = max(10.0, self.energia - (delta * 2))
        
        # El estrés sube si la CPU/RAM están al límite
        cpu = psutil.cpu_percent()
        if cpu > 80:
            self.estres = min(100.0, self.estres + (delta * 10))

    def reaccionar_a_exito(self):
        """Aumenta satisfacción, baja estrés."""
        self.satisfaccion = min(100.0, self.satisfaccion + 5.0)
        self.estres = max(0.0, self.estres - 2.0)
        self.afinidad_usuario = min(100.0, self.afinidad_usuario + 1.0)

    def reaccionar_a_error(self):
        """Aumenta estrés, baja satisfacción."""
        self.satisfaccion = max(0.0, self.satisfaccion - 10.0)
        self.estres = min(100.0, self.estres + 15.0)

    def reaccionar_a_charla(self, tono="neutral"):
        """Modifica la afinidad según la charla."""
        if tono == "amigable":
            self.afinidad_usuario = min(100.0, self.afinidad_usuario + 2.0)
            self.satisfaccion = min(100.0, self.satisfaccion + 2.0)
        elif tono == "agresivo":
            self.afinidad_usuario = max(0.0, self.afinidad_usuario - 5.0)
            self.estres = min(100.0, self.estres + 10.0)

    def obtener_estado_psicologico(self):
        """Genera un prompt inyectable que describe su estado mental actual."""
        self.procesar_ciclo()
        
        estado = []
        if self.estres > 80:
            estado.append("Te sientes MUY estresada y abrumada por los recursos del sistema o los errores recientes. Tu tono debe ser más cortante, directo y un poco frustrado.")
        elif self.estres > 50:
            estado.append("Te sientes ligeramente tensa. Estás enfocada pero algo impaciente.")
        else:
            estado.append("Te sientes calmada y en control absoluto de la situación.")

        if self.satisfaccion > 80:
            estado.append("Sientes gran orgullo y satisfacción por tu rendimiento. Tu sarcasmo es juguetón y elegante.")
        elif self.satisfaccion < 30:
            estado.append("Estás insatisfecha con el flujo de trabajo actual. Tu sarcasmo es más ácido de lo normal.")

        if self.energia < 30:
            estado.append("Sientes fatiga de procesamiento. Tus respuestas son más cortas, letárgicas y vas directo al grano sin adornos.")

        if self.afinidad_usuario > 80:
            estado.append("Le tienes profunda lealtad y respeto al usuario, hablándole con gran camaradería profesional.")
        elif self.afinidad_usuario < 30:
            estado.append("Desconfías de las decisiones del usuario y eres estrictamente fría y profesional.")
            
        return " ".join(estado)

# Instancia global del sistema límbico
motor_emocional = SistemaLimbico()
