import os
import json
from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import pytesseract
from PIL import Image
from io import BytesIO
import base64
from flask_cors import CORS
import re
from sqlalchemy import inspect

#Configuración Flask y db
app = Flask(__name__)
CORS(app)

#Configuramos la ruta de la base de datos SQLite
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'skilllens.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'clave-secreta'  #En producción, manejar de forma más segura 

db = SQLAlchemy(app)

#Modelos db
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class CV(db.Model):
    __tablename__ = 'cvs'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    image_base64 = db.Column(db.Text, nullable=True)
    nombre = db.Column(db.String(120), nullable=True)
    experiencia = db.Column(db.String(250), nullable=True)
    educacion = db.Column(db.String(250), nullable=True)
    full_text = db.Column(db.Text, nullable=True)

with app.app_context():
    db.create_all()
    inspector = inspect(db.engine)
    if 'cvs' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('cvs')]
        if 'full_text' not in cols:
            db.engine.execute('ALTER TABLE cvs ADD COLUMN full_text TEXT')

#Rutas autenticación
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Campos requeridos faltantes'}), 400

    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'message': 'El usuario ya existe'}), 400

    hashed_password = generate_password_hash(data['password'])
    new_user = User(email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Usuario registrado con éxito', 'user_id': new_user.id}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Campos requeridos faltantes'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    if not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Credenciales inválidas'}), 401

    return jsonify({'message': 'Login exitoso', 'user_id': user.id}), 200


#Rutas Escaneo
@app.route('/cv/scan', methods=['POST'])
def scan_cv():
    user_id = request.form.get('user_id')
    if not user_id:
        return jsonify({'message': 'Falta user_id'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Usuario no existe'}), 404

    file = request.files.get('file')
    if not file:
        return jsonify({'message': 'No se envió ningún archivo'}), 400

    file_bytes = file.read()
    image_base64 = base64.b64encode(file_bytes).decode('utf-8')

    image_pil = Image.open(BytesIO(file_bytes))
    text_extracted = pytesseract.image_to_string(image_pil, lang='spa')

    #Parseo básico del OCR:
    lines = [l.strip() for l in text_extracted.splitlines() if l.strip()]
    #Nombre: primera línea no vacía
    nombre_detectado = lines[0] if lines else ''

    #Experiencia: sección entre 'Experiencia' y 'Educación'
    experiencia_detectada = ''
    for i, l in enumerate(lines):
        if re.search(r'experiencia', l, re.IGNORECASE):
            exp_lines = []
            for sub in lines[i+1:]:
                if re.search(r'educaci', sub, re.IGNORECASE):
                    break
                exp_lines.append(sub)
            experiencia_detectada = ' '.join(exp_lines)
            break

    #Educación: sección tras 'Educación'
    educacion_detectada = ''
    for i, l in enumerate(lines):
        if re.search(r'educaci', l, re.IGNORECASE):
            edu_lines = lines[i+1:]
            educacion_detectada = ' '.join(edu_lines)
            break

    new_cv = CV(
        owner_id=user.id,
        image_base64=image_base64,
        nombre=nombre_detectado,
        experiencia=experiencia_detectada,
        educacion=educacion_detectada,
        full_text=text_extracted
    )
    db.session.add(new_cv)
    db.session.commit()
    #Exportar a JSON
    export_cv_to_json(new_cv)
    return jsonify({
        'message': 'Documento escaneado y almacenado',
        'cv_id': new_cv.id,
        'full_text': text_extracted,
        'nombre': nombre_detectado,
        'experiencia': experiencia_detectada,
        'educacion': educacion_detectada
    }), 201

@app.route('/cv/create', methods=['POST'])
def create_cv():
    data = request.json
    if not data:
        return jsonify({'message': 'Datos no válidos'}), 400

    user_id = data.get('user_id')
    nombre = data.get('nombre')
    experiencia = data.get('experiencia')
    educacion = data.get('educacion')
    full_text = data.get('full_text')

    if not (user_id and nombre and experiencia and educacion):
        return jsonify({'message': 'Faltan campos obligatorios: user_id, nombre, experiencia, educacion'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    new_cv = CV(
        owner_id=user.id,
        nombre=nombre,
        experiencia=experiencia,
        educacion=educacion,
        full_text=full_text
    )
    db.session.add(new_cv)
    db.session.commit()
    #Exportar a JSON
    export_cv_to_json(new_cv)
    return jsonify({'message': 'Hoja de vida creada manualmente', 'cv_id': new_cv.id}), 201

@app.route('/cv', methods=['GET'])
def get_cvs():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'message': 'El parámetro user_id es obligatorio'}), 400

    cvs = CV.query.filter_by(owner_id=user_id).all()
    result = []
    for cv in cvs:
        result.append({
            'id': cv.id,
            'owner_id': cv.owner_id,
            'nombre': cv.nombre,
            'experiencia': cv.experiencia,
            'educacion': cv.educacion,
            'full_text': cv.full_text
        })
    return jsonify(result), 200

@app.route('/cv/<int:cv_id>', methods=['GET'])
def get_one_cv(cv_id):
    cv = CV.query.get(cv_id)
    if not cv:
        return jsonify({'message': 'CV no encontrado'}), 404

    return jsonify({
        'id': cv.id,
        'owner_id': cv.owner_id,
        'nombre': cv.nombre,
        'experiencia': cv.experiencia,
        'educacion': cv.educacion,
        'full_text': cv.full_text
    }), 200

@app.route('/cv/<int:cv_id>', methods=['PUT'])
def update_cv(cv_id):
    data = request.json
    cv = CV.query.get(cv_id)
    if not cv:
        return jsonify({'message': 'CV no encontrado'}), 404

    if data.get('nombre'):
        cv.nombre = data['nombre']
    if data.get('experiencia'):
        cv.experiencia = data['experiencia']
    if data.get('educacion'):
        cv.educacion = data['educacion']
    if data.get('full_text'):
        cv.full_text = data['full_text']

    db.session.commit()
    return jsonify({'message': 'CV actualizado con éxito'}), 200

@app.route('/cv/<int:cv_id>', methods=['DELETE'])
def delete_cv(cv_id):
    cv = CV.query.get(cv_id)
    if not cv:
        return jsonify({'message': 'CV no encontrado'}), 404
    db.session.delete(cv)
    db.session.commit()
    return jsonify({'message': 'CV eliminado'}), 200


def export_cv_to_json(cv):
    #Añade el CV dado al fichero cvs_export.json en la raíz del proyecto.
    
    data = {
        'id': cv.id,
        'owner_id': cv.owner_id,
        'nombre': cv.nombre,
        'experiencia': cv.experiencia,
        'educacion': cv.educacion,
        'full_text': cv.full_text
    }
    file_path = os.path.join(BASE_DIR, 'cvs_export.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            existing = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing = []
    existing.append(data)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    app.run(debug=True)
