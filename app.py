from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config
from controllers.empleados_controller import empleados_bp
from controllers.home_controller import home_bp
from controllers.interlocutor_controller import interlocutor_bp
from controllers.login_controller import login_dp
from controllers.inventario_controller import inventario_bp
from models import db

# Inicialización de la app
app = Flask(__name__)
app.config.from_object(Config)

# Habilitar CORS
CORS(app)

# Inicializar la base de datos con la app
db.init_app(app)

# Registrar Blueprints
app.register_blueprint(empleados_bp, url_prefix='/empleados')
app.register_blueprint(home_bp, url_prefix='/home')
app.register_blueprint(login_dp)
app.register_blueprint(interlocutor_bp)
app.register_blueprint(inventario_bp)

# Rutas base
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/configuracion')
def configuracion():
    return render_template('configuracion.html')

@app.route('/empleados')
def empleados():
    return render_template('empleados.html')

@app.route('/informes')
def informes():
    return render_template('informe.html')

@app.route('/interlocutor')
def interlocutor():
    return render_template('interlocutor.html')

@app.route('/interlocutor/detalle')
def interlocutor_detalle():
    return render_template('interlocutor-detalle.html')

@app.route('/inventario')
def inventario():
    return render_template('inventario.html')

@app.route('/inventario/detalle')
def inventario_detalle():
    return render_template('inventario-detalle.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crear tablas si no existen
    app.run(debug=True, port=5000)