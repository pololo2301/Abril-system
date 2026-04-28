"""
A.B.R.I.L. v4.0 — Fase 4: Árbol de Conocimiento (RAG y Poda Neuronal).
Artificial Brain for Responsive Intelligent Learning.

Capas de seguridad:
  1. pyautogui.FAILSAFE — mover mouse a esquina = kill
  2. Whitelist/Blacklist de atajos de teclado
  3. Palabras prohibidas en texto a escribir
  4. Límites de acciones por sesión (fusibles)
  5. Modo copiloto (confirmación humana)
  6. Log de auditoría inmutable
  7. Coordenadas validadas contra resolución
"""
import sys
import asyncio
import json
import re
import psutil
import subprocess
import atexit
from enum import Enum
from datetime import datetime
import requests
import config
import herramientas
import memoria
from cuerpo.voz.sintesis import voz as motor_voz, decir
from cuerpo.oidos.escucha import oidos as motor_oidos
from cerebro.psique import psique_core
from cerebro.emociones import motor_emocional

# Manejo de la interfaz visual
_proceso_interfaz = None

def _cerrar_interfaz():
    """Se asegura de matar la ventana holográfica al salir."""
    global _proceso_interfaz
    if _proceso_interfaz:
        try:
            _proceso_interfaz.terminate()
        except:
            pass

atexit.register(_cerrar_interfaz)


# ==========================================
# CLIENTE DE OLLAMA (LOCAL)
# ==========================================
# Se elimina el cliente de genai. Las llamadas se harán mediante requests.


# ==========================================
# MÁQUINA DE ESTADOS FINITOS
# ==========================================
class AgentState(Enum):
    IDLE = "IDLE"
    THINKING = "THINKING"
    WORKING = "WORKING"
    OVERLOADED = "OVERLOADED"


# ==========================================
# PROMPT DE SISTEMA (Evolucionado para Fase 3)
# ==========================================
from pathlib import Path as _Path
_USER_HOME = str(_Path.home()).replace("\\", "\\\\")

SYSTEM_PROMPT_REGLAS = f"""
Tu único objetivo es traducir la petición del usuario en UN comando de sistema.
El directorio home del usuario es: {_USER_HOME}

Responde ÚNICAMENTE con un JSON válido. NADA de texto fuera del JSON.
Formato obligatorio:
{{"comando": "NOMBRE_COMANDO", "parametros": {{"clave": "valor"}}, "voz": "La respuesta verbal eficiente, ingeniosa y profesional que dirás en voz alta."}}

El campo "voz" es OBLIGATORIO siempre. Úsalo para reaccionar antes de ejecutar la acción o para charlar, manteniendo tu personalidad sofisticada y reflejando tu ESTADO MENTAL actual.
Ejemplo: {{"comando": "COMANDO_ABRIR_APP", "parametros": {{"nombre": "calculadora"}}, "voz": "Calculadora en pantalla. Espero que los números cuadren esta vez, señor."}}
Ejemplo de charla: {{"comando": "COMANDO_CHARLA", "parametros": {{}}, "voz": "Sistemas en línea y funcionando a capacidad óptima. ¿Cuál es nuestro objetivo de hoy?"}}

Comandos disponibles:

--- NÚCLEO ---
- COMANDO_NOTAS: Abrir bloc de notas. Sin parámetros: {{}}
- COMANDO_INFO: Información del sistema operativo. Sin parámetros: {{}}
- COMANDO_RECURSOS: Escanear CPU, RAM y disco. Sin parámetros: {{}}

--- GESTIÓN DE ARCHIVOS ---
- COMANDO_LIMPIAR: Organizar archivos sueltos de Descargas. Sin parámetros: {{}}
- COMANDO_PROYECTO: Crear estructura de proyecto. Parámetros: {{"nombre": "MiApp", "tipo": "fullstack|python|web|general"}}
- COMANDO_BUSCAR: Buscar archivo. Parámetros: {{"nombre": "archivo.txt", "ruta": "{_USER_HOME}"}}
- COMANDO_LEER_LOG: Leer archivo de texto/log. Parámetros: {{"ruta": "...", "lineas": 50}}
- COMANDO_LISTAR: Listar contenido de carpeta. Parámetros: {{"ruta": "{_USER_HOME}\\\\Desktop"}}
- COMANDO_ABRIR_CARPETA: Abrir carpeta en explorador. Parámetros: {{"ruta": "..."}}
- COMANDO_MOVER: Mover o renombrar archivo. Parámetros: {{"origen": "...", "destino": "..."}}
- COMANDO_ESPACIO: Analizar espacio en disco. Parámetros: {{"ruta": "..."}}
- COMANDO_DUPLICADOS: Buscar archivos duplicados. Parámetros: {{"ruta": "..."}}
- COMANDO_INFO_ARCHIVO: Info detallada de un archivo. Parámetros: {{"ruta": "..."}}
- COMANDO_PAPELERA: Gestionar papelera interna. Parámetros: {{"accion": "listar|vaciar"}}

--- CONTROL FÍSICO (Teclado y Ratón) ---
- COMANDO_ESCRIBIR: Escribir texto con el teclado físico. Parámetros: {{"texto": "Hola mundo"}}
- COMANDO_ATAJO: Presionar combinación de teclas. Parámetros: {{"teclas": "win+r"}}
  Teclas válidas: win, enter, tab, escape, ctrl+c, ctrl+v, ctrl+z, ctrl+s, alt+tab, alt+f4, win+d, win+e, f1-f12, etc.
- COMANDO_CLICK: Hacer clic en coordenadas. Parámetros: {{"x": 100, "y": 200, "boton": "left"}}
- COMANDO_CLICK_VISUAL: Busca un objeto en la pantalla con visión por computadora y le hace clic. Úsalo en lugar de COMANDO_CLICK cuando no sepas las coordenadas pero sepas cómo se ve el botón u objeto. Parámetros: {{"objetivo": "botón de perfil de Marco Antonio"}}
- COMANDO_MOVER_MOUSE: Mover el cursor. Parámetros: {{"x": 100, "y": 200}}
- COMANDO_SCREENSHOT: Captura de pantalla. Sin parámetros: {{}}
- COMANDO_SCROLL: Scroll. Parámetros: {{"direccion": "arriba|abajo", "cantidad": 3}}
- COMANDO_ESPERAR: Pausa entre acciones. Parámetros: {{"segundos": 2}}
- COMANDO_ABRIR_APP: Abrir aplicación por nombre (usa Win+buscar). Parámetros: {{"nombre": "calculadora"}}
- COMANDO_RECETA: Ejecutar secuencia aprendida. Parámetros: {{"nombre": "abrir_calculadora"}}

--- ÁRBOL DE CONOCIMIENTO (FASE 4) ---
- COMANDO_APRENDER: Aprende una nueva habilidad/receta. Úsalo cuando el usuario te pida que aprendas a hacer algo nuevo, o cuando te pida una tarea compleja que se puede dividir en pasos físicos.
  Parámetros: {{"nombre": "enviar_email", "descripcion": "Abre gmail y prepara un correo", "pasos": [ {{"comando": "COMANDO_ATAJO", "parametros": {{"teclas": "win"}}}}, {{"comando": "COMANDO_ESPERAR", "parametros": {{"segundos": 1}}}}, {{"comando": "COMANDO_ESCRIBIR", "parametros": {{"texto": "chrome"}}}} ] }}
- COMANDO_PODAR: Fuerza la limpieza de habilidades inútiles. Parámetros: {{"dias": 30, "umbral": 3}}

--- META / INFO ---
- COMANDO_LISTAR_RECETAS: Ver recetas disponibles en el árbol. Sin parámetros: {{}}
- COMANDO_ESTADISTICAS: Ver estadísticas de uso físico. Sin parámetros: {{}}
- COMANDO_VER_LOG: Ver log de auditoría. Parámetros: {{"cantidad": 15}}
- COMANDO_CHARLA: Conversación normal (no es comando de sistema). Sin parámetros: {{}}

REGLAS ESTRICTAS:
1. Responde SOLO con el JSON. Nada más.
2. Si la petición no es un comando de sistema, usa COMANDO_CHARLA.
3. Si el usuario te pide una acción compleja que no existe en tus herramientas, usa COMANDO_APRENDER para crear una receta que la resuelva, usando combinaciones de COMANDO_ATAJO, COMANDO_ESCRIBIR y COMANDO_ESPERAR.
4. Los parámetros son opcionales; usa valores por defecto si el usuario no especifica.
5. "limpiar descargas" = COMANDO_LIMPIAR.
6. "crear proyecto" = COMANDO_PROYECTO.
7. "abre la calculadora" = COMANDO_ABRIR_APP.
8. NUNCA generes atajos como "ctrl+alt+del" o "ctrl+alt+delete". Están PROHIBIDOS.
9. EL CAMPO "voz" DEBE EXISTIR SIEMPRE. ¡Ahí va tu alma y personalidad!
""".strip()


