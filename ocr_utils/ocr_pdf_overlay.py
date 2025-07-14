import fitz  # PyMuPDF
import io

def create_searchable_pdf(pil_image, ocr_text, output_path):
    # Crear nuevo documento PDF
    pdf = fitz.open()

    # Convertir la imagen a bytes (formato PNG)
    img_bytes_io = io.BytesIO()
    pil_image.save(img_bytes_io, format='PNG')
    img_bytes = img_bytes_io.getvalue()

    # Obtener tamaño de imagen y crear página
    img_width, img_height = pil_image.width, pil_image.height
    rect = fitz.Rect(0, 0, img_width, img_height)
    page = pdf.new_page(width=img_width, height=img_height)

    # Insertar imagen como fondo
    page.insert_image(rect, stream=img_bytes)

    # Definir rectángulo centrado con márgenes (10%)
    margin_x = img_width * 0.1
    margin_y = img_height * 0.1
    text_rect = fitz.Rect(
        margin_x,
        margin_y,
        img_width - margin_x,
        img_height - margin_y
    )

    # Insertar texto OCR invisible pero seleccionable
    page.insert_textbox(
        text_rect,
        ocr_text,
        fontsize=48,                # Tamaño grande para cubrir bien
        fontname="helv",
        fontfile=None,
        color=(1, 1, 1, 0),         # RGBA: blanco completamente transparente
        overlay=True,
        render_mode=3               # Invisible pero copiable/seleccionable
    )

    # Guardar PDF
    pdf.save(output_path)
    pdf.close()
