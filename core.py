import asyncio
import subprocess
import platform
from google import genai
from enum import Enum

# Configuración de A.B.R.I.L.
CLAVE_API = "" # Asegúrate de poner tu clave válida
client = genai.Client(api_key=CLAVE_API)

class AgentState(Enum):
    IDLE = "IDLE"
    THINKING = "THINKING"
    WORKING = "WORKING"

class AbrilAgent:
    def __init__(self):
        self.state = AgentState.IDLE
        self.task_queue = []

    # ==========================================
    # LAS MANOS DE A.B.R.I.L. (Herramientas OS)
    # ==========================================
    def tool_abrir_bloc_notas(self):
        """Abre una instancia del bloc de notas de forma asíncrona."""
        print("[SISTEMA] Abriendo el Bloc de Notas...")
        # Subprocess abre el programa de forma independiente sin bloquear a A.B.R.I.L.
        subprocess.Popen(['notepad.exe']) 
        return "Bloc de notas abierto."

    def tool_reporte_sistema(self):
        """Genera un reporte básico del sistema operativo subyacente."""
        print("[SISTEMA] Generando reporte de arquitectura...")
        os_info = platform.system() + " " + platform.release()
        return f"Sistema operativo: {os_info}. Todo en orden."

    def tool_desconocida(self):
        """Manejador por defecto para acciones no reconocidas."""
        print("[SISTEMA] Accion no reconocida o no autorizada.")
        return "Error: Herramienta no disponible."

    async def tool_charla_normal(self, user_prompt):
        """
        Envía el prompt del usuario directamente a Gemini para generar 
        una respuesta conversacional natural.
        """
        print("[SISTEMA] Generando respuesta conversacional...")
        # Usamos Gemini nuevamente para responder de forma natural
        try:
            response = await asyncio.to_thread(
                client.models.generate_content,
                model='gemini-3-flash-preview',
                contents=user_prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"[SISTEMA ERROR] No se pudo generar la respuesta conversacional: {e}")
            return "Lo siento, tuve un problema de conexion y no pude procesar la conversacion."

    # ==========================================
    # EL CEREBRO (Conexión con Gemini)
    # ==========================================
    async def ask_gemini(self, user_prompt):
        """
        Consulta al modelo de Gemini para clasificar la intención del usuario
        en un comando predefinido.
        """
        self.state = AgentState.THINKING
        print(f"\n[A.B.R.I.L. THINKING] Analizando peticion: '{user_prompt}'")
        
        # INGENIERÍA DE PROMPTS: Obligamos a la IA a responder como una máquina
        system_instruction = """
        Eres A.B.R.I.L. (Artificial Brain for Responsive Intelligent Learning).
        Tu objetivo es traducir la petición del usuario en comandos de sistema.
        Responde ÚNICAMENTE con una de las siguientes claves, sin formato markdown, sin saludos y sin comillas:
        - COMANDO_NOTAS (si el usuario pide escribir, anotar o abrir el bloc)
        - COMANDO_INFO (si el usuario pregunta por el sistema operativo o estado)
        - COMANDO_NULO (si no sabes qué hacer o es una charla normal)
        """
        
        full_prompt = f"{system_instruction}\n\nPetición del usuario: {user_prompt}"
        
        # --- Lógica de Resiliencia (Manejo del Error 429) ---
        max_reintentos = 3
        for intento in range(max_reintentos):
            try:
                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model='gemini-3-flash-preview',
                    contents=full_prompt
                )
                return response.text.strip()
            
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    espera = 15 * (intento + 1) # Espera 15s, luego 30s, etc.
                    print(f"[A.B.R.I.L. RED] Limite de API alcanzado. Esperando {espera} segundos antes de reintentar...")
                    await asyncio.sleep(espera)
                else:
                    print(f"[A.B.R.I.L. ERROR] Fallo critico en el cerebro: {e}")
                    return "COMANDO_NULO" # Si hay otro error, aborta la tarea de forma segura
                    
        print("[A.B.R.I.L. ALERTA] No se pudo conectar con los servidores tras varios intentos.")
        return "COMANDO_NULO"

    # ==========================================
    # EL EJECUTOR (El puente entre Cerebro y Manos)
    # ==========================================
    async def execute_action(self, decision_key, user_prompt):
        """
        Ejecuta la función correspondiente a la decisión clasificada.
        """
        self.state = AgentState.WORKING
        print(f"[A.B.R.I.L. WORKING] Decision tomada: {decision_key}")
        
        # Evaluamos la decisión y ejecutamos la acción correspondiente
        if decision_key == "COMANDO_NOTAS":
            resultado = self.tool_abrir_bloc_notas()
        elif decision_key == "COMANDO_INFO":
            resultado = self.tool_reporte_sistema()
        elif decision_key == "COMANDO_NULO":
            # Si es charla normal, le pasamos el prompt original para que responda
            resultado = await self.tool_charla_normal(user_prompt)
        else:
            resultado = self.tool_desconocida()
        
        print(f"[A.B.R.I.L. IDLE] Resultado: {resultado}\n")
        self.state = AgentState.IDLE

    async def run(self):
        while True:
            if self.task_queue and self.state == AgentState.IDLE:
                task = self.task_queue.pop(0)
                decision = await self.ask_gemini(task)
                await self.execute_action(decision, task)
            
            # Condición para salir del bucle infinito cuando ya no hay tareas
            if not self.task_queue and self.state == AgentState.IDLE:
                break
                
            await asyncio.sleep(0.5)

# Punto de entrada
async def main():
    abril = AbrilAgent()
    
    # Vamos a probar su capacidad de deducción con dos frases distintas
    abril.task_queue.append("A.B.R.I.L., necesito apuntar una idea rápida, prepárame un lienzo en blanco.")
    abril.task_queue.append("Dime en qué sistema operativo estamos corriendo ahora mismo.")
    abril.task_queue.append("Cuéntame un chiste.") # Esto debería disparar el COMANDO_NULO
    
    await abril.run()

if __name__ == "__main__":
    asyncio.run(main())
