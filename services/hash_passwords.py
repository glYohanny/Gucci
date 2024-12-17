import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bcrypt
from flask import Flask
import logging
import pymysql
from models import db, Cuenta

class PasswordService:
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    def hash_passwords(self):
        """Hashea todas las contraseñas existentes en la base de datos que no estén hasheadas"""
        try:
            # Obtener todas las cuentas
            cuentas = Cuenta.query.all()
            contador = 0
            
            for cuenta in cuentas:
                # Verificar si la contraseña ya está hasheada
                if not cuenta.contraseña.startswith('$2b$'):
                    # Generar hash de la contraseña
                    hashed = bcrypt.hashpw(cuenta.contraseña.encode('utf-8'), bcrypt.gensalt())
                    cuenta.contraseña = hashed.decode('utf-8')
                    contador += 1
                    print(f"Contraseña hasheada para usuario: {cuenta.nombre_usuario}")
            
            db.session.commit()
            print(f"Proceso de hasheo completado exitosamente. Se hashearon {contador} contraseñas.")
            return True, f"Se hashearon {contador} contraseñas exitosamente"
            
        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()
            return False, str(e)

# Script de ejecución directa
def run_hash_script():
    # Registrar PyMySQL como el controlador de MySQL
    pymysql.install_as_MySQLdb()

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Mypassword@127.0.0.1/gushi'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        password_service = PasswordService()
        success, message = password_service.hash_passwords()
        if not success:
            sys.exit(1)

if __name__ == '__main__':
    run_hash_script()