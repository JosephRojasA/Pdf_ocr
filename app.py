import os
import sys
import time
from flask import Flask, render_template, request, redirect

# -------------------------------
# Asegurar que la carpeta base del proyecto está en sys.path
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UTILS_PATH = os.path.join(BASE_DIR, "ocr_utils")
if UTILS_PATH not in sys.path:
    sys.path.insert(0, UTILS_PATH)

# -------------------------------
# Importar módulos propios desde el paquete ocr_utils
# -------------------------------
from ocr_utils import ocr_processor
from ocr_utils import pdf_splitter
from ocr_utils import metadata_writer
from ocr_utils import logger

# -------------------------------
# Inicializar Flask
# -------------------------------
app = Flask(__name__)

# -------------------------------
# Configurar logs
# -------------------------------
LOG_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "proceso.log")
logger.init_logger(LOG_FILE)

# -------------------------------
# Ruta principal (vista HTML)
# -------------------------------
@app.route('/')
def index():
    return render_template('index.html')

# -------------------------------
# Ruta para iniciar el procesamiento OCR
# -------------------------------
@app.route('/start', methods=['POST'])
def start_processing():
    input_folder = request.form.get('input_folder')
    output_folder = request.form.get('output_folder')

    if not input_folder or not output_folder:
        logger.log_error("❌ Rutas no válidas.")
        return "Error: Rutas no válidas."

    input_path = os.path.abspath(input_folder)
    output_path = os.path.abspath(output_folder)

    start_time = time.time()
    logger.log_info(f"🚀 Iniciando procesamiento OCR en: {input_path}")
    logger.log_info(f"💾 Guardando resultados en: {output_path}")

    try:
        os.makedirs(output_path, exist_ok=True)
        processed_files = 0

        for file in os.listdir(input_path):
            if file.lower().endswith(".pdf"):
                pdf_path = os.path.join(input_path, file)
                base_name = os.path.splitext(file)[0]

                try:
                    # OCR primero (crear subcarpeta solo si es exitoso)
                    temp_output_dir = os.path.join(output_path, base_name)
                    os.makedirs(temp_output_dir, exist_ok=True)

                    logger.log_info(f"🔁 Iniciando OCR para: {file}")
                    ocr_processor.ocr_pdf_to_text(pdf_path, temp_output_dir)

                    # Verificar si el OCR generó algún archivo de texto
                    has_text = any(
                        fname.endswith(".txt") and os.path.getsize(os.path.join(temp_output_dir, fname)) > 0
                        for fname in os.listdir(temp_output_dir)
                    )

                    if not has_text:
                        logger.log_error(f"⚠️ OCR fallido o sin texto: {file}")
                        # Elimina carpeta vacía
                        if os.path.exists(temp_output_dir) and not os.listdir(temp_output_dir):
                            os.rmdir(temp_output_dir)
                        continue  # Saltar este archivo

                    # Si OCR fue exitoso, continuar con los otros pasos
                    pdf_splitter.split_pdf_by_page(pdf_path, temp_output_dir)
                    metadata_writer.insert_metadata_to_pdf(pdf_path, {
                        "Title": file,
                        "Producer": "OCR App",
                        "CustomID": f"{int(time.time())}"
                    })

                    processed_files += 1
                    logger.log_info(f"✅ Procesado correctamente: {file}")

                except Exception as e:
                    logger.log_error(f"❌ Error procesando {file}: {str(e)}")

        end_time = time.time()
        logger.log_benchmark(start_time, end_time, processed_files)
        return redirect('/')

    except Exception as e:
        logger.log_error(f"❌ Error general: {str(e)}")
        return f"Error: {str(e)}"

# -------------------------------
# Ruta para ver los logs
# -------------------------------
@app.route('/logs')
def get_logs():
    return logger.get_log_content()

# -------------------------------
# Ejecutar servidor Flask
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)
