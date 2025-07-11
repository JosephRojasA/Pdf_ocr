import sys
import os
import time
from flask import Flask, render_template, request, redirect, jsonify

# Agregar carpeta "ocr_utils" al path para importar sus módulos
sys.path.append(os.path.join(os.path.dirname(__file__), "ocr_utils"))

# Ahora sí se pueden importar sin prefijo
import ocr_processor
import pdf_splitter
import metadata_writer
import logger

app = Flask(__name__)

# Ruta global para el log
LOG_FILE = "output/proceso.log"
logger.init_logger(LOG_FILE)

# -------------------------------
# Función: Página principal
# -------------------------------
@app.route('/')
def index():
    return render_template('index.html')


# -------------------------------
# Función: Inicia el procesamiento
# -------------------------------
@app.route('/start', methods=['POST'])
def start_processing():
    input_folder = request.form.get('input_folder')
    output_folder = request.form.get('output_folder')

    if not input_folder or not output_folder:
        logger.log_error("❌ Rutas no válidas.")
        return "Error: Rutas no válidas."

    input_path = os.path.join(os.getcwd(), input_folder)
    output_path = os.path.join(os.getcwd(), output_folder)

    start_time = time.time()
    logger.log_info(f"🚀 Iniciando procesamiento de OCR en: {input_path}")
    logger.log_info(f"💾 Guardando resultados en: {output_path}")

    try:
        os.makedirs(output_path, exist_ok=True)

        processed_files = 0
        for file in os.listdir(input_path):
            if file.lower().endswith(".pdf"):
                pdf_path = os.path.join(input_path, file)
                pdf_output_dir = os.path.join(output_path, os.path.splitext(file)[0])
                os.makedirs(pdf_output_dir, exist_ok=True)

                # 1. OCR
                ocr_processor.ocr_pdf_to_text(pdf_path, pdf_output_dir)

                # 2. División
                pdf_splitter.split_pdf_by_page(pdf_path, pdf_output_dir)

                # 3. Inserta metadatos básicos
                metadata_writer.insert_metadata_to_pdf(pdf_path, {
                    "Title": file,
                    "Producer": "OCR App",
                    "CustomID": f"{int(time.time())}"
                })

                processed_files += 1
                logger.log_info(f"✅ Procesado: {file}")

        end_time = time.time()
        logger.log_benchmark(start_time, end_time, processed_files)
        return redirect('/')
    
    except Exception as e:
        logger.log_error(f"❌ Error general: {str(e)}")
        return f"Error: {str(e)}"


# -------------------------------
# Función: Retorna contenido del log
# -------------------------------
@app.route('/logs')
def get_logs():
    return logger.get_log_content()


# -------------------------------
# Ejecutar el servidor
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)
