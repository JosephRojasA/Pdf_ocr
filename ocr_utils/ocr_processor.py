import os
import traceback
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
from fpdf import FPDF
import easyocr
from ocr_utils.logger import log_info, log_error
import re

# -------------------------------
# Configuración
# -------------------------------
DEBUG = True
USE_PREPROCESSING = True
OCR_DPI = 400  # Mayor resolución para mejorar OCR

# -------------------------------
# Inicializar lector EasyOCR
# -------------------------------
reader = easyocr.Reader(['es'], gpu=False)

# -------------------------------
# Convierte PDF a imágenes
# -------------------------------
def convert_pdf_to_images(pdf_path, dpi=OCR_DPI):
    try:
        images = convert_from_path(pdf_path, dpi=dpi)
        log_info(f"PDF convertido en {len(images)} imágenes")
        return images
    except Exception as e:
        msg = f"Error al convertir PDF a imágenes: {safe_str(e)}"
        log_error(msg)
        if DEBUG: print(msg)
        return []

# -------------------------------
# Preprocesamiento avanzado de imagen
# -------------------------------
def preprocess_image(pil_image):
    try:
        img = pil_image.convert('L')  # Escala de grises

        # Aumentar contraste
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)

        # Filtro para mejorar bordes
        img = img.filter(ImageFilter.MedianFilter(size=3))

        img_np = np.array(img)

        # Umbral binario (Otsu) y limpieza de ruido
        _, img_bin = cv2.threshold(img_np, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        img_bin = cv2.medianBlur(img_bin, 3)

        # Corrección de inclinación (deskew)
        coords = np.column_stack(np.where(img_bin < 255))
        if coords.any():
            angle = cv2.minAreaRect(coords)[-1]
            angle = -(90 + angle) if angle < -45 else -angle
            (h, w) = img_bin.shape
            M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
            img_rotated = cv2.warpAffine(img_bin, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        else:
            img_rotated = img_bin

        return Image.fromarray(img_rotated)
    except Exception as e:
        msg = f"Error en preprocesamiento de imagen: {safe_str(e)}"
        log_error(msg)
        if DEBUG: print(msg)
        return pil_image

# -------------------------------
# OCR con EasyOCR
# -------------------------------
def perform_ocr(image):
    try:
        img_np = np.array(image)
        results = reader.readtext(img_np, detail=0, paragraph=True)
        clean_text = "\n".join([line.strip() for line in results if line.strip()])
        return clean_text
    except Exception as e:
        trace = traceback.format_exc()
        msg = "Error en EasyOCR:\n" + safe_str(trace)
        log_error(msg)
        if DEBUG: print(msg)
        return ""




# -------------------------------
# Guarda texto como .txt
# -------------------------------
def save_ocr_text(text, output_path):
    try:
        with open(output_path, 'w', encoding='utf-8', errors='ignore') as f:
            f.write(text)
        log_info(f"Texto guardado en {output_path}")
    except Exception as e:
        msg = f"Error al guardar texto OCR: {safe_str(e)}"
        log_error(msg)
        if DEBUG: print(msg)

# -------------------------------
# Guarda texto como PDF
# -------------------------------
def save_text_as_pdf(text, output_path):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.set_auto_page_break(auto=True, margin=15)

        clean_text = text.encode('latin-1', errors='replace').decode('latin-1', errors='replace')

        for line in clean_text.split('\n'):
            pdf.multi_cell(0, 10, line)

        pdf.output(output_path)
        log_info(f"PDF de texto guardado en: {output_path}")
    except Exception as e:
        msg = f"Error al guardar PDF de texto: {safe_str(e)}"
        log_error(msg)
        if DEBUG: print(msg)

import re

def is_valid_text(text):
    # Filtrar caracteres no imprimibles
    text = re.sub(r'[^\x20-\x7EñÑáéíóúÁÉÍÓÚüÜ]', '', text)

    # Eliminar espacios dobles
    cleaned = re.sub(r'\s+', ' ', text).strip()

    # Demasiado corto
    if len(cleaned) < 20:
        return False

    # Evaluar contenido alfanumérico
    letters = len(re.findall(r'[a-zA-ZáéíóúñÑÁÉÍÓÚÜü]', cleaned))
    digits = len(re.findall(r'\d', cleaned))
    symbols = len(re.findall(r'[^a-zA-Z0-9\s]', cleaned))

    total_chars = len(cleaned)
    if total_chars == 0:
        return False

    # Criterios de calidad
    symbol_ratio = symbols / total_chars
    letter_ratio = letters / total_chars

    if symbol_ratio > 0.5:  # Demasiados símbolos
        return False
    if letter_ratio < 0.4:  # Muy pocas letras
        return False

    # Si pasa los filtros, el texto es considerado válido
    return True

# -------------------------------
# Flujo principal: OCR PDF completo
# -------------------------------
def ocr_pdf_to_text(pdf_path, output_folder):
    log_info(f"OCR del archivo: {pdf_path}")
    images = convert_pdf_to_images(pdf_path)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    total_text = ""

    for idx, image in enumerate(images):
        page_number = idx + 1
        processed_image = preprocess_image(image) if USE_PREPROCESSING else image
        text = perform_ocr(processed_image)

        if text.strip() and is_valid_text(text):
            output_txt = os.path.join(output_folder, f"{base_name}_pagina_{page_number}.txt")
            save_ocr_text(text, output_txt)

            output_pdf = os.path.join(output_folder, f"{base_name}_pagina_{page_number}_ocr.pdf")
            save_text_as_pdf(text, output_pdf)

            total_text += text + "\n\n"
        else:
            log_error(f"OCR fallido o sin texto útil en página {page_number} de {base_name}")

    if not total_text.strip():
        log_error(f"OCR fallido o sin texto: {base_name}.pdf")

# -------------------------------
# Utilidad segura para logs
# -------------------------------
def safe_str(obj):
    try:
        return str(obj)
    except Exception:
        try:
            return str(obj).encode("utf-8", errors="replace").decode("utf-8", errors="replace")
        except Exception:
            return "[Error al convertir a string]"
