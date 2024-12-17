from flask import Blueprint, Flask, request, jsonify, session
from models import db, Cuenta
from flask_cors import CORS
import bcrypt
import logging
from sqlalchemy.orm import joinedload
from functools import wraps
from datetime import datetime, timedelta
import jwt

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear el Blueprint para login
login_dp = Blueprint('login', __name__)

# Configuración
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'Mypassword',
    'database': 'gushi'
}

# Clave secreta para JWT (deberías moverla a variables de entorno)
SECRET_KEY = 'tu_clave_secreta_muy_segura'

def generate_token(user_id):
    """Genera un token JWT"""
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=1),
            'iat': datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            SECRET_KEY,
            algorithm='HS256'
        )
    except Exception as e:
        logger.error(f"Error generando token: {e}")
        raise

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'mensaje': 'Token faltante'}), 401
        try:
            # Remover el prefijo 'Bearer ' si existe
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            # Puedes agregar el ID del usuario al request para usarlo en la función
            request.user_id = data['sub']
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'mensaje': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'mensaje': 'Token inválido'}), 401
    return decorated

@login_dp.route('/login_autenticacion', methods=['POST'])
def login_consulta():
    try:
        data = request.get_json()
        logger.info(f"Datos recibidos: {data}")

        nombre_usuario = data.get('nombre_usuario', '').strip()
        contraseña = data.get('contraseña', '').strip()

        # Añadir logs para debugging
        print("Nombre usuario recibido:", nombre_usuario)
        print("Contraseña recibida:", contraseña)

        cuenta = Cuenta.query.filter_by(nombre_usuario=nombre_usuario).first()
        
        if not cuenta:
            print("Cuenta no encontrada")
            return jsonify({"error": "Usuario o contraseña incorrectos"}), 401
        
        print("Contraseña almacenada en BD:", cuenta.contraseña)
        
        # Verificación de contraseña
        try:
            # Añadir logs para ver los valores
            print("Contraseña a verificar:", contraseña.encode('utf-8'))
            print("Hash almacenado:", cuenta.contraseña.encode('utf-8'))
            
            login_exitoso = bcrypt.checkpw(
                contraseña.encode('utf-8'),
                cuenta.contraseña.encode('utf-8')
            )
            print("Resultado de verificación:", login_exitoso)
            
        except Exception as e:
            print("Error en verificación:", str(e))
            return jsonify({"error": f"Error en verificación: {str(e)}"}), 500

        if not login_exitoso:
            return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

        # Actualizar último acceso
        cuenta.ultimo_acceso = datetime.utcnow()
        db.session.commit()

        # Obtener datos del usuario
        usuario = cuenta.usuario
        
        return jsonify({
            "mensaje": "Login exitoso",
            "id_usuario": cuenta.usuario_id,
            "cargo": cuenta.cargo or "",
            "estado": cuenta.estado,
            "nombre_completo": usuario.nombre_completo,
            "tipo_usuario": usuario.tipo_usuario,
            "rut": usuario.rut,
            "token": generate_token(cuenta.usuario_id)
        }), 200

    except Exception as e:
        logger.error(f"Error general: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Error en el servidor"}), 500


@login_dp.route('/verificar_token', methods=['GET'])
@login_required
def verificar_token():
    """Endpoint para verificar si el token es válido"""
    return jsonify({
        'mensaje': 'Token válido',
        'user_id': request.user_id
    }), 200

@login_dp.route('/recuperar_password', methods=['POST'])
def recuperar_password():
    try:
        data = request.get_json()
        email = data.get('email', '').strip()

        if not email:
            return jsonify({"error": "Email es requerido"}), 400

        # Buscar usuario por email
        cuenta = Cuenta.query.join(Cuenta.usuario).filter_by(email=email).first()
        
        if not cuenta:
            logger.warning(f"Email no encontrado para recuperación de contraseña: {email}")
            return jsonify({"error": "No se encontró una cuenta asociada a este email"}), 404

        # Aquí deberías implementar la lógica de envío de email
        # Por ahora solo retornamos un mensaje de éxito
        return jsonify({
            "mensaje": "Se han enviado las instrucciones de recuperación a tu email"
        }), 200

    except Exception as e:
        logger.error(f"Error en recuperación de contraseña: {str(e)}")
        return jsonify({"error": "Error en el servidor"}), 500

# Función para cerrar sesión (opcional, ya que con JWT el cierre de sesión se maneja del lado del cliente)
@login_dp.route('/logout', methods=['POST'])
@login_required
def logout():
    return jsonify({"mensaje": "Sesión cerrada exitosamente"}), 200

# Inicialización de la aplicación
def init_app(app):
    CORS(app, supports_credentials=True)
    app.register_blueprint(login_dp)

# Si necesitas ejecutar el archivo directamente para pruebas
if __name__ == '__main__':
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    init_app(app)
    
    app.run(debug=True)