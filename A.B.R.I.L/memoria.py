"""
Sistema de Memoria de A.B.R.I.L. — Fase 3
Gestiona el aprendizaje, recetas de acciones, y auditoría de seguridad.
"""
import json
import os
from datetime import datetime
from pathlib import Path
import config


# ==========================================
# RUTAS DE MEMORIA
# ==========================================
RUTA_MEMORIA = config.RUTA_BASE / "_memoria"
RUTA_LOG_ACCIONES = RUTA_MEMORIA / "log_acciones.jsonl"
RUTA_RECETAS = RUTA_MEMORIA / "recetas.json"
RUTA_ESTADISTICAS = RUTA_MEMORIA / "estadisticas.json"


def _asegurar_carpeta():
    """Crea la carpeta de memoria si no existe."""
    RUTA_MEMORIA.mkdir(exist_ok=True)


# ==========================================
# LOG DE AUDITORÍA (Registro inmutable)
# ==========================================
def registrar_accion(tipo, comando, parametros, resultado, aprobado=True):
    """
    Registra cada acción física ejecutada en un log append-only.
    Esto es el 'black box' de A.B.R.I.L. — nunca se borra.
    """
    _asegurar_carpeta()
    entrada = {
        "timestamp": datetime.now().isoformat(),
        "tipo": tipo,  # "fisico", "sistema", "receta"
        "comando": comando,
        "parametros": parametros,
        "resultado": resultado[:300],
        "aprobado": aprobado
    }
    try:
        with open(RUTA_LOG_ACCIONES, "a", encoding="utf-8") as f:
            f.write(json.dumps(entrada, ensure_ascii=False) + "\n")
    except Exception:
        pass  # El log nunca debe romper la ejecución


def obtener_log_reciente(n=20):
    """Devuelve las últimas N acciones del log."""
    if not RUTA_LOG_ACCIONES.exists():
        return []
    try:
        with open(RUTA_LOG_ACCIONES, "r", encoding="utf-8") as f:
            lineas = f.readlines()
        return [json.loads(l) for l in lineas[-n:]]
    except Exception:
        return []


