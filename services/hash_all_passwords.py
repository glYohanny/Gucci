from flask import Flask
from models import db
from services.hash_passwords import PasswordService
import pymysql

def main():
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
            print(f"Error: {message}")
            return 1
        print(message)
        return 0

if __name__ == '__main__':
    exit(main())