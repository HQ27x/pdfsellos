from flask import Flask, request, send_file, jsonify
import os
import time
import re
import traceback
from sellador import agregar_sello_pdf

# Configuración de la aplicación Flask
app = Flask(__name__)

# Directorios para archivos temporales
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

# Asegurar que los directorios existan
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def safe_filename(filename):
    """Convierte un nombre de archivo en uno seguro para el sistema de archivos."""
    return re.sub(r'[^\w\-_. ]', '_', filename)

@app.route('/')
def home():
    """Ruta de inicio para verificar que la API está funcionando."""
    return "API de Sellador de PDF está funcionando correctamente."

@app.route('/sellar_pdf', methods=['POST'])
def handle_sellado():
    """Maneja la solicitud de sellado de PDF."""
    # Variables para limpieza en el finally
    pdf_path = None
    sello_path = None
    output_path = None
    
    try:
        print("\n--- Nueva solicitud de sellado ---")
        
        # Verificar que los archivos se hayan enviado correctamente
        if 'pdf' not in request.files or 'sello' not in request.files:
            error_msg = "Faltan archivos. Asegúrate de enviar 'pdf' y 'sello'."
            print(f"❌ Error: {error_msg}")
            return jsonify({"error": error_msg}), 400

        pdf_file = request.files['pdf']
        sello_file = request.files['sello']
        posicion = request.form.get('posicion', 'bottom-right')
        
        print(f"📄 Archivo PDF recibido: {pdf_file.filename} ({pdf_file.content_type})")
        print(f"🖋️ Archivo de sello recibido: {sello_file.filename} ({sello_file.content_type})")
        
        # Validaciones básicas
        if pdf_file.filename == '':
            error_msg = "No se seleccionó ningún archivo PDF"
            print(f"❌ {error_msg}")
            return jsonify({"error": error_msg}), 400
            
        if sello_file.filename == '':
            error_msg = "No se seleccionó ningún archivo de sello"
            print(f"❌ {error_msg}")
            return jsonify({"error": error_msg}), 400
        
        # Validar extensión del PDF
        if not pdf_file.filename.lower().endswith('.pdf'):
            error_msg = f"El archivo {pdf_file.filename} no es un PDF válido"
            print(f"❌ {error_msg}")
            return jsonify({"error": error_msg}), 400
        
        # Validar tipo de archivo de sello
        sello_ext = os.path.splitext(sello_file.filename)[1].lower()
        if sello_ext not in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.pdf']:
            error_msg = f"El archivo {sello_file.filename} no es una imagen o PDF válido"
            print(f"❌ {error_msg}")
            return jsonify({"error": error_msg}), 400
            
        # Validar posición
        posiciones_validas = ["top-left", "top-right", "bottom-left", "bottom-right"]
        if posicion not in posiciones_validas:
            error_msg = f"Posición no válida. Usar: {', '.join(posiciones_validas)}"
            print(f"❌ {error_msg}")
            return jsonify({"error": error_msg}), 400

        # Generar nombres de archivo seguros
        timestamp = str(int(time.time()))
        pdf_filename = f"{timestamp}_{safe_filename(pdf_file.filename)}"
        sello_filename = f"{timestamp}_{safe_filename(sello_file.filename)}"
        output_filename = f"{timestamp}_sellado_{safe_filename(pdf_file.filename)}"

        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
        sello_path = os.path.join(UPLOAD_FOLDER, sello_filename)
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        print(f"💾 Guardando archivos temporales...")
        print(f"   - PDF: {pdf_path}")
        print(f"   - Sello: {sello_path}")
        print(f"   - Salida: {output_path}")
        
        # Guardar archivos temporalmente
        pdf_file.save(pdf_path)
        sello_file.save(sello_path)
        
        # Verificar que los archivos se hayan guardado correctamente
        if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
            error_msg = f"Error al guardar el archivo PDF: {pdf_path}"
            print(f"❌ {error_msg}")
            return jsonify({"error": error_msg}), 500
            
        if not os.path.exists(sello_path) or os.path.getsize(sello_path) == 0:
            error_msg = f"Error al guardar el archivo de sello: {sello_path}"
            print(f"❌ {error_msg}")
            return jsonify({"error": error_msg}), 500
            
        print("✅ Archivos guardados correctamente")
        
        # Procesar el PDF con el sello
        print("🔄 Procesando PDF con sello...")
        try:
            agregar_sello_pdf(
                pdf_entrada=pdf_path,
                img_sello=sello_path,
                pdf_salida=output_path,
                posicion=posicion,
                tamano_sello=(100, 100)
            )
        except Exception as e:
            error_msg = f"Error al procesar el PDF: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            return jsonify({"error": error_msg}), 500
        
        print("✅ PDF procesado correctamente")
        
        # Verificar que el archivo de salida se haya creado
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            error_msg = f"Error: No se pudo generar el archivo de salida: {output_path}"
            print(f"❌ {error_msg}")
            return jsonify({"error": error_msg}), 500

        return send_file(
            output_path, 
            as_attachment=True,
            download_name=f"sellado_{pdf_file.filename}",
            as_attachment_kwargs={"mimetype": "application/pdf"}
        )

    except Exception as e:
        error_msg = f"Error inesperado: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        return jsonify({"error": error_msg}), 500

    finally:
        # Limpieza de archivos temporales
        print("🧹 Limpiando archivos temporales...")
        for file_path in [pdf_path, sello_path, output_path]:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"   - Eliminado: {file_path}")
                except Exception as e:
                    print(f"   - Error al eliminar {file_path}: {str(e)}")
        print("✅ Limpieza completada")

# Configuración para ejecución local
if __name__ == '__main__':
    print("Iniciando servidor de prueba local en http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
