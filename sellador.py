import fitz  # PyMuPDF
import os
import sys
import traceback

def validar_pdf(ruta_archivo):
    """Valida que un archivo sea un PDF válido."""
    try:
        with open(ruta_archivo, 'rb') as f:
            header = f.read(4)
            if header != b'%PDF':
                return False, "El archivo no es un PDF válido (falta el encabezado %PDF)"
        
        # Intentar abrir con PyMuPDF para validar más a fondo
        doc = fitz.open(ruta_archivo)
        if not doc.is_pdf:
            doc.close()
            return False, "El archivo no es un PDF válido"
        
        # Verificar que el PDF no esté vacío
        if len(doc) == 0:
            doc.close()
            return False, "El PDF está vacío"
            
        doc.close()
        return True, ""
    except Exception as e:
        return False, f"Error al validar el PDF: {str(e)}"

def validar_imagen(ruta_archivo):
    """Valida que un archivo sea una imagen o PDF válido."""
    try:
        # Verificar si es un PDF
        if ruta_archivo.lower().endswith('.pdf'):
            return validar_pdf(ruta_archivo)
            
        # Si no es PDF, intentar abrir como imagen
        try:
            doc = fitz.open(ruta_archivo)
            if not doc.is_pdf:  # Si no es PDF, es una imagen
                return True, ""
            doc.close()
            return True, ""
        except:
            # Si falla, intentar abrir con otro método
            try:
                import imghdr
                img_type = imghdr.what(ruta_archivo)
                if img_type is not None:
                    return True, ""
                return False, "El archivo no es una imagen o PDF válido"
            except:
                return False, "No se pudo validar el archivo de imagen"
    except Exception as e:
        return False, f"Error al validar la imagen: {str(e)}"

def agregar_sello_pdf(pdf_entrada, img_sello, pdf_salida, posicion="bottom-right", tamano_sello=(100, 100), margen=15):
    """
    Agrega una imagen (sello) a todas las páginas de un PDF en una posición específica.
    
    Args:
        pdf_entrada (str): Ruta al archivo PDF de entrada.
        img_sello (str): Ruta al archivo de imagen o PDF del sello.
        pdf_salida (str): Ruta donde se guardará el PDF resultante.
        posicion (str): Posición del sello. Valores posibles: 'top-left', 'top-right', 'bottom-left', 'bottom-right'.
        tamano_sello (tuple): Tamaño del sello (ancho, alto) en píxeles.
        margen (int): Margen desde los bordes en píxeles.
        
    Returns:
        tuple: (éxito, mensaje) donde éxito es booleano y mensaje es un string descriptivo.
    """
    doc = None
    sello_doc = None
    
    try:
        # Validar parámetros de entrada
        if not os.path.exists(pdf_entrada):
            raise FileNotFoundError(f"El archivo PDF de entrada no existe: {pdf_entrada}")
            
        if not os.path.exists(img_sello):
            raise FileNotFoundError(f"El archivo de sello no existe: {img_sello}")
            
        # Validar que el PDF de entrada sea válido
        es_valido, mensaje = validar_pdf(pdf_entrada)
        if not es_valido:
            raise ValueError(f"PDF de entrada inválido: {mensaje}")
            
        # Validar que el sello sea una imagen o PDF válido
        es_valido, mensaje = validar_imagen(img_sello)
        if not es_valido:
            raise ValueError(f"Archivo de sello inválido: {mensaje}")
        
        # Abrir el documento PDF
        doc = fitz.open(pdf_entrada)
        
        # Verificar que el PDF no esté protegido con contraseña
        if doc.is_encrypted:
            try:
                # Intentar abrir sin contraseña (puede fallar si requiere contraseña)
                doc.authenticate("")
            except:
                raise ValueError("El PDF está protegido con contraseña y no se puede editar")
        
        # Determinar si el sello es un PDF o una imagen
        es_sello_pdf = img_sello.lower().endswith('.pdf')
        
        if es_sello_pdf:
            # Si el sello es un PDF, abrirlo
            sello_doc = fitz.open(img_sello)
            if len(sello_doc) == 0:
                raise ValueError("El archivo PDF del sello está vacío")
        
        ancho_sello, alto_sello = tamano_sello
        
        # Procesar cada página del PDF
        for i in range(len(doc)):
            page = doc[i]
            page_rect = page.rect
            
            # Calcular posición del sello
            if posicion == "top-left":
                x0 = margen
                y0 = margen
            elif posicion == "top-right":
                x0 = page_rect.width - ancho_sello - margen
                y0 = margen
            elif posicion == "bottom-left":
                x0 = margen
                y0 = page_rect.height - alto_sello - margen
            else:  # bottom-right (por defecto)
                x0 = page_rect.width - ancho_sello - margen
                y0 = page_rect.height - alto_sello - margen
            
            rect_sello = fitz.Rect(x0, y0, x0 + ancho_sello, y0 + alto_sello)
            
            # Insertar el sello en la página
            if es_sello_pdf:
                # Si el sello es un PDF, insertar la primera página
                page.show_pdf_page(rect_sello, sello_doc, 0)
            else:
                # Si el sello es una imagen, insertarla directamente
                page.insert_image(rect_sello, filename=img_sello)
        
        # Guardar el documento resultante
        doc.save(pdf_salida, deflate=True, garbage=3)
        
        # Verificar que el archivo de salida se haya creado correctamente
        if not os.path.exists(pdf_salida) or os.path.getsize(pdf_salida) == 0:
            raise IOError("No se pudo guardar el archivo de salida")
            
        return True, "PDF procesado correctamente"
        
    except Exception as e:
        # Registrar el error para depuración
        error_msg = f"Error en agregar_sello_pdf: {str(e)}"
        print(error_msg, file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return False, error_msg
        
    finally:
        # Asegurarse de cerrar los documentos
        if doc is not None:
            doc.close()
        if sello_doc is not None:
            sello_doc.close()