# ==========================================
# SISTEMA DE RECETAS (Aprendizaje supervisado)
# ==========================================
def cargar_recetas():
    """Carga las recetas aprendidas desde disco."""
    if not RUTA_RECETAS.exists():
        return {}
    try:
        with open(RUTA_RECETAS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def guardar_receta(nombre, descripcion, pasos):
    """
    Guarda una receta nueva (aprender). Cada receta es una secuencia de acciones.
    
    Formato de cada paso:
    {"comando": "COMANDO_ATAJO", "parametros": {"teclas": "win"}}
    """
    _asegurar_carpeta()
    recetas = cargar_recetas()
    recetas[nombre] = {
        "descripcion": descripcion,
        "pasos": pasos,
        "creada": datetime.now().isoformat(),
        "ultima_vez_usada": datetime.now().isoformat(),
        "veces_usada": 0
    }
    with open(RUTA_RECETAS, "w", encoding="utf-8") as f:
        json.dump(recetas, f, ensure_ascii=False, indent=2)
    return f"✅ Receta '{nombre}' guardada en el Árbol de Conocimiento con {len(pasos)} pasos."


def obtener_receta(nombre):
    """Obtiene una receta por nombre."""
    recetas = cargar_recetas()
    return recetas.get(nombre)


def listar_recetas():
    """Lista todas las recetas disponibles en el árbol."""
    recetas = cargar_recetas()
    if not recetas:
        return "📋 El Árbol de Conocimiento está vacío."
    
    resumen = f"🌳 Árbol de Conocimiento ({len(recetas)} habilidades):\n"
    for nombre, datos in recetas.items():
        resumen += f"   🌿 {nombre}: {datos['descripcion']} ({len(datos['pasos'])} pasos, usada {datos['veces_usada']}x)\n"
    return resumen


def incrementar_uso_receta(nombre):
    """Incrementa el contador de uso de una receta y actualiza la última vez usada."""
    recetas = cargar_recetas()
    if nombre in recetas:
        recetas[nombre]["veces_usada"] += 1
        recetas[nombre]["ultima_vez_usada"] = datetime.now().isoformat()
        with open(RUTA_RECETAS, "w", encoding="utf-8") as f:
            json.dump(recetas, f, ensure_ascii=False, indent=2)


def podar_arbol(dias_inactividad=30, umbral_uso=3):
    """
    Poda el árbol de conocimiento: elimina ramas (recetas) que no se usan,
    excepto si son recetas base predefinidas.
    """
    recetas = cargar_recetas()
    if not recetas:
        return "🌳 El árbol está vacío, no hay nada que podar."
        
    ahora = datetime.now()
    podadas = []
    
    # Recetas base que nunca se deben borrar
    recetas_base = ["abrir_calculadora", "abrir_chrome", "captura_pantalla", "minimizar_todo", "nuevo_escritorio_virtual"]
    
    for nombre in list(recetas.keys()):
        if nombre in recetas_base:
            continue  # No podar recetas vitales
            
        datos = recetas[nombre]
        ultima_vez_str = datos.get("ultima_vez_usada", datos.get("creada", ahora.isoformat()))
        try:
            ultima_vez = datetime.fromisoformat(ultima_vez_str)
        except ValueError:
            ultima_vez = ahora
            
        dias_sin_uso = (ahora - ultima_vez).days
        veces_usada = datos.get("veces_usada", 0)
        
        # Criterio de poda: más de X días sin uso, o poco uso en mucho tiempo
        if dias_sin_uso >= dias_inactividad or (dias_sin_uso >= (dias_inactividad // 2) and veces_usada < umbral_uso):
            podadas.append(nombre)
            del recetas[nombre]
            
    if podadas:
        with open(RUTA_RECETAS, "w", encoding="utf-8") as f:
            json.dump(recetas, f, ensure_ascii=False, indent=2)
        return f"✂️ Poda Neuronal completada: se olvidaron {len(podadas)} habilidades inútiles ({', '.join(podadas)})."
    
    return "🌳 Árbol sano: ninguna habilidad requirió poda."


# ==========================================
# ESTADÍSTICAS DE SESIÓN
# ==========================================
class ContadorSeguridad:
    """
    Lleva la cuenta de acciones físicas en la sesión actual.
    Esto es el 'fusible' que evita que A.B.R.I.L. se desborde.
    """
    def __init__(self):
        self.teclas_escritas = 0
        self.clics_realizados = 0
        self.atajos_presionados = 0
        self.acciones_bloqueadas = 0
        self.inicio_sesion = datetime.now()
    
    def puede_escribir(self, cantidad_chars):
        """Verifica si se puede escribir más texto en esta sesión."""
        if self.teclas_escritas + cantidad_chars > config.MAX_TECLAS_SESION:
            self.acciones_bloqueadas += 1
            return False
        return True
    
    def puede_hacer_clic(self):
        """Verifica si se puede hacer más clics en esta sesión."""
        if self.clics_realizados >= config.MAX_CLICS_SESION:
            self.acciones_bloqueadas += 1
            return False
        return True
    
    def puede_presionar_atajo(self):
        """Verifica si se puede presionar más atajos en esta sesión."""
        if self.atajos_presionados >= config.MAX_ATAJOS_SESION:
            self.acciones_bloqueadas += 1
            return False
        return True
    
    def registrar_escritura(self, cantidad):
        self.teclas_escritas += cantidad
    
    def registrar_clic(self):
        self.clics_realizados += 1
    
    def registrar_atajo(self):
        self.atajos_presionados += 1
    
    def resumen(self):
        duracion = datetime.now() - self.inicio_sesion
        minutos = int(duracion.total_seconds() // 60)
        return (
            f"📊 Estadísticas de Sesión Física:\n"
            f"   ⌨️ Teclas escritas:     {self.teclas_escritas}/{config.MAX_TECLAS_SESION}\n"
            f"   🖱️ Clics realizados:    {self.clics_realizados}/{config.MAX_CLICS_SESION}\n"
            f"   ⌨️ Atajos presionados:  {self.atajos_presionados}/{config.MAX_ATAJOS_SESION}\n"
            f"   🚫 Acciones bloqueadas: {self.acciones_bloqueadas}\n"
            f"   ⏱️ Duración sesión:     {minutos} minutos"
        )


# ==========================================
# RECETAS PREDEFINIDAS (Kit de inicio)
# ==========================================
def inicializar_recetas_base():
    """Crea recetas predefinidas si no existen."""
    recetas = cargar_recetas()
    
    recetas_base = {
        "abrir_calculadora": {
            "descripcion": "Abre la calculadora de Windows",
            "pasos": [
                {"comando": "COMANDO_ATAJO", "parametros": {"teclas": "win"}},
                {"comando": "COMANDO_ESPERAR", "parametros": {"segundos": 1}},
                {"comando": "COMANDO_ESCRIBIR", "parametros": {"texto": "calculadora"}},
                {"comando": "COMANDO_ESPERAR", "parametros": {"segundos": 0.8}},
                {"comando": "COMANDO_ATAJO", "parametros": {"teclas": "enter"}}
            ],
            "creada": datetime.now().isoformat(),
            "veces_usada": 0
        },
        "abrir_chrome": {
            "descripcion": "Abre Google Chrome",
            "pasos": [
                {"comando": "COMANDO_ATAJO", "parametros": {"teclas": "win"}},
                {"comando": "COMANDO_ESPERAR", "parametros": {"segundos": 1}},
                {"comando": "COMANDO_ESCRIBIR", "parametros": {"texto": "chrome"}},
                {"comando": "COMANDO_ESPERAR", "parametros": {"segundos": 0.8}},
                {"comando": "COMANDO_ATAJO", "parametros": {"teclas": "enter"}}
            ],
            "creada": datetime.now().isoformat(),
            "veces_usada": 0
        },
        "captura_pantalla": {
            "descripcion": "Toma una captura de pantalla con Snipping Tool",
            "pasos": [
                {"comando": "COMANDO_ATAJO", "parametros": {"teclas": "win+shift+s"}}
            ],
            "creada": datetime.now().isoformat(),
            "veces_usada": 0
        },
        "minimizar_todo": {
            "descripcion": "Minimiza todas las ventanas y muestra el escritorio",
            "pasos": [
                {"comando": "COMANDO_ATAJO", "parametros": {"teclas": "win+d"}}
            ],
            "creada": datetime.now().isoformat(),
            "veces_usada": 0
        },
        "nuevo_escritorio_virtual": {
            "descripcion": "Crea un nuevo escritorio virtual en Windows",
            "pasos": [
                {"comando": "COMANDO_ATAJO", "parametros": {"teclas": "win+ctrl+d"}}
            ],
            "creada": datetime.now().isoformat(),
            "veces_usada": 0
        }
    }
    
    # Solo agregar las que no existan
    actualizado = False
    for nombre, datos in recetas_base.items():
        if nombre not in recetas:
            recetas[nombre] = datos
            actualizado = True
    
    if actualizado:
        _asegurar_carpeta()
        with open(RUTA_RECETAS, "w", encoding="utf-8") as f:
            json.dump(recetas, f, ensure_ascii=False, indent=2)