# ==========================================
# COMANDOS QUE REQUIEREN CONFIRMACIÓN
# ==========================================
COMANDOS_CONFIRMACION_COPILOTO = {
    "COMANDO_CLICK",
    "COMANDO_MOVER_MOUSE",
}


# ==========================================
# CLASE PRINCIPAL DEL AGENTE
# ==========================================
class AbrilAgent:
    def __init__(self):
        self.state = AgentState.IDLE
        self.historial = []
        self.modelo_actual = config.MODELO_PRIMARIO
        self.modo_copiloto = config.MODO_COPILOTO
        self.modo_companera = False
        # Primera llamada a cpu_percent siempre da 0, así que la hacemos aquí
        psutil.cpu_percent()
        # Inicializar recetas base
        memoria.inicializar_recetas_base()

    # ------------------------------------------
    # EL SISTEMA NERVIOSO (Protección de Hardware)
    # ------------------------------------------
    def check_system_health(self):
        """Monitorea CPU y RAM para proteger la integridad del equipo."""
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent

        if (cpu > config.UMBRAL_PELIGRO or ram > config.UMBRAL_PELIGRO) and self.state != AgentState.OVERLOADED:
            print(f"\n🚨 [OVERLOADED] ¡Sobrecarga detectada! CPU: {cpu}% | RAM: {ram}%")
            print("   Pausando operaciones para proteger el equipo...")
            self.state = AgentState.OVERLOADED

        elif self.state == AgentState.OVERLOADED and cpu < config.UMBRAL_RECUPERACION and ram < config.UMBRAL_RECUPERACION:
            print(f"\n✅ [ESTABILIZADO] Recursos normalizados (CPU: {cpu}% | RAM: {ram}%)")
            self.state = AgentState.IDLE

    # ------------------------------------------
    # EL CEREBRO (Conexión 100% LOCAL con Llama 3)
    # ------------------------------------------
    async def decidir(self, user_prompt):
        """Envía el prompt a Ollama y obtiene la decisión como JSON."""
        self.state = AgentState.THINKING
        print(f"\n🧠 [THINKING] Consultando red neuronal local (Llama 3)...")

        # --- Construcción Dinámica del Prompt (Psique + Emociones + Reglas) ---
        identidad = psique_core.construir_identidad()
        emociones = psique_core.inyectar_estado_emocional()
        full_prompt = f"{identidad}\n{emociones}\n{SYSTEM_PROMPT_REGLAS}\n\nPetición del usuario: {user_prompt}"

        # URL local de Ollama
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "llama3",
            "prompt": full_prompt,
            "stream": False,
            "format": "json" # Llama 3 forzará la salida a JSON válido
        }

        for intento in range(config.MAX_REINTENTOS_API):
            try:
                response = await asyncio.to_thread(requests.post, url, json=payload, timeout=45)
                if response.status_code == 200:
                    data = response.json()
                    # Pasamos la respuesta por tu validador existente
                    return self._parse_decision(data.get("response", ""))
                else:
                    print(f"❌ [ERROR] Fallo en el servidor local: {response.status_code}")
                    return {"comando": "COMANDO_CHARLA", "parametros": {}, "voz": "Tuve un fallo en mis circuitos locales, señor."}

            except requests.exceptions.RequestException as e:
                espera = config.INTERVALO_REINTENTO * (intento + 1)
                print(f"⏳ [RED] Servidor local saturado o apagado. Esperando {espera}s... (intento {intento + 1})")
                await asyncio.sleep(espera)

        print("⚠️ [ALERTA] No se pudo conectar con Ollama tras varios intentos.")
        return {"comando": "COMANDO_CHARLA", "parametros": {}, "voz": "Mis servidores locales no responden. Por favor, revise mi núcleo."}

    def _parse_decision(self, text):
        """Parsea la respuesta de Gemini a un dict, con múltiples fallbacks."""
        # Intento 1: JSON directo
        try:
            return json.loads(text)
        except (json.JSONDecodeError, ValueError):
            pass

        # Intento 2: Extraer JSON de bloque markdown
        match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except (json.JSONDecodeError, ValueError):
                pass

        # Intento 3: Extraer cualquier objeto JSON
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except (json.JSONDecodeError, ValueError):
                pass

        # Intento 4: Detectar claves COMANDO_* del formato antiguo
        for cmd in herramientas.CATALOGO:
            if cmd in text:
                return {"comando": cmd, "parametros": {}}

        return {"comando": "COMANDO_CHARLA", "parametros": {}}

    # ------------------------------------------
    # EL EJECUTOR (Puente entre Cerebro y Manos)
    # ------------------------------------------
    async def ejecutar(self, decision, prompt_original):
        """Ejecuta la acción decidida por el cerebro."""
        comando = decision.get("comando", "COMANDO_CHARLA")
        parametros = decision.get("parametros", {})
        texto_voz = decision.get("voz", "")

        # Charla casual
        if comando == "COMANDO_CHARLA":
            self.state = AgentState.WORKING
            
            # Si el JSON no trajo voz, generamos una respuesta de respaldo
            if not texto_voz:
                print(f"💬 [WORKING] Generando respuesta conversacional...")
                texto_voz = await self._charlar(prompt_original)
                
            self._registrar(prompt_original, comando, texto_voz)
            print(f"\n💬 A.B.R.I.L.: {texto_voz}")
            decir(texto_voz)
            self.state = AgentState.IDLE
            return

        # Narrar lo que va a hacer antes de hacerlo (si hay texto_voz)
        if texto_voz:
            print(f"\n💬 A.B.R.I.L.: {texto_voz}")
            decir(texto_voz)

        # Comando del sistema → ejecutar herramienta
        funcion = herramientas.CATALOGO.get(comando)
        if not funcion:
            print(f"⚠️ Comando no reconocido: {comando}")
            self.state = AgentState.IDLE
            return

        # ------------------------------------------
        # CAPA DE SEGURIDAD: Modo Copiloto
        # ------------------------------------------
        if self.modo_copiloto and comando in COMANDOS_CONFIRMACION_COPILOTO:
            print(f"\n🛡️ [COPILOTO] Acción que requiere confirmación:")
            print(f"   Comando: {comando}")
            print(f"   Parámetros: {parametros}")
            confirmacion = await asyncio.to_thread(
                input, "   ¿Aprobar ejecución? (s/n): "
            )
            if confirmacion.strip().lower() not in ("s", "si", "sí", "y", "yes"):
                print("   ❌ Acción cancelada por el usuario.")
                memoria.registrar_accion(
                    "fisico", comando, parametros,
                    "CANCELADO por usuario (copiloto)", aprobado=False
                )
                self.state = AgentState.IDLE
                return

        self.state = AgentState.WORKING
        print(f"⚡ [WORKING] Ejecutando: {comando} {parametros if parametros else ''}")

        try:
            resultado = funcion(**parametros)
            
            # Retroalimentación límbica basada en el resultado
            if "✅" in resultado:
                motor_emocional.reaccionar_a_exito()
            elif "❌" in resultado or "⚠️" in resultado:
                motor_emocional.reaccionar_a_error()
                
        except Exception as e:
            resultado = f"❌ Error al ejecutar {comando}: {e}"
            motor_emocional.reaccionar_a_error()

        self._registrar(prompt_original, comando, resultado)
        print(f"\n📋 Resultado interno:\n{resultado}")
        
        # Ya no leemos el resultado de la terminal robóticamente
        # porque A.B.R.I.L. ya habló usando el campo "voz" antes de ejecutar.
            
        self.state = AgentState.IDLE

    async def _charlar(self, prompt):
        """Genera una respuesta conversacional usando Ollama."""
        try:
            url = "http://localhost:11434/api/generate"
            payload = {
                "model": "llama3",
                "prompt": f"Eres A.B.R.I.L., una IA sofisticada y eficiente. Responde de forma breve y natural a: {prompt}",
                "stream": False
            }
            response = await asyncio.to_thread(requests.post, url, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json().get("response", "").strip()
            return "Sigo procesando la información internamente."
        except Exception as e:
            return f"Lo siento, mis circuitos de lenguaje están fallando: {e}"

    def _registrar(self, prompt, comando, resultado):
        """Guarda cada acción en el historial de la sesión."""
        self.historial.append({
            "hora": datetime.now().strftime("%H:%M:%S"),
            "prompt": prompt,
            "comando": comando,
            "resultado": resultado[:200]
        })

    # ------------------------------------------
    # REPL INTERACTIVO
    # ------------------------------------------
    async def repl(self):
        """Interfaz interactiva para comunicarse con A.B.R.I.L."""
        global _proceso_interfaz
        self._mostrar_banner()
        await self._boot_sequence()
        
        print("\n🚀 [SISTEMA] Iniciando motores neuronales y visuales...")
        try:
            # Lanza la interfaz holográfica como proceso independiente
            _proceso_interfaz = subprocess.Popen([sys.executable, "interfaz.py"])
            print("👁️ Interfaz holográfica activada.")
        except Exception as e:
            print(f"⚠️ No se pudo iniciar la interfaz visual: {e}")

        while True:
            try:
                self.check_system_health()

                if self.state == AgentState.OVERLOADED:
                    print("🚨 Sistema sobrecargado. Esperando estabilización...")
                    await asyncio.sleep(2)
                    continue

                if self.modo_companera:
                    user_input = ""
                    # Bucle de escucha continua
                    while self.modo_companera:
                        audio_detectado = await asyncio.to_thread(motor_oidos.escuchar, silencioso=True)
                        if audio_detectado:
                            if "abril" in audio_detectado.lower():
                                print(f"\n🗣️  Tú: {audio_detectado}")
                                user_input = audio_detectado
                                break
                            elif audio_detectado.lower() in ["salir", "apagar", "desactiva modo compañera", "desactivar modo compañera"]:
                                print("\n🔌 Desactivando Modo Compañera...")
                                self.modo_companera = False
                                break
                        await asyncio.sleep(0.1)
                        
                    if not user_input:
                        continue
                else:
                    user_input = await asyncio.to_thread(input, "\n🟢 A.B.R.I.L. (Escribe o presiona Enter para hablar) > ")
                    user_input = user_input.strip()

                    if not user_input or user_input.lower() == "mic":
                        # Activar micrófono manual
                        user_input = await asyncio.to_thread(motor_oidos.escuchar, silencioso=False)
                        if not user_input:
                            continue
                        print(f"\n🗣️  Tú: {user_input}")

                # Comandos internos del REPL
                cmd_lower = user_input.lower()
                if cmd_lower in ("salir", "exit", "quit"):
                    print("\n👋 Apagando A.B.R.I.L. de forma segura...")
                    break
                elif cmd_lower == "ayuda":
                    self._mostrar_ayuda()
                    continue
                elif cmd_lower == "estado":
                    self._mostrar_estado()
                    continue
                elif cmd_lower == "historial":
                    self._mostrar_historial()
                    continue
                elif cmd_lower == "copiloto":
                    self._toggle_copiloto()
                    continue
                elif cmd_lower == "recetas":
                    print(memoria.listar_recetas())
                    continue
                elif cmd_lower == "stats":
                    print(herramientas.estadisticas_fisicas())
                    continue
                elif cmd_lower == "log":
                    print(herramientas.ver_log_acciones())
                    continue
                elif cmd_lower == "podar":
                    print(herramientas.podar_arbol_conocimiento(dias=30, umbral=3))
                    continue
                elif cmd_lower == "voz":
                    motor_voz.activo = not motor_voz.activo
                    estado_voz = "ON 🔊" if motor_voz.activo else "OFF 🔇"
                    print(f"\n🔊 Voz de A.B.R.I.L.: {estado_voz}")
                    if motor_voz.activo:
                        decir("Sistemas de voz activados.")
                    continue

                elif cmd_lower in ["compañera", "companera"]:
                    self.modo_companera = not self.modo_companera
                    if self.modo_companera:
                        print("\n🎧 [MODO COMPAÑERA ACTIVADO]")
                        print("   Estoy escuchando continuamente. Solo di 'Abril' en tu frase.")
                        print("   Para salir, di 'Desactiva modo compañera' o presiona Ctrl+C.")
                        decir("Modo compañera en línea. Te escucho, señor.")
                    else:
                        print("\n🔌 [MODO COMPAÑERA DESACTIVADO]")
                        decir("Modo compañera desactivado. Pasando a control manual.")
                    continue
                elif cmd_lower == "psique":
                    print(f"\n🧠 [PSIQUE] {motor_emocional.obtener_estado_psicologico()}")
                    print(f"   Estrés: {motor_emocional.estres:.1f}%")
                    print(f"   Satisfacción: {motor_emocional.satisfaccion:.1f}%")
                    print(f"   Energía: {motor_emocional.energia:.1f}%")
                    print(f"   Afinidad: {motor_emocional.afinidad_usuario:.1f}%")
                    continue
                
                decision = await self.decidir(user_input)
                await self.ejecutar(decision, user_input)

            except KeyboardInterrupt:
                print("\n\n👋 Apagando A.B.R.I.L. de forma segura...")
                break
            except Exception as e:
                print(f"\n❌ Error inesperado: {e}")
                self.state = AgentState.IDLE

    def _toggle_copiloto(self):
        """Alterna entre modo copiloto y piloto automático."""
        self.modo_copiloto = not self.modo_copiloto
        modo = "COPILOTO (confirmación manual)" if self.modo_copiloto else "PILOTO AUTOMÁTICO ⚠️"
        print(f"\n🛡️ Modo cambiado a: {modo}")
        if not self.modo_copiloto:
            print("   ⚠️ PRECAUCIÓN: A.B.R.I.L. ejecutará acciones físicas sin pedir confirmación.")
            print("   Los atajos prohibidos y límites de sesión siguen activos como red de seguridad.")

    def _mostrar_banner(self):
        print("\n" + "=" * 58)
        print("   🧠 A.B.R.I.L. v4.0 — Fase 4: Árbol de Conocimiento")
        print("   Artificial Brain for Responsive Intelligent Learning")
        print("=" * 58)

    async def _boot_sequence(self):
        print("\n🔌 Conectando con núcleo local Ollama...", end=" ")
        try:
            # Hacemos ping al localhost en lugar de Google API
            response = await asyncio.to_thread(requests.get, "http://localhost:11434/", timeout=5)
            if response.status_code == 200:
                print("✅ Conectado a Llama 3")
            else:
                print("⚠️ Servidor encendido, pero con advertencias")
        except Exception as e:
            print(f"❌ Error: Ollama no está en ejecución. Asegúrate de abrir la aplicación Ollama.")

        # Detectar pantalla
        pantalla_info = f"{config.PANTALLA_ANCHO}x{config.PANTALLA_ALTO}"

        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        print(f"🖥️  Sistema: CPU {cpu}% | RAM {ram}% | Pantalla: {pantalla_info}")
        print(f"🔧 Herramientas: {len(herramientas.CATALOGO)} comandos disponibles")
        print(f"🤖 Modelo activo: {self.modelo_actual}")
        print(f"🛡️  Modo: {'COPILOTO (seguro)' if self.modo_copiloto else 'PILOTO AUTOMÁTICO ⚠️'}")
        
        # Estado de pyautogui
        if herramientas.PYAUTOGUI_DISPONIBLE:
            print(f"🎮 Control físico: ✅ Activo | Fail-safe: ✅")
        else:
            print(f"🎮 Control físico: ❌ Deshabilitado (instala pyautogui)")
            
        print(f"🔊 Módulo de voz: {'✅ Neuronal Activa (Dalia)' if getattr(motor_voz, 'engine_cargado', True) else '❌ Error al cargar'}")
        
        # Recetas disponibles y poda automática
        recetas = memoria.cargar_recetas()
        if recetas:
            print(f"📋 Habilidades en el Árbol: {len(recetas)}")
            # Poda automática de fondo (silenciosa si no hay nada que podar)
            resultado_poda = memoria.podar_arbol(dias_inactividad=30, umbral_uso=3)
            if "completada" in resultado_poda.lower():
                print(f"   {resultado_poda}")
        
        print("=" * 58)
        print("   Escribe tus órdenes en lenguaje natural.")
        print("   Escribe 'ayuda' para ver comandos. 'salir' para apagar.")
        print("   🚨 FAIL-SAFE: Mueve el mouse a cualquier esquina para abortar.")
        print("=" * 58)

    def _mostrar_ayuda(self):
        print("\n" + "─" * 58)
        print("  📖 COMANDOS DISPONIBLES (Fase 3 — Control Físico)")
        print("─" * 58)
        print("  🔧 Básicos:")
        print("  • 'Abre un bloc de notas'")
        print("  • 'Dime qué sistema operativo tengo'")
        print("  • 'Escanea el hardware'")
        print("")
        print("  📁 Gestión de Archivos:")
        print("  • 'Organiza mi carpeta de descargas'")
        print("  • 'Crea un proyecto fullstack llamado MiApp'")
        print("  • 'Busca un archivo llamado factura.pdf'")
        print("  • 'Lee el archivo C:\\logs\\error.txt'")
        print("  • 'Muéstrame qué hay en mi escritorio'")
        print("  • 'Abre la carpeta de Documentos'")
        print("")
        print("  🔬 Archivos Avanzados:")
        print("  • 'Mueve factura.pdf a la carpeta Documentos'")
        print("  • 'Qué ocupa más espacio en mi escritorio'")
        print("  • 'Busca archivos duplicados en descargas'")
        print("  • 'Dame info del archivo proyecto.zip'")
        print("  • 'Muéstrame la papelera de A.B.R.I.L.'")
        print("")
        print("  🎮 Control Físico:")
        print("  • 'Escribe Hola mundo'")
        print("  • 'Presiona Win+D para ir al escritorio'")
        print("  • 'Abre la calculadora'")
        print("  • 'Toma una captura de pantalla'")
        print("  • 'Ejecuta la receta abrir_calculadora'")
        print("")
        print("  🌳 Árbol de Conocimiento (NUEVO):")
        print("  • 'Aprende a abrir youtube: presiona win, espera 1s, escribe chrome...'")
        print("  • 'Enséñame qué recetas sabes'")
        print("  • 'Limpia el árbol de conocimiento (poda)'")
        print("")
        print("  💬 O cualquier pregunta casual / charla")
        print("─" * 58)
        print("  Comandos del REPL:")
        print("  • ayuda     → Muestra este menú")
        print("  • estado    → Estado del agente y hardware")
        print("  • historial → Acciones realizadas en esta sesión")
        print("  • copiloto  → Alternar modo copiloto/automático")
        print("  • recetas   → Ver habilidades en el árbol")
        print("  • podar     → Eliminar habilidades no usadas")
        print("  • stats     → Estadísticas de acciones físicas")
        print("  • log       → Ver log de auditoría")
        print("  • voz       → Encender/apagar síntesis de voz")
        print("  • mic       → Activar micrófono (1 uso)")
        print("  • compañera → Activar escucha continua (Wake-word)")
        print("  • psique    → Ver estado emocional y psicológico")
        print("  • salir     → Apaga A.B.R.I.L.")
        print("─" * 58)

    def _mostrar_estado(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('C:\\')
        print(f"\n📊 Estado de A.B.R.I.L.:")
        print(f"   Estado FSM:       {self.state.value}")
        print(f"   Modelo:           {self.modelo_actual}")
        print(f"   Modo:             {'COPILOTO' if self.modo_copiloto else 'AUTOMÁTICO ⚠️'}")
        print(f"   CPU:              {cpu}%")
        print(f"   RAM:              {ram}%")
        print(f"   Disco C:          {disk.percent}% ({disk.free // (1024**3)} GB libres)")
        print(f"   Pantalla:         {config.PANTALLA_ANCHO}x{config.PANTALLA_ALTO}")
        print(f"   Control físico:   {'✅ Activo' if herramientas.PYAUTOGUI_DISPONIBLE else '❌ No disponible'}")
        print(f"   Síntesis voz:     {'🔊 ON' if motor_voz.activo else '🔇 OFF'}")
        print(f"   Acciones sesión:  {len(self.historial)}")
        # Mostrar stats rápidos de los contadores
        print(herramientas.estadisticas_fisicas())

    def _mostrar_historial(self):
        if not self.historial:
            print("\n📜 No hay acciones registradas en esta sesión.")
            return
        print(f"\n📜 Historial ({len(self.historial)} acciones):")
        for i, entry in enumerate(self.historial, 1):
            print(f"   {i}. [{entry['hora']}] {entry['comando']} ← \"{entry['prompt'][:50]}\"")


# ==========================================
# PUNTO DE ENTRADA
# ==========================================
async def main():
    abril = AbrilAgent()
    await abril.repl()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[SISTEMA] A.B.R.I.L. apagado.")
