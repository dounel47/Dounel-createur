from flask import Flask, jsonify, request, render_template
from flask_mail import Mail, Message
from flask_cors import CORS
from database import Database, init_database
import os
import sys
import traceback
import logging
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('app.log', mode='a', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
# Configuración de CORS más permisiva
CORS(app, resources={
    r"/*": {"origins": "*"}
})

# Configuración de correo electrónico
try:
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    
    mail = Mail(app)
except Exception as e:
    logging.error(f"Error configurando correo: {e}")
    mail = None

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

# Inicializar base de datos
try:
    db = Database()
except Exception as e:
    logging.error(f"Error inicializando base de datos: {e}")
    db = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cursos', methods=['GET'])
def obtener_cursos():
    try:
        cursos = db.find_documents('cursos')
        # Convertir ObjectId a string para serialización JSON
        for curso in cursos:
            curso['_id'] = str(curso['_id'])
        return jsonify(cursos), 200
    except Exception as e:
        logging.error(f"Error en obtener_cursos: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/curso/<curso_id>', methods=['GET'])
def obtener_curso(curso_id):
    try:
        curso = db.get_collection('cursos').find_one({"id": curso_id})
        if curso:
            curso['_id'] = str(curso['_id'])
            return jsonify(curso), 200
        return jsonify({"error": "Curso no encontrado"}), 404
    except Exception as e:
        logging.error(f"Error en obtener_curso: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/usuarios', methods=['POST'])
def registrar_usuario():
    try:
        datos_usuario = request.json
        resultado = db.insert_document('usuarios', datos_usuario)
        return jsonify({"mensaje": "Usuario registrado", "id": str(resultado.inserted_id)}), 201
    except Exception as e:
        logging.error(f"Error en registrar_usuario: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    return jsonify({
        "status": "ok",
        "database": "conectada" if db is not None else "no conectada",
        "mail": "configurado" if mail is not None else "no configurado"
    }), 200

def main():
    try:
        # Inicializar base de datos
        init_database()
        
        # Imprimir mensaje de inicio
        print("Servidor Flask iniciado en http://localhost:5000")
        print("Presiona Ctrl+C para detener el servidor")
        
        # Iniciar servidor
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logging.error(f"Error al iniciar el servidor: {e}")
        print(f"No se pudo iniciar el servidor: {e}")

if __name__ == '__main__':
    main()
