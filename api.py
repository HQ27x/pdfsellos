# --- api.py ---
from flask import Flask, request, send_file, jsonify
import os
import time
from sellador import agregar_sello_pdf  # Importamos la función

# Creamos la aplicación de Flask
app = Flask(__name__)

# Directorios para guardar archivos temporalmente
# Render tiene un sistema de archivos temporal, esto funcionará bien.
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def home():
    # Una ruta simple para saber que la API está viva
    return "API de Sellador de PDF está funcionando."

@app.route('/sellar_pdf', methods=['POST'])
def handle_sellado():
    if 'pdf' not in request.files or 'sello' not in request.files:
        return jsonify({"error": "Faltan archivos. Asegúrate de enviar 'pdf' y 'sello'."}), 400

    pdf_file = request.files['pdf']
    sello_file = request.files['sello']
    posicion = request.form.get('posicion', 'bottom-right')
    
    posiciones_validas = ["top-left", "top-right", "bottom-left", "bottom-right"]
    if posicion not in posiciones_validas:
        return jsonify({"error": f"Posición no válida. Usar: {posiciones_validas}"}), 400

    timestamp = str(int(time.time()))
    
    pdf_filename = f"{timestamp}_{pdf_file.filename}"
    sello_filename = f"{timestamp}_{sello_file.filename}"
    output_filename = f"{timestamp}_sellado_{pdf_file.filename}"

    pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
    sello_path = os.path.join(UPLOAD_FOLDER, sello_filename)
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    pdf_file.save(pdf_path)
    sello_file.save(sello_path)

    try:
        agregar_sello_pdf(
            pdf_entrada=pdf_path,
            img_sello=sello_path,
            pdf_salida=output_path,
            posicion=posicion,
            tamano_sello=(100, 100)
        )

        return send_file(
            output_path, 
            as_attachment=True,
            download_name=f"sellado_{pdf_file.filename}"
        )

    except Exception as e:
        return jsonify({"error": f"Ocurrió un error: {str(e)}"}), 500

    finally:
        # Limpiamos los archivos temporales
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        if os.path.exists(sello_path):
            os.remove(sello_path)
        if os.path.exists(output_path):
             # Es buena idea borrar el de salida también después de enviarlo
             # send_file a veces lo maneja, pero aseguramos
             try:
                os.remove(output_path)
             except:
                pass # El archivo podría estar en uso, pero está bien

# --- ESTE BLOQUE SOLO SE USA PARA PRUEBAS LOCALES ---
# Render ignorará esto y usará Gunicorn
if __name__ == '__main__':
    print("Iniciando servidor de prueba local en http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
