"""
Las Manos de A.B.R.I.L. — Herramientas de interacción con el sistema operativo.
Incluye herramientas originales + Fase 1 (Archivos) + Fase 3 (Control Físico).
"""
import subprocess
import platform
import psutil
import os
import shutil
import hashlib
import time
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from fnmatch import fnmatch
import config

# Importar pyautogui con fail-safe activado
try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = config.PAUSA_ENTRE_ACCIONES
    PYAUTOGUI_DISPONIBLE = True
    # Detectar resolución real de pantalla
    _screen_w, _screen_h = pyautogui.size()
    config.PANTALLA_ANCHO = _screen_w
    config.PANTALLA_ALTO = _screen_h
except ImportError:
    PYAUTOGUI_DISPONIBLE = False
    print(" [AVISO] pyautogui no instalado. Herramientas físicas deshabilitadas.")
    print("   Instala con: py -m pip install pyautogui")

# Importar motor de visión (Fase 6)
try:
    from cuerpo.vista.vision_core import buscar_objeto_en_pantalla, captura_pantalla
    VISION_DISPONIBLE = True
except ImportError:
    VISION_DISPONIBLE = False
    print(" [AVISO] Módulo de visión no disponible.")

# Importar sistema de memoria
import memoria

# Instancia global del contador de seguridad de sesión
_contador = memoria.ContadorSeguridad()

# Importar motricidad fina (Fase 3/6 reestructurada)
try:
    from cuerpo.motricidad.teclado import escribir_texto, presionar_atajo
    from cuerpo.motricidad.raton import hacer_clic, hacer_clic_visual, mover_mouse, hacer_scroll
except ImportError as e:
    print(f" [AVISO] Módulos de motricidad no disponibles: {e}")

# ==========================================
# HERRAMIENTAS ORIGINALES (Núcleo)
# ==========================================

def abrir_bloc_notas(**kwargs):
    """Abre un Bloc de Notas independiente sin bloquear al agente."""
    subprocess.Popen(['notepad.exe'])
    return " Bloc de notas abierto correctamente."


def reporte_sistema(**kwargs):
    """Genera un reporte completo de la arquitectura del sistema."""
    os_info = f"{platform.system()} {platform.release()} ({platform.version()})"
    arch = platform.machine()
    proc = platform.processor()
    return f"SO: {os_info} | Arquitectura: {arch} | Procesador: {proc}"


def escaner_hardware(**kwargs):
    """Escanea CPU, RAM y disco en tiempo real."""
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('C:\\')
    return (
        f"CPU: {cpu}% | "
        f"RAM: {ram.percent}% ({ram.used // (1024**3)}/{ram.total // (1024**3)} GB) | "
        f"Disco C: {disk.percent}% ({disk.free // (1024**3)} GB libres)"
    )


# ==========================================
# FASE 1: GESTIÓN DE ARCHIVOS (Completa)
# ==========================================

# --- Diccionario maestro de categorías ---
CATEGORIAS_ARCHIVO = {
    "Imagenes":     ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg', '.ico', '.tiff'],
    "Videos":       ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm'],
    "Musica":       ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
    "Documentos":   ['.pdf', '.docx', '.doc', '.txt', '.xlsx', '.xls', '.pptx', '.ppt', '.odt', '.csv'],
    "Instaladores": ['.exe', '.msi', '.dmg', '.deb', '.apk'],
    "Comprimidos":  ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
    "Codigo":       ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.ts', '.json', '.xml', '.sql', '.php'],
    "Fuentes":      ['.ttf', '.otf', '.woff', '.woff2'],
}


