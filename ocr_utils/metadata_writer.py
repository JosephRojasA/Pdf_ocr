import os
import json
import csv
import pikepdf
from datetime import datetime
from ocr_utils.logger import log_info, log_error

# -------------------------------
# Lee metadatos desde archivo CSV o JSON
# -------------------------------
def read_metadata_from_file(metadata_path):
    metadata_map = {}

    try:
        if metadata_path.endswith('.json'):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata_map = json.load(f)
        elif metadata_path.endswith('.csv'):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    filename = row.get("filename")
                    if filename:
                        metadata_map[filename] = {k: v for k, v in row.items() if k != "filename"}
        log_info(f"📄 Metadatos cargados desde: {metadata_path}")
    except Exception as e:
        log_error(f"❌ Error leyendo metadatos: {str(e)}")

    return metadata_map

# -------------------------------
# Inserta metadatos en un solo PDF
# -------------------------------
def insert_metadata_to_pdf(pdf_path, metadata: dict):
    try:
        with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
            pdf.metadata['Title'] = metadata.get('Title', '')
            pdf.metadata['Author'] = metadata.get('Author', 'OCR_App')
            pdf.metadata['Producer'] = metadata.get('Producer', 'OCR_App')
            pdf.metadata['Subject'] = metadata.get('Subject', '')
            pdf.metadata['CustomID'] = metadata.get('CustomID', f"ID-{int(datetime.now().timestamp())}")
            pdf.save(pdf_path)
        log_info(f"🧾 Metadatos insertados en: {os.path.basename(pdf_path)}")
    except Exception as e:
        log_error(f"❌ Error insertando metadatos en {os.path.basename(pdf_path)}: {str(e)}")

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
        log_info(f"📦 Metadatos aplicados en lote en carpeta: {folder_path}")
    except Exception as e:
        log_error(f"❌ Error en procesamiento masivo de metadatos: {str(e)}")
