import os
from PyPDF2 import PdfReader, PdfWriter
from logger import log_info, log_error  # Cambio: sin prefijo 'ocr_utils.'

# -------------------------------
# Divide PDF en páginas individuales
# -------------------------------
def split_pdf_by_page(pdf_path, output_folder):
    try:
        reader = PdfReader(pdf_path)
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]

        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)

            output_filename = f"{base_name}_pagina_{i+1}.pdf"
            output_path = os.path.join(output_folder, output_filename)

            with open(output_path, "wb") as f:
                writer.write(f)

            log_info(f" Página {i+1} guardada como: {safe_str(output_filename)}")
    except Exception as e:
        log_error(f" Error al dividir PDF {safe_str(pdf_path)}: {safe_str(e)}")


# -------------------------------
# Divide PDF por rangos personalizados
# Ejemplo de ranges: [(1, 3), (4, 6)] → páginas 1-3, 4-6
# -------------------------------
def split_pdf_by_ranges(pdf_path, ranges, output_folder):
    try:
        reader = PdfReader(pdf_path)
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]

        for idx, (start, end) in enumerate(ranges):
            writer = PdfWriter()
            for i in range(start-1, end):
                writer.add_page(reader.pages[i])

            output_filename = f"{base_name}_rango_{start}_a_{end}.pdf"
            output_path = os.path.join(output_folder, output_filename)

            with open(output_path, "wb") as f:
                writer.write(f)

            log_info(f" Rango {start}-{end} guardado como: {safe_str(output_filename)}")
    except Exception as e:
        log_error(f" Error al dividir por rangos en {safe_str(pdf_path)}: {safe_str(e)}")


# -------------------------------
# Renombra PDFs de una carpeta usando metadatos
# metadata_list: lista de diccionarios con campos 'filename', 'new_name'
# -------------------------------
def rename_split_pdfs(output_folder, metadata_list):
    try:
        for meta in metadata_list:
            old_file = os.path.join(output_folder, meta['filename'])
            new_file = os.path.join(output_folder, meta['new_name'])

            if os.path.exists(old_file):
                os.rename(old_file, new_file)
                log_info(f" Renombrado: {safe_str(meta['filename'])} → {safe_str(meta['new_name'])}")
            else:
                log_error(f" Archivo no encontrado para renombrar: {safe_str(meta['filename'])}")
    except Exception as e:
        log_error(f" Error al renombrar archivos: {safe_str(e)}")


# -------------------------------
# Limpia cadenas para evitar errores de codificación
# -------------------------------
def safe_str(obj):
    try:
        return str(obj)
    except Exception:
        try:
            return str(obj).encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        except Exception:
            return "[Error al convertir a string]"
