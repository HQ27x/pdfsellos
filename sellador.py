# --- sellador.py ---
import fitz  # PyMuPDF
import os

def agregar_sello_pdf(pdf_entrada, img_sello, pdf_salida, posicion="bottom-right", tamano_sello=(100, 100), margen=15):
    """
    Agrega una imagen (sello) a todas las páginas de un PDF en una posición específica.
    """
    
    doc = fitz.open(pdf_entrada)
    sello = fitz.open(img_sello)

    ancho_sello, alto_sello = tamano_sello

    for i in range(len(doc)):
        page = doc[i]
        page_rect = page.rect

        if posicion == "top-left":
            x0 = margen
            y0 = margen
        elif posicion == "top-right":
            x0 = page_rect.width - ancho_sello - margen
            y0 = margen
        elif posicion == "bottom-left":
            x0 = margen
            y0 = page_rect.height - alto_sello - margen
        elif posicion == "bottom-right":
            x0 = page_rect.width - ancho_sello - margen
            y0 = page_rect.height - alto_sello - margen
        else:
            x0 = page_rect.width - ancho_sello - margen
            y0 = page_rect.height - alto_sello - margen

        rect_sello = fitz.Rect(x0, y0, x0 + ancho_sello, y0 + alto_sello)
        
        page.show_pdf_page(rect_sello, sello, 0) 

    doc.save(pdf_salida)
    doc.close()
    sello.close()
    
    # Quitamos el print, ya que en la API es mejor devolver la respuesta
    # print(f"¡Éxito! PDF guardado en: {pdf_salida}")
