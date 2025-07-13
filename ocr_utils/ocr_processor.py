import os
import pytesseract

# Ruta al ejecutable de Tesseract (ajusta si es necesario)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

from pdf2image import convert_from_path
from PIL import Image
import cv2
import numpy as np
from fpdf import FPDF
from ocr_utils.logger import log_info, log_error

# -------------------------------
# Convierte un PDF en imágenes (una por página)
# -------------------------------
def convert_pdf_to_images(pdf_path, dpi=300):
    try:
        images = convert_from_path(pdf_path, dpi=dpi)
        log_info(f"📄 PDF convertido en {len(images)} imágenes")
        return images
    except Exception as e:
        log_error(f"❌ Error al convertir PDF a imágenes: {str(e)}")
        return []

# -------------------------------
# Preprocesa imagen para mejorar OCR
# -------------------------------
def preprocess_image(pil_image):
    try:
        img = np.array(pil_image.convert('L'))  # escala de grises
        _, img_bin = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        coords = np.column_stack(np.where(img_bin < 255))
        angle = cv2.minAreaRect(coords)[-1]
        angle = -(90 + angle) if angle < -45 else -angle

        (h, w) = img_bin.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        img_deskewed = cv2.warpAffine(img_bin, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        return Image.fromarray(img_deskewed)
    except Exception as e:
        log_error(f"⚠️ Error en preprocesamiento de imagen: {str(e)}")
        return pil_image

# -------------------------------
# Realiza OCR sobre una imagen (PIL)
# -------------------------------
def perform_ocr(image):
    try:
        text = pytesseract.image_to_string(image, lang='spa')
        print("🧪 Texto OCR extraído:\n", text)  # DEBUG
        return text
    except Exception as e:
        log_error(f"❌ Error en OCR: {str(e)}")
        return ""


# -------------------------------
# Guarda el texto extraído en archivo .txt
# -------------------------------
def save_ocr_text(text, output_path):
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        log_info(f"📝 Texto guardado en {output_path}")
    except Exception as e:
        log_error(f"❌ Error al guardar texto OCR: {str(e)}")

# -------------------------------
# Guarda el texto extraído como PDF
# -------------------------------


def save_text_as_pdf(text, output_path):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)

        # Reemplazar caracteres incompatibles
        clean_text = text.encode('latin-1', errors='replace').decode('latin-1')

        for line in clean_text.split('\n'):
            pdf.multi_cell(0, 10, line)

        pdf.output(output_path)
        log_info(f"📄 PDF de texto guardado en: {output_path}")
    except Exception as e:
        log_error(f"❌ Error al guardar PDF de texto: {str(e)}")

# -------------------------------
# Proceso completo: PDF a texto por página
# -------------------------------
def ocr_pdf_to_text(pdf_path, output_folder):
    log_info(f"🔁 OCR del archivo: {pdf_path}")
    images = convert_pdf_to_images(pdf_path)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]

    for idx, image in enumerate(images):
        page_number = idx + 1
        preprocessed = preprocess_image(image)
        text = perform_ocr(preprocessed)

        output_txt = os.path.join(output_folder, f"{base_name}_pagina_{page_number}.txt")
        save_ocr_text(text, output_txt)

        output_pdf = os.path.join(output_folder, f"{base_name}_pagina_{page_number}.pdf")
        save_text_as_pdf(text, output_pdf)