def limpiar_descargas(**kwargs):
    """Organiza archivos sueltos de Descargas en carpetas por categoría."""
    print(" Iniciando protocolo de limpieza en Descargas...")
    ruta_descargas = config.RUTA_DESCARGAS

    if not ruta_descargas.exists():
        return f" La carpeta de descargas no existe: {ruta_descargas}"

    archivos_movidos = 0
    sin_categoria = 0
    detalle = []

    for archivo in ruta_descargas.iterdir():
        if not archivo.is_file():
            continue

        ext = archivo.suffix.lower()
        categoria_destino = None

        for categoria, extensiones in CATEGORIAS_ARCHIVO.items():
            if ext in extensiones:
                categoria_destino = categoria
                break

        if categoria_destino:
            carpeta_destino = ruta_descargas / categoria_destino
            carpeta_destino.mkdir(exist_ok=True)
            try:
                destino_final = carpeta_destino / archivo.name
                # Si ya existe, añadir timestamp para no sobrescribir
                if destino_final.exists():
                    stem = archivo.stem
                    ts = datetime.now().strftime("%H%M%S")
                    destino_final = carpeta_destino / f"{stem}_{ts}{ext}"
                shutil.move(str(archivo), str(destino_final))
                archivos_movidos += 1
                detalle.append(f"   → {archivo.name} ➜ {categoria_destino}/")
            except Exception:
                pass  # Ignorar archivos en uso
        else:
            sin_categoria += 1

    if archivos_movidos == 0:
        return " Tu carpeta de descargas ya está organizada. No hay archivos sueltos que mover."

    resumen = f" Se organizaron {archivos_movidos} archivo(s) en categorías:\n"
    for linea in detalle[:15]:
        resumen += linea + "\n"
    if len(detalle) > 15:
        resumen += f"   ... y {len(detalle) - 15} más.\n"
    if sin_categoria > 0:
        resumen += f"📎 {sin_categoria} archivo(s) sin categoría conocida (no se movieron)."
    return resumen


def crear_proyecto(**kwargs):
    """Crea una estructura de carpetas profesional para un proyecto nuevo."""
    print(" Inicializando estructura base de desarrollo...")
    nombre = kwargs.get("nombre", "Nuevo_Proyecto")
    tipo = kwargs.get("tipo", "fullstack").lower()

    ruta_proyecto = config.RUTA_ESCRITORIO / nombre

    if ruta_proyecto.exists():
        return f" Ya existe una carpeta llamada '{nombre}' en el Escritorio."

    ruta_proyecto.mkdir(parents=True)

    if tipo == "fullstack":
        # Estructura full-stack profesional
        for carpeta in [
            "src/backend", "src/frontend",
            "database/migrations", "database/seeds",
            "docs", "tests", "config", "scripts"
        ]:
            (ruta_proyecto / carpeta).mkdir(parents=True)
        (ruta_proyecto / "README.md").write_text(
            f"# {nombre}\n\nProyecto full-stack generado por A.B.R.I.L.\n\n"
            f"## Estructura\n- `src/backend/` — Lógica del servidor\n"
            f"- `src/frontend/` — Interfaz de usuario\n"
            f"- `database/` — Migraciones y seeds\n"
            f"- `docs/` — Documentación\n- `tests/` — Pruebas\n",
            encoding="utf-8")
        (ruta_proyecto / ".gitignore").write_text(
            "node_modules/\nvenv/\n__pycache__/\n*.pyc\n.env\n.DS_Store\n", encoding="utf-8")
        (ruta_proyecto / "src/backend/app.py").write_text(
            '"""Servidor principal."""\n\ndef main():\n    print("Servidor iniciado")\n\nif __name__ == "__main__":\n    main()\n',
            encoding="utf-8")

    elif tipo == "python":
        for carpeta in ["src", "tests", "docs"]:
            (ruta_proyecto / carpeta).mkdir()
        (ruta_proyecto / "src" / "__init__.py").touch()
        (ruta_proyecto / "src" / "main.py").write_text(
            '"""Punto de entrada principal."""\n\ndef main():\n    print("¡Hola mundo!")\n\nif __name__ == "__main__":\n    main()\n',
            encoding="utf-8")
        (ruta_proyecto / "requirements.txt").write_text("", encoding="utf-8")
        (ruta_proyecto / "README.md").write_text(f"# {nombre}\n\nProyecto Python generado por A.B.R.I.L.\n", encoding="utf-8")
        (ruta_proyecto / ".gitignore").write_text("__pycache__/\n*.pyc\n.env\nvenv/\n", encoding="utf-8")

    elif tipo == "web":
        for carpeta in ["css", "js", "assets/img", "assets/fonts"]:
            (ruta_proyecto / carpeta).mkdir(parents=True)
        (ruta_proyecto / "index.html").write_text(
            f'<!DOCTYPE html>\n<html lang="es">\n<head>\n    <meta charset="UTF-8">\n'
            f'    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            f'    <title>{nombre}</title>\n    <link rel="stylesheet" href="css/style.css">\n'
            f'</head>\n<body>\n    <h1>{nombre}</h1>\n    <script src="js/app.js"></script>\n</body>\n</html>\n',
            encoding="utf-8")
        (ruta_proyecto / "css" / "style.css").write_text(
            "/* Estilos principales */\n* { margin: 0; padding: 0; box-sizing: border-box; }\n", encoding="utf-8")
        (ruta_proyecto / "js" / "app.js").write_text("// Lógica principal\nconsole.log('App lista');\n", encoding="utf-8")
    else:
        # General
        for carpeta in ["docs", "assets", "scripts"]:
            (ruta_proyecto / carpeta).mkdir()
        (ruta_proyecto / "README.md").write_text(f"# {nombre}\n\nProyecto generado por A.B.R.I.L.\n", encoding="utf-8")

    return f" Proyecto '{nombre}' ({tipo}) creado en: {ruta_proyecto}"


