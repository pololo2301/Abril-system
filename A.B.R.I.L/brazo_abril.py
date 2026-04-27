import asyncio
import subprocess
import platform
import psutil
from google import genai
from enum import Enum

# Configuración de A.B.R.I.L.
CLAVE_API = "AIzaSyBtgFaAFpEH4qr-4v6V8xIkHHdTPZR6gTQ" 
client = genai.Client(api_key=CLAVE_API)

class AgentState(Enum):
    IDLE = "IDLE"
    THINKING = "THINKING"
    WORKING = "WORKING"
    OVERLOADED = "OVERLOADED" # Nuevo estado de emergencia

class AbrilAgent:
    def __init__(self):
        self.state = AgentState.IDLE
        self.task_queue = []
        # Inicializamos el sensor de CPU (la primera llamada siempre da 0, así que la hacemos aquí)
        psutil.cpu_percent()

    # ==========================================
    # LAS MANOS DE A.B.R.I.L. (Herramientas OS)
    # ==========================================
    def tool_abrir_bloc_notas(self):
        print("⚙️ [SISTEMA] Abriendo el Bloc de Notas...")
        subprocess.Popen(['notepad.exe']) 
        return "Bloc de notas abierto."

    def tool_reporte_sistema(self):
        print("⚙️ [SISTEMA] Generando reporte de arquitectura...")
        os_info = platform.system() + " " + platform.release()
        return f"Sistema operativo: {os_info}. Todo en orden."

    def tool_escaner_hardware(self):
        print("⚙️ [SISTEMA] Escaneando sensores de la placa base...")
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        return f"Consumo actual -> CPU: {cpu}% | RAM: {ram}%"

    def tool_desconocida(self):
        print("⚠️ [SISTEMA] Acción no reconocida o no autorizada.")
        return "Error: Herramienta no disponible."

    # ==========================================
    # EL SISTEMA NERVIOSO (Protección de Hardware)
    # ==========================================
    def check_system_health(self):
        """Monitorea que la PC no se congele durante las tareas"""
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent

        # Si el procesador o la memoria superan el 85%, entra en modo pánico
        if (cpu_usage > 85.0 or ram_usage > 85.0) and self.state != AgentState.OVERLOADED:
            print(f"\n🚨 [A.B.R.I.L. OVERLOADED] ¡Peligro de sobrecarga! CPU: {cpu_usage}% | RAM: {ram_usage}%")
            print("🚨 Pausando operaciones para proteger la integridad del equipo...")
            self.state = AgentState.OVERLOADED

        # Si estaba en pánico y los recursos bajan del 60%, vuelve a la normalidad
        elif self.state == AgentState.OVERLOADED and cpu_usage < 60.0 and ram_usage < 60.0:
            print(f"\n✅ [A.B.R.I.L. ESTABILIZADO] Recursos liberados (CPU: {cpu_usage}%). Retomando el trabajo.")
            self.state = AgentState.IDLE

    # ==========================================
    # EL CEREBRO (Conexión Resiliente)
    # ==========================================
    async def ask_gemini(self, user_prompt):
        self.state = AgentState.THINKING
        print(f"\n🧠 [A.B.R.I.L. THINKING] Analizando petición: '{user_prompt}'")
        
        system_instruction = """
        Eres A.B.R.I.L. (Artificial Brain for Responsive Intelligent Learning).
        Tu objetivo es traducir la petición del usuario en comandos de sistema.
        Responde ÚNICAMENTE con una de las siguientes claves:
        - COMANDO_NOTAS (si piden escribir o abrir el bloc)
        - COMANDO_INFO (si preguntan por el sistema operativo)
        - COMANDO_RECURSOS (si piden escanear hardware, RAM, procesador o rendimiento)
        - COMANDO_NULO (si es charla o no sabes qué hacer)
        """
        
        full_prompt = f"{system_instruction}\n\nPetición del usuario: {user_prompt}"
        
        # Lógica de reintento para evitar el Error 429
        for intento in range(3):
            try:
                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model='gemini-3-flash-preview',
                    contents=full_prompt
                )
                return response.text.strip()
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    espera = 15 * (intento + 1)
                    print(f"⏳ [A.B.R.I.L. RED] Límite de API. Esperando {espera}s...")
                    await asyncio.sleep(espera)
                else:
                    return "COMANDO_NULO"
        return "COMANDO_NULO"

    # ==========================================
    # EL EJECUTOR
    # ==========================================
    async def execute_action(self, decision_key):
        if decision_key == "COMANDO_NULO":
            print("✅ [A.B.R.I.L. IDLE] Petición ignorada o no procesable.\n")
            self.state = AgentState.IDLE
            return

        self.state = AgentState.WORKING
        print(f"⚡ [A.B.R.I.L. WORKING] Decisión tomada: {decision_key}")
        
        herramientas = {
            "COMANDO_NOTAS": self.tool_abrir_bloc_notas,
            "COMANDO_INFO": self.tool_reporte_sistema,
            "COMANDO_RECURSOS": self.tool_escaner_hardware,
        }
        
        funcion = herramientas.get(decision_key, self.tool_desconocida)
        resultado = funcion()
        print(f"✅ [A.B.R.I.L. IDLE] Resultado: {resultado}\n")
        self.state = AgentState.IDLE

    async def run(self):
        print("🖥️  A.B.R.I.L. en línea. Esperando órdenes...")
        while True:
            # 1. El agente revisa sus propios signos vitales en cada ciclo
            self.check_system_health()

            # 2. Si está sobrecargado, no hace nada, solo espera a que el hardware se enfríe
            if self.state == AgentState.OVERLOADED:
                await asyncio.sleep(2)
                continue

            # 3. Si está sano y hay tareas, las ejecuta
            if self.task_queue and self.state == AgentState.IDLE:
                task = self.task_queue.pop(0)
                decision = await self.ask_gemini(task)
                await self.execute_action(decision)
            
            await asyncio.sleep(0.5)

# Punto de entrada
async def main():
    abril = AbrilAgent()
    
    # Probando la nueva herramienta
    abril.task_queue.append("A.B.R.I.L., revisa cómo vamos de procesador y memoria en este momento.")
    
    await abril.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[SISTEMA] Apagando a A.B.R.I.L. de forma segura...")