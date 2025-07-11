import os
from datetime import datetime

# Variable global para la ruta del archivo de log
log_path = None

# -------------------------------
# Inicializa el sistema de logs
# -------------------------------
def init_logger(path):
    global log_path
    log_path = path
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(f"[{timestamp()}] 📝 Log inicializado\n")

# -------------------------------
# Registra un mensaje de información
# -------------------------------
def log_info(message):
    _write_log(f"[{timestamp()}] INFO: {message}")

# -------------------------------
# Registra un mensaje de error
# -------------------------------
def log_error(message):
    _write_log(f"[{timestamp()}] ERROR: {message}")

# -------------------------------
# Guarda benchmarking de duración
# -------------------------------
def log_benchmark(start_time, end_time, total_files):
    duration = round(end_time - start_time, 2)
    _write_log(f"[{timestamp()}] 🕒 Tiempo total: {duration}s | Archivos procesados: {total_files}")

# -------------------------------
# Retorna el contenido del log
# -------------------------------
def get_log_content():
    if log_path and os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "⚠️ Log no encontrado."

# -------------------------------
# Función privada para escribir en el log
# -------------------------------
def _write_log(line):
    if log_path:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(line + "\n")

# -------------------------------
# Timestamp formato
# -------------------------------
def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
