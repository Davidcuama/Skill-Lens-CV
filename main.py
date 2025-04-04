import os
from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import pytesseract
from PIL import Image
from io import BytesIO
import base64
###########################################################
#Configuración flask y base de datos
###########################################################
app = Flask(__name__)

#Configuramos la ruta de la base de datos SQLite
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'skilllens.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'clave-secreta'  
db = SQLAlchemy(app)
###########################################################
#Creación de base de datos
###########################################################
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
    #Campos extraídos o definidos manualmente o tras escaneo
    nombre = db.Column(db.String(120), nullable=True)
    experiencia = db.Column(db.String(250), nullable=True)
    educacion = db.Column(db.String(250), nullable=True)

#Creación de tablas en caso de que no existan
with app.app_context():
    db.create_all()
###########################################################
#Autenticación
###########################################################
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Campos requeridos faltantes'}), 400

    #Verificar si ya existe un usuario con el mismo email
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
###########################################################
#Rutas request / OCR / CV
###########################################################
@app.route('/cv/scan', methods=['POST'])
def scan_cv():
    """
    Escanea un documento (imagen) y realiza el escaneo con OCR y guarda la información en el DB
    - Debe recibir un user_id (simulando autenticación)
    """
    user_id = request.form.get('user_id')  
    if not user_id:
        return jsonify({'message': 'Falta user_id'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Usuario no existe'}), 404

    file = request.files.get('file')
    if not file:
        return jsonify({'message': 'No se envió ningún archivo'}), 400

    #Convertir la imagen a base64 para guardarla
    file_bytes = file.read()
    image_base64 = base64.b64encode(file_bytes).decode('utf-8')

    #OCR con pytesseract
    image_pil = Image.open(BytesIO(file_bytes))
    text_extracted = pytesseract.image_to_string(image_pil, lang='spa')  

    nombre_detectado = 'Detectado OCR'
    experiencia_detectada = 'Experiencia (ejemplo OCR)'
    educacion_detectada = 'Educación (ejemplo OCR)'

    #Crear registro CV
    new_cv = CV(
        owner_id=user.id,
        image_base64=image_base64,
        nombre=nombre_detectado,
        experiencia=experiencia_detectada,
        educacion=educacion_detectada
    )
    db.session.add(new_cv)
    db.session.commit()

    return jsonify({
        'message': 'Documento escaneado y almacenado',
        'cv_id': new_cv.id,
        'extracted_text': text_extracted
    }), 201

@app.route('/cv/create', methods=['POST'])
def create_cv():
    """
    Crea una hoja de vida manualmente 
    """
    data = request.json
    if not data:
        return jsonify({'message': 'Datos no válidos'}), 400

    user_id = data.get('user_id')
    nombre = data.get('nombre')
    experiencia = data.get('experiencia')
    educacion = data.get('educacion')

    if not (user_id and nombre and experiencia and educacion):
        return jsonify({'message': 'Todos los campos (user_id, nombre, experiencia, educacion) son obligatorios'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    new_cv = CV(
        owner_id=user.id,
        nombre=nombre,
        experiencia=experiencia,
        educacion=educacion
    )
    db.session.add(new_cv)
    db.session.commit()

    return jsonify({'message': 'Hoja de vida creada manualmente', 'cv_id': new_cv.id}), 201

@app.route('/cv', methods=['GET'])
def get_cvs():
    all_cvs = CV.query.all()
    result = []
    for cv in all_cvs:
        result.append({
            'id': cv.id,
            'owner_id': cv.owner_id,
            'nombre': cv.nombre,
            'experiencia': cv.experiencia,
            'educacion': cv.educacion
        })
    return jsonify(result), 200

@app.route('/cv/<int:cv_id>', methods=['GET'])
def get_one_cv(cv_id):
    """
    Obtiene un CV específico (para posterior edición).
    """
    cv = CV.query.get(cv_id)
    if not cv:
        return jsonify({'message': 'CV no encontrado'}), 404

    return jsonify({
        'id': cv.id,
        'owner_id': cv.owner_id,
        'nombre': cv.nombre,
        'experiencia': cv.experiencia,
        'educacion': cv.educacion
    }), 200

@app.route('/cv/<int:cv_id>', methods=['PUT'])
def update_cv(cv_id):
    data = request.json
    cv = CV.query.get(cv_id)
    if not cv:
        return jsonify({'message': 'CV no encontrado'}), 404

    #Actualizar campos
    nombre = data.get('nombre')
    experiencia = data.get('experiencia')
    educacion = data.get('educacion')

    if nombre:
        cv.nombre = nombre
    if experiencia:
        cv.experiencia = experiencia
    if educacion:
        cv.educacion = educacion

    db.session.commit()
    return jsonify({'message': 'CV actualizado con éxito'}), 200

@app.route('/vacancies', methods=['GET'])
def get_vacancies():
    """
    (Por ahora se simula la lógica)
    """
    #En un caso real se haría un filtrado en base a la info del CV
    dummy_vacancies = [
        {'title': 'Desarrollador Full-Stack', 'description': 'Oportunidad en empresa ABC'},
        {'title': 'Analista de Datos', 'description': 'Oportunidad en empresa XYZ'}
    ]
    return jsonify(dummy_vacancies), 200
###########################################################
#Ejecución 
###########################################################
if __name__ == '__main__':
    app.run(debug=True)