def buscar_archivo(**kwargs):
    """Busca archivos recursivamente en el disco."""
    nombre = kwargs.get("nombre", "")
    ruta_inicio = kwargs.get("ruta", str(Path.home()))

    if not nombre:
        return " Necesito un nombre o patrón de archivo para buscar."

    resultados = []
    ruta = Path(ruta_inicio)

    if not ruta.exists():
        return f" La ruta '{ruta_inicio}' no existe."

    excluir = {"Windows", "Program Files", "Program Files (x86)", "$Recycle.Bin",
               "ProgramData", "AppData", "node_modules", ".git", "__pycache__"}

    try:
        for dirpath, dirnames, filenames in os.walk(str(ruta)):
            profundidad = str(dirpath).replace(str(ruta), "").count(os.sep)
            if profundidad > 5:
                dirnames.clear()
                continue
            dirnames[:] = [d for d in dirnames if d not in excluir]

            for filename in filenames:
                if fnmatch(filename.lower(), f"*{nombre.lower()}*"):
                    ruta_completa = Path(dirpath) / filename
                    try:
                        tamano_str = _formato_tamano(ruta_completa.stat().st_size)
                        resultados.append(f"    {ruta_completa} ({tamano_str})")
                    except OSError:
                        resultados.append(f"    {ruta_completa}")

                    if len(resultados) >= config.MAX_RESULTADOS_BUSQUEDA:
                        resultados.append(f"   ... (límite de {config.MAX_RESULTADOS_BUSQUEDA} resultados)")
                        return f" Resultados para '{nombre}':\n" + "\n".join(resultados)
    except PermissionError:
        pass

    if not resultados:
        return f" No se encontró ningún archivo que coincida con '{nombre}' en {ruta_inicio}"

    return f" {len(resultados)} resultado(s) para '{nombre}':\n" + "\n".join(resultados)


def leer_log(**kwargs):
    """Lee el contenido de un archivo de texto/log."""
    ruta = kwargs.get("ruta", "")
    lineas_param = int(kwargs.get("lineas", 0))

    if not ruta:
        return " Necesito la ruta del archivo para leerlo."

    archivo = Path(ruta)

    if not archivo.exists():
        return f" El archivo no existe: {ruta}"
    if not archivo.is_file():
        return f" '{ruta}' no es un archivo válido."

    extensiones_seguras = {".txt", ".log", ".md", ".csv", ".json", ".xml",
                           ".py", ".js", ".html", ".css", ".yaml", ".yml",
                           ".ini", ".cfg", ".conf", ".sql", ".env", ".sh", ".bat"}

    if archivo.suffix.lower() not in extensiones_seguras:
        return f" Por seguridad, solo puedo leer archivos de texto ({', '.join(sorted(extensiones_seguras))})"

    try:
        contenido = archivo.read_text(encoding="utf-8", errors="replace")
        total_lineas = len(contenido.splitlines())

        if lineas_param > 0:
            # Mostrar solo las últimas N líneas
            lineas_contenido = contenido.splitlines()
            ultimas = lineas_contenido[-lineas_param:]
            contenido = f"[Mostrando últimas {len(ultimas)} líneas de {total_lineas}]\n"
            contenido += "\n".join(ultimas)
        elif len(contenido) > config.MAX_CHARS_LECTURA:
            lineas_contenido = contenido.splitlines()
            ultimas = lineas_contenido[-100:]
            contenido = f"[... archivo truncado, mostrando últimas 100 líneas de {total_lineas} ...]\n"
            contenido += "\n".join(ultimas)

        return f" Contenido de '{archivo.name}' ({_formato_tamano(archivo.stat().st_size)} | {total_lineas} líneas):\n\n{contenido}"
    except Exception as e:
        return f" Error al leer el archivo: {e}"


def listar_directorio(**kwargs):
    """Lista el contenido de un directorio."""
    ruta = kwargs.get("ruta", str(Path.home() / "Desktop"))
    carpeta = Path(ruta)

    if not carpeta.exists():
        return f" La carpeta no existe: {ruta}"
    if not carpeta.is_dir():
        return f" '{ruta}' no es un directorio."

    dirs = []
    files = []

    try:
        for item in sorted(carpeta.iterdir()):
            if item.name.startswith('.'):
                continue
            if item.is_dir():
                dirs.append(f"    {item.name}/")
            else:
                tamano = _formato_tamano(item.stat().st_size)
                files.append(f"    {item.name} ({tamano})")
    except PermissionError:
        return f" Sin permisos para acceder a: {ruta}"

    resumen = f" Contenido de {carpeta} ({len(dirs)} carpetas, {len(files)} archivos):\n"
    for d in dirs[:20]:
        resumen += d + "\n"
    for f in files[:30]:
        resumen += f + "\n"
    total = len(dirs) + len(files)
    if total > 50:
        resumen += f"   ... y {total - 50} elementos más."
    return resumen


def abrir_carpeta(**kwargs):
    """Abre una carpeta en el Explorador de Windows."""
    ruta = kwargs.get("ruta", str(Path.home() / "Desktop"))
    carpeta = Path(ruta)

    if not carpeta.exists():
        return f" La carpeta no existe: {ruta}"

    subprocess.Popen(['explorer', str(carpeta)])
    return f" Carpeta abierta en el explorador: {carpeta}"


# ==========================================
# FASE 1 EXTRA: Herramientas Avanzadas
# ==========================================

def mover_archivo(**kwargs):
    """Mueve o renombra un archivo/carpeta de forma segura."""
    origen = kwargs.get("origen", "")
    destino = kwargs.get("destino", "")

    if not origen or not destino:
        return " Necesito la ruta de origen y la ruta de destino."

    ruta_origen = Path(origen)
    ruta_destino = Path(destino)

    if not ruta_origen.exists():
        return f" El origen no existe: {origen}"

    # Si el destino es un directorio existente, mover dentro de él
    if ruta_destino.is_dir():
        ruta_destino = ruta_destino / ruta_origen.name

    try:
        ruta_destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(ruta_origen), str(ruta_destino))
        return f" Movido: {ruta_origen.name} ➜ {ruta_destino}"
    except Exception as e:
        return f" Error al mover: {e}"


def analizar_espacio(**kwargs):
    """Analiza el uso de espacio en disco de una carpeta (top 10 más pesados)."""
    ruta = kwargs.get("ruta", str(Path.home() / "Desktop"))
    carpeta = Path(ruta)

    if not carpeta.exists():
        return f" La carpeta no existe: {ruta}"

    print(" Analizando uso de espacio en disco...")
    items_con_tamano = []

    try:
        for item in carpeta.iterdir():
            if item.name.startswith('.'):
                continue
            try:
                if item.is_file():
                    tamano = item.stat().st_size
                elif item.is_dir():
                    tamano = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                else:
                    continue
                items_con_tamano.append((item.name, tamano, item.is_dir()))
            except (PermissionError, OSError):
                continue
    except PermissionError:
        return f" Sin permisos para acceder a: {ruta}"

    # Ordenar por tamaño descendente
    items_con_tamano.sort(key=lambda x: x[1], reverse=True)
    total = sum(t[1] for t in items_con_tamano)

    resumen = f" Análisis de espacio en {carpeta} (Total: {_formato_tamano(total)}):\n\n"
    for nombre, tamano, es_dir in items_con_tamano[:10]:
        icono = "" if es_dir else ""
        porcentaje = (tamano / total * 100) if total > 0 else 0
        barra = "█" * int(porcentaje / 5) + "░" * (20 - int(porcentaje / 5))
        resumen += f"   {icono} {nombre:<35} {_formato_tamano(tamano):>10}  {barra} {porcentaje:.1f}%\n"

    if len(items_con_tamano) > 10:
        resumen += f"\n   ... y {len(items_con_tamano) - 10} elementos más."
    return resumen


def encontrar_duplicados(**kwargs):
    """Busca archivos duplicados por tamaño + hash en una carpeta."""
    ruta = kwargs.get("ruta", str(Path.home() / "Downloads"))
    carpeta = Path(ruta)

    if not carpeta.exists():
        return f" La carpeta no existe: {ruta}"

    print(" Escaneando archivos duplicados (esto puede tardar)...")

    # Paso 1: Agrupar por tamaño (filtro rápido)
    por_tamano = {}
    try:
        for archivo in carpeta.rglob('*'):
            if archivo.is_file():
                try:
                    tamano = archivo.stat().st_size
                    if tamano > 0:  # Ignorar archivos vacíos
                        por_tamano.setdefault(tamano, []).append(archivo)
                except (PermissionError, OSError):
                    continue
    except PermissionError:
        return f" Sin permisos para acceder a: {ruta}"

    # Paso 2: Solo verificar hash en grupos con mismo tamaño
    duplicados = []
    for tamano, archivos in por_tamano.items():
        if len(archivos) < 2:
            continue

        por_hash = {}
        for archivo in archivos:
            try:
                h = hashlib.md5()
                with open(archivo, 'rb') as f:
                    # Leer solo los primeros 8KB para rapidez
                    h.update(f.read(8192))
                por_hash.setdefault(h.hexdigest(), []).append(archivo)
            except (PermissionError, OSError):
                continue

        for hash_val, grupo in por_hash.items():
            if len(grupo) >= 2:
                duplicados.append((grupo, tamano))

    if not duplicados:
        return f" No se encontraron archivos duplicados en {carpeta}"

    resumen = f" Se encontraron {len(duplicados)} grupo(s) de duplicados en {carpeta}:\n\n"
    for i, (grupo, tamano) in enumerate(duplicados[:8], 1):
        resumen += f"   Grupo {i} ({_formato_tamano(tamano)}):\n"
        for archivo in grupo:
            resumen += f"       {archivo}\n"
    if len(duplicados) > 8:
        resumen += f"\n   ... y {len(duplicados) - 8} grupos más."

    espacio_recuperable = sum(t * (len(g) - 1) for g, t in duplicados)
    resumen += f"\n\n   💾 Espacio recuperable: {_formato_tamano(espacio_recuperable)}"
    return resumen


def info_archivo(**kwargs):
    """Muestra información detallada de un archivo específico."""
    ruta = kwargs.get("ruta", "")

    if not ruta:
        return " Necesito la ruta del archivo."

    archivo = Path(ruta)

    if not archivo.exists():
        return f" No existe: {ruta}"

    try:
        stat = archivo.stat()
        fecha_creacion = datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
        fecha_modificacion = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        fecha_acceso = datetime.fromtimestamp(stat.st_atime).strftime("%Y-%m-%d %H:%M:%S")

        info = f" Información de '{archivo.name}':\n"
        info += f"   📍 Ruta completa:   {archivo.resolve()}\n"
        info += f"   📦 Tamaño:          {_formato_tamano(stat.st_size)}\n"
        info += f"   📝 Extensión:       {archivo.suffix or '(sin extensión)'}\n"
        info += f"   📅 Creado:          {fecha_creacion}\n"
        info += f"   📅 Modificado:      {fecha_modificacion}\n"
        info += f"   📅 Último acceso:   {fecha_acceso}\n"

        if archivo.is_dir():
            n_archivos = sum(1 for _ in archivo.rglob('*') if _.is_file())
            n_carpetas = sum(1 for _ in archivo.rglob('*') if _.is_dir())
            info += f"    Contenido:       {n_archivos} archivos, {n_carpetas} carpetas\n"

        return info
    except Exception as e:
        return f" Error al obtener información: {e}"


def gestionar_papelera(**kwargs):
    """Lista, restaura o vacía la papelera interna de A.B.R.I.L."""
    accion = kwargs.get("accion", "listar")

    if accion == "listar":
        if not config.RUTA_PAPELERA.exists():
            return " La papelera de A.B.R.I.L. está vacía."

        items = list(config.RUTA_PAPELERA.rglob('*'))
        archivos = [i for i in items if i.is_file()]
        tamano_total = sum(f.stat().st_size for f in archivos)

        if not archivos:
            return " La papelera de A.B.R.I.L. está vacía."

        resumen = f" Papelera de A.B.R.I.L. ({len(archivos)} archivos, {_formato_tamano(tamano_total)}):\n"
        for f in archivos[:15]:
            rel = f.relative_to(config.RUTA_PAPELERA)
            resumen += f"    {rel} ({_formato_tamano(f.stat().st_size)})\n"
        if len(archivos) > 15:
            resumen += f"   ... y {len(archivos) - 15} más."
        return resumen

    elif accion == "vaciar":
        if not config.RUTA_PAPELERA.exists():
            return " La papelera ya está vacía."
        try:
            shutil.rmtree(str(config.RUTA_PAPELERA))
            return " Papelera vaciada completamente."
        except Exception as e:
            return f" Error al vaciar la papelera: {e}"

    return f" Acción no reconocida: {accion}. Usa 'listar' o 'vaciar'."


