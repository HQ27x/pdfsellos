# 🚀 Servidor API - Sellador de PDFs

Este es el código que va en GitHub y se despliega en Render para crear la API.

## 📁 Archivos del Servidor

- `sellador.py` - Motor de sellado de PDFs
- `api.py` - API REST con Flask
- `requirements.txt` - Dependencias del servidor
- `.gitignore` - Archivos a ignorar en Git
- `README_SERVIDOR.md` - Esta documentación

## 🎯 Propósito

Este servidor proporciona una API REST que:
- Recibe archivos PDF y de sello
- Aplica el sello a todas las páginas del PDF
- Devuelve el PDF sellado
- Maneja múltiples posiciones de sello

## 🛠️ Instalación Local (Para Pruebas)

1. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ejecuta el servidor:**
   ```bash
   python api.py
   ```

3. **La API estará disponible en:** `http://127.0.0.1:5000`

## 🌐 Endpoints de la API

### GET `/`
- **Descripción:** Verificar que la API está funcionando
- **Respuesta:** "API de Sellador de PDF está funcionando."

### POST `/sellar_pdf`
- **Descripción:** Sellar un PDF con una imagen
- **Content-Type:** `multipart/form-data`
- **Parámetros:**
  - `pdf` (file, requerido): Archivo PDF
  - `sello` (file, requerido): Imagen del sello
  - `posicion` (string, opcional): Posición del sello
- **Respuesta:** Archivo PDF sellado para descargar

## 📋 Posiciones Válidas

- `top-left` - Esquina superior izquierda
- `top-right` - Esquina superior derecha
- `bottom-left` - Esquina inferior izquierda
- `bottom-right` - Esquina inferior derecha (por defecto)

## 🚀 Despliegue en Render

### 1. Preparar el Repositorio

```bash
# Inicializar Git
git init

# Agregar archivos
git add .

# Primer commit
git commit -m "API de sellado de PDFs"

# Conectar con GitHub
git remote add origin https://github.com/tu-usuario/tu-repositorio.git

# Subir código
git push -u origin main
```

### 2. Configurar en Render

1. Ve a [Render Dashboard](https://dashboard.render.com)
2. Clic en **"New +"** → **"Web Service"**
3. Conecta tu cuenta de GitHub
4. Selecciona tu repositorio
5. Configuración:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn api:app`
   - **Python Version:** 3.9+ (automático)
6. Clic en **"Create Web Service"**

### 3. Variables de Entorno (Opcional)

Si necesitas configuraciones especiales, puedes agregar:
- `PYTHON_VERSION`: 3.9
- `PORT`: 10000 (automático en Render)

## 🔧 Configuración Avanzada

### Personalizar Tamaño del Sello

Edita en `api.py` línea 60:
```python
tamano_sello=(150, 150)  # Cambia el tamaño aquí
```

### Personalizar Margen

Edita en `sellador.py` línea 4:
```python
margen=20  # Cambia el margen aquí
```

### Agregar Autenticación

Puedes agregar autenticación básica en `api.py`:
```python
from flask import request, abort

def verificar_auth():
    auth = request.authorization
    if not auth or auth.username != 'usuario' or auth.password != 'contraseña':
        abort(401)
    return True

@app.route('/sellar_pdf', methods=['POST'])
def handle_sellado():
    verificar_auth()  # Agregar esta línea
    # ... resto del código
```

## 📊 Monitoreo y Logs

### Ver Logs en Render
1. Ve a tu servicio en Render Dashboard
2. Clic en "Logs"
3. Revisa errores y actividad

### Logs Locales
```bash
# Ejecutar con logs detallados
python api.py
```

## 🐛 Solución de Problemas

### Error: "Build failed"
- Verifica que `requirements.txt` esté en la raíz
- Asegúrate de que el comando de build sea correcto
- Revisa que no haya errores de sintaxis en Python

### Error: "Start failed"
- Verifica que el comando de inicio sea: `gunicorn api:app`
- Revisa que todas las dependencias estén en `requirements.txt`
- Verifica que no haya errores en el código

### Error: "Module not found"
- Asegúrate de que `PyMuPDF` esté en `requirements.txt`
- Verifica que `Flask` esté en `requirements.txt`
- Revisa que `gunicorn` esté en `requirements.txt`

### API no responde
- Verifica que el servicio esté "Live" en Render
- Revisa los logs para errores
- Asegúrate de que la URL sea correcta

## 🔒 Seguridad

### Recomendaciones:
- No subas archivos sensibles al repositorio
- Usa variables de entorno para configuraciones
- Considera agregar límites de tamaño de archivo
- Implementa autenticación si es necesario

### Límites de Archivo:
```python
# En api.py, puedes agregar:
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@app.route('/sellar_pdf', methods=['POST'])
def handle_sellado():
    # Verificar tamaño de archivos
    if request.content_length > MAX_FILE_SIZE:
        return jsonify({"error": "Archivo demasiado grande"}), 413
    # ... resto del código
```

## 📈 Escalabilidad

### Para mayor tráfico:
- Considera usar Redis para cache
- Implementa rate limiting
- Usa un CDN para archivos estáticos
- Considera bases de datos para logs

## 🧪 Pruebas

### Probar Localmente:
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
python api.py

# Probar con Postman o curl
curl -X POST http://127.0.0.1:5000/sellar_pdf \
  -F "pdf=@documento.pdf" \
  -F "sello=@sello.png" \
  -F "posicion=bottom-right"
```

### Probar en Render:
```bash
# Usar la URL que te dé Render
curl -X POST https://tu-api.onrender.com/sellar_pdf \
  -F "pdf=@documento.pdf" \
  -F "sello=@sello.png" \
  -F "posicion=bottom-right"
```

---

**¡Tu API está lista para procesar PDFs! 🎉**
