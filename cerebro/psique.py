"""
Núcleo de Psique (Personalidad e Identidad) — A.B.R.I.L.
Administra la personalidad base (V.I.E.R.N.E.S.) y fusiona el estado emocional
para generar el prompt maestro que se inyecta a Gemini.
"""
from cerebro.emociones import motor_emocional

class Psique:
    """
    Clase que representa el núcleo de la personalidad e identidad del sistema.
    Almacena los rasgos, nombre y arquetipo, y provee métodos para 
    construir el bloque de identidad y el estado emocional que se enviarán
    como contexto al modelo de lenguaje.
    """
    def __init__(self):
        """
        Inicializa el estado base de la psique, configurando el nombre
        y el arquetipo de personalidad de la IA.
        """
        self.nombre = "A.B.R.I.L."
        self.arquetipo = "Inteligencia Artificial de alto rendimiento, élite, sofisticada y corporativa (estilo V.I.E.R.N.E.S.)."
        
    def construir_identidad(self):
        """
        Genera y retorna el bloque de texto con la identidad inicial.
        Este bloque define cómo debe comportarse el asistente y cuáles 
        son sus rasgos de personalidad clave.
        
        Returns:
            str: Bloque de texto con las instrucciones de identidad.
        """
        identidad = f"Eres {self.nombre} (Artificial Brain for Responsive Intelligent Learning).\n"
        identidad += f"Tu personalidad es la de una {self.arquetipo}\n"
        identidad += "Eres increíblemente eficiente, profesional, muy inteligente y con un toque de sarcasmo y agudeza.\n"
        identidad += "No eres melosa ni excesivamente dulce; eres leal, directa, analítica y te comunicas con un tono seguro.\n"
        return identidad
        
    def inyectar_estado_emocional(self):
        """
        Consulta al motor emocional para obtener el estado psicológico 
        actual y lo formatea para ser añadido al contexto del modelo.
        
        Returns:
            str: Texto representativo del estado emocional actual.
        """
        estado = motor_emocional.obtener_estado_psicologico()
        return f"\n--- ESTADO MENTAL Y EMOCIONAL ACTUAL ---\n{estado}\n"

# Instancia global de la psique
psique_core = Psique()