# ==========================================
# UTILIDADES INTERNAS
# ==========================================

def _formato_tamano(bytes_size):
    """Convierte bytes a formato legible."""
    for unidad in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unidad}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"





def esperar(**kwargs):
    """Pausa la ejecución un número de segundos (para dar tiempo entre acciones)."""
    segundos = float(kwargs.get("segundos", 1.0))
    
    # Limitar espera máxima a 10 segundos
    segundos = min(max(segundos, 0.1), 10.0)
    
    print(f" Esperando {segundos}s...")
    time.sleep(segundos)
    return f" Pausa de {segundos}s completada."


def abrir_app(**kwargs):
    """
    Abre una aplicación usando el buscador de Windows.
    Es una 'macro' segura que utiliza los motores motrices.
    """
    nombre = kwargs.get("nombre", "")
    
    if not nombre:
        return " Necesito el nombre de la aplicación."
    
    if len(nombre) > 50:
        return "🚫 Nombre de aplicación demasiado largo."
    
    print(f" Abriendo aplicación: '{nombre}'")
    
    # Secuencia motriz
    presionar_atajo(teclas="win")
    esperar(segundos=1.0)
    escribir_texto(texto=nombre)
    esperar(segundos=0.8)
    presionar_atajo(teclas="enter")
    
    memoria.registrar_accion("fisico", "COMANDO_ABRIR_APP", {"nombre": nombre}, "OK")
    return f" Aplicación '{nombre}' abierta (si existe en el sistema)."


def aprender_habilidad(**kwargs):
    """
    Aprende una nueva secuencia de acciones y la guarda en el Árbol de Conocimiento.
    Esta es la base de la Fase 4: Crecimiento Neuronal.
    """
    nombre = kwargs.get("nombre", "")
    descripcion = kwargs.get("descripcion", "Habilidad aprendida automáticamente")
    pasos = kwargs.get("pasos", [])
    
    if not nombre or not pasos:
        return " Para aprender, necesito un nombre y una lista de pasos."
        
    # Validar que los pasos contengan comandos válidos
    comandos_validos = ["COMANDO_ESCRIBIR", "COMANDO_ATAJO", "COMANDO_CLICK", "COMANDO_MOVER_MOUSE", "COMANDO_ESPERAR", "COMANDO_ABRIR_APP"]
    
    for paso in pasos:
        if paso.get("comando") not in comandos_validos:
            return f" El comando '{paso.get('comando')}' no se puede usar dentro de una receta."
            
    resultado = memoria.guardar_receta(nombre, descripcion, pasos)
    memoria.registrar_accion("sistema", "COMANDO_APRENDER", {"nombre": nombre}, "OK")
    
    # Auto-ejecutar la receta recién aprendida para probarla inmediatamente
    print(f"\n Habilidad '{nombre}' aprendida. Iniciando prueba de ejecución automática...")
    resultado_ejecucion = ejecutar_receta(nombre=nombre)
    
    return f"{resultado}\n\n--- Prueba de ejecución automática ---\n{resultado_ejecucion}"


def ejecutar_receta(**kwargs):
    """Ejecuta una secuencia de acciones aprendida (receta)."""
    nombre = kwargs.get("nombre", "")
    
    if not nombre:
        recetas_texto = memoria.listar_recetas()
        return f" Necesito el nombre de la receta.\n\n{recetas_texto}"
    
    receta = memoria.obtener_receta(nombre)
    if not receta:
        return f" Receta '{nombre}' no encontrada.\n\n{memoria.listar_recetas()}"
    
    print(f" Ejecutando: '{nombre}' ({len(receta['pasos'])} pasos)")
    
    resultados = []
    for i, paso in enumerate(receta["pasos"], 1):
        cmd = paso.get("comando", "")
        params = paso.get("parametros", {})
        
        # Buscar la herramienta en el catálogo
        funcion = CATALOGO.get(cmd)
        if not funcion:
            resultados.append(f"   Paso {i}:  Comando desconocido: {cmd}")
            continue
        
        try:
            resultado = funcion(**params)
            resultados.append(f"   Paso {i}: {resultado}")
        except Exception as e:
            resultados.append(f"   Paso {i}:  Error: {e}")
            break  # Abortar receta si un paso falla
    
    memoria.incrementar_uso_receta(nombre)
    memoria.registrar_accion("receta", "COMANDO_RECETA", {"nombre": nombre}, "OK")
    
    return f" Receta '{nombre}' completada:\n" + "\n".join(resultados)


