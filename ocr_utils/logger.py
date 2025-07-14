import os
from datetime import datetime

# -------------------------------
# Ruta global del archivo de log
# -------------------------------
log_path = None

# -------------------------------
# Inicializa el logger con una ruta
# -------------------------------
def init_logger(path):
    global log_path
    log_path = path
    os.makedirs(os.path.dirname(path), exist_ok=True)

    try:
        with open(log_path, 'w', encoding='utf-8', errors='replace') as f:
            f.write(f"[{timestamp()}] Log inicializado\n")
    except Exception as e:
        print(f"[LOGGER] Error inicializando log: {safe_str(e)}")

# -------------------------------
# Escribe mensaje informativo
# -------------------------------
def log_info(message):
    _write_log(f"[{timestamp()}] INFO: {safe_str(message)}")

# -------------------------------
# Escribe mensaje de error
# -------------------------------
def log_error(message):
    _write_log(f"[{timestamp()}] ERROR: {safe_str(message)}")

# -------------------------------
# Registra métricas de tiempo y archivos
# -------------------------------
def log_benchmark(start_time, end_time, total_files):
    duration = round(end_time - start_time, 2)
    _write_log(f"[{timestamp()}] Tiempo total: {duration}s | Archivos procesados: {total_files}")

# -------------------------------
# Devuelve contenido completo del log
# -------------------------------
def get_log_content():
    if log_path and os.path.exists(log_path):
        try:
            with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
        except Exception as e:
            return f"[LOGGER] Error leyendo log: {safe_str(e)}"
    return "Log no encontrado."

# -------------------------------
# Función interna: escribe en el archivo de log
# -------------------------------
def _write_log(line):
    if not log_path:
        print(f"[LOGGER] Log no inicializado: {line}")
        return

    try:
        with open(log_path, 'a', encoding='utf-8', errors='replace') as f:
            f.write(line + "\n")
    except Exception as e:
        print(f"[LOGGER] Error escribiendo log: {safe_str(e)}")

# -------------------------------
# Devuelve timestamp actual en formato legible
# -------------------------------
def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# -------------------------------
# Limpia cadenas con caracteres problemáticos
# -------------------------------
def safe_str(message):
    try:
        return str(message)
    except Exception:
        try:
            return str(message).encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        except Exception:
            return "[Error al convertir a string]"
