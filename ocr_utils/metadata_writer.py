import os
import json
import csv
import pikepdf
from datetime import datetime
from ocr_utils.logger import log_info, log_error

# -------------------------------
# Lee metadatos desde archivo CSV o JSON (UTF-8)
# -------------------------------
def read_metadata_from_file(metadata_path):
    metadata_map = {}

    try:
        if metadata_path.endswith('.json'):
            with open(metadata_path, 'r', encoding='utf-8', errors='ignore') as f:
                metadata_map = json.load(f)

        elif metadata_path.endswith('.csv'):
            with open(metadata_path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    filename = row.get("filename")
                    if filename:
                        metadata_map[filename] = {k: v for k, v in row.items() if k != "filename"}

        log_info(f"Metadatos cargados desde: {metadata_path}")

    except Exception as e:
        log_error(f"Error leyendo metadatos: {safe_str(e)}")

    return metadata_map

# -------------------------------
# Inserta metadatos en un solo PDF
# -------------------------------
def insert_metadata_to_pdf(pdf_path, metadata: dict):
    try:
        with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
            info = pdf.docinfo

            # Campos estándar
            info["/Title"] = metadata.get('Title', '')
            info["/Author"] = metadata.get('Author', 'OCR_App')
            info["/Producer"] = metadata.get('Producer', 'OCR_App')
            info["/Subject"] = metadata.get('Subject', '')

            # Campo personalizado
            custom_id = metadata.get('CustomID', f"ID-{int(datetime.now().timestamp())}")
            info["/CustomID"] = custom_id

            pdf.save(pdf_path)

        log_info(f"Metadatos insertados en: {os.path.basename(pdf_path)}")
    except Exception as e:
        log_error(f"Error insertando metadatos en {os.path.basename(pdf_path)}: {safe_str(e)}")


# -------------------------------
# Aplica metadatos a todos los PDFs de una carpeta
# -------------------------------
def batch_insert_metadata(folder_path, metadata_map: dict):
    try:
        for file in os.listdir(folder_path):
            if file.lower().endswith(".pdf"):
                pdf_path = os.path.join(folder_path, file)

                metadata = metadata_map.get(file, {
                    "Title": file,
                    "CustomID": f"Auto-{int(datetime.now().timestamp())}"
                })

                insert_metadata_to_pdf(pdf_path, metadata)

        log_info(f"Metadatos aplicados en lote en carpeta: {folder_path}")

    except Exception as e:
        log_error(f"Error en procesamiento masivo de metadatos: {safe_str(e)}")

# -------------------------------
# Utilidad: limpia strings para evitar errores de codificación
# -------------------------------
def clean_str(value):
    try:
        return str(value).encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
    except Exception:
        return ""

# -------------------------------
# Utilidad: convierte cualquier objeto a string sin error
# -------------------------------
def safe_str(obj):
    try:
        return str(obj)
    except Exception:
        try:
            return str(obj).encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        except Exception:
            return "[Error al convertir a string]"