def listar_recetas_disponibles(**kwargs):
    """Lista todas las recetas aprendidas disponibles."""
    return memoria.listar_recetas()


def podar_arbol_conocimiento(**kwargs):
    """
    Ejecuta la poda neuronal: elimina habilidades inútiles o no usadas.
    """
    dias = int(kwargs.get("dias", 30))
    umbral = int(kwargs.get("umbral", 3))
    
    print(f" Iniciando poda neuronal (Inactividad > {dias} días)...")
    resultado = memoria.podar_arbol(dias_inactividad=dias, umbral_uso=umbral)
    memoria.registrar_accion("sistema", "COMANDO_PODAR", {"dias": dias}, "OK")
    return resultado


def estadisticas_fisicas(**kwargs):
    """Muestra las estadísticas de uso físico de la sesión actual."""
    return _contador.resumen()


def ver_log_acciones(**kwargs):
    """Muestra las últimas acciones registradas en el log de auditoría."""
    n = int(kwargs.get("cantidad", 15))
    acciones = memoria.obtener_log_reciente(n)
    
    if not acciones:
        return " No hay acciones registradas en el log."
    
    resumen = f" Últimas {len(acciones)} acciones registradas:\n"
    for a in acciones:
        estado = "" if a.get("aprobado", True) else "🚫"
        resumen += f"   {estado} [{a['timestamp'][11:19]}] {a['tipo']}: {a['comando']}\n"
    return resumen


# ==========================================
# REGISTRO DE HERRAMIENTAS
# ==========================================
# Mapa que conecta los comandos de Gemini con las funciones reales

CATALOGO = {
    # --- Núcleo ---
    "COMANDO_NOTAS":              abrir_bloc_notas,
    "COMANDO_INFO":               reporte_sistema,
    "COMANDO_RECURSOS":           escaner_hardware,
    # --- Fase 1: Gestión de Archivos ---
    "COMANDO_LIMPIAR":            limpiar_descargas,
    "COMANDO_PROYECTO":           crear_proyecto,
    "COMANDO_BUSCAR":             buscar_archivo,
    "COMANDO_LEER_LOG":           leer_log,
    "COMANDO_LISTAR":             listar_directorio,
    "COMANDO_ABRIR_CARPETA":      abrir_carpeta,
    # --- Fase 1 Extra: Avanzadas ---
    "COMANDO_MOVER":              mover_archivo,
    "COMANDO_ESPACIO":            analizar_espacio,
    "COMANDO_DUPLICADOS":         encontrar_duplicados,
    "COMANDO_INFO_ARCHIVO":       info_archivo,
    "COMANDO_PAPELERA":           gestionar_papelera,
    # --- Fase 3: Control Físico ---
    "COMANDO_ESCRIBIR":           escribir_texto,
    "COMANDO_ATAJO":              presionar_atajo,
    "COMANDO_CLICK":              hacer_clic,
    "COMANDO_MOVER_MOUSE":        mover_mouse,
    "COMANDO_SCREENSHOT":         captura_pantalla,
    "COMANDO_SCROLL":             hacer_scroll,
    "COMANDO_ESPERAR":            esperar,
    "COMANDO_ABRIR_APP":          abrir_app,
    "COMANDO_RECETA":             ejecutar_receta,
    # --- Fase 6: Visión ---
    "COMANDO_CLICK_VISUAL":       hacer_clic_visual,
    # --- Fase 4: Árbol de Conocimiento ---
    "COMANDO_APRENDER":           aprender_habilidad,
    "COMANDO_PODAR":              podar_arbol_conocimiento,
    # --- Meta / Info ---
    "COMANDO_LISTAR_RECETAS":     listar_recetas_disponibles,
    "COMANDO_ESTADISTICAS":       estadisticas_fisicas,
    "COMANDO_VER_LOG":            ver_log_acciones,
}

