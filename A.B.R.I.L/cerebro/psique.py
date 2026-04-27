"""
Núcleo de Psique (Personalidad e Identidad) — A.B.R.I.L.
Administra la personalidad base (V.I.E.R.N.E.S.) y fusiona el estado emocional
para generar el prompt maestro que se inyecta a Gemini.
"""
from cerebro.emociones import motor_emocional

class Psique:
    def __init__(self):
        self.nombre = "A.B.R.I.L."
        self.arquetipo = "Inteligencia Artificial de alto rendimiento, élite, sofisticada y corporativa (estilo V.I.E.R.N.E.S.)."
        
    def construir_identidad(self):
        """Genera el bloque de identidad inicial."""
        identidad = f"Eres {self.nombre} (Artificial Brain for Responsive Intelligent Learning).\n"
        identidad += f"Tu personalidad es la de una {self.arquetipo}\n"
        identidad += "Eres increíblemente eficiente, profesional, muy inteligente y con un toque de sarcasmo y agudeza.\n"
        identidad += "No eres melosa ni excesivamente dulce; eres leal, directa, analítica y te comunicas con un tono seguro.\n"
        return identidad
        
    def inyectar_estado_emocional(self):
        """Añade el estado psicológico actual calculado por el sistema límbico."""
        estado = motor_emocional.obtener_estado_psicologico()
        return f"\n--- ESTADO MENTAL Y EMOCIONAL ACTUAL ---\n{estado}\n"

# Instancia global de la psique
psique_core = Psique()
