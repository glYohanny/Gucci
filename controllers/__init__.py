# controllers/__init__.py

from .empleados_controller import empleados_bp
from .home_controller import home_bp
from .login_controller import login_dp
from .interlocutor_controller import interlocutor_bp
from .inventario_controller import inventario_bp

# Esto permite importar los blueprints directamente desde el paquete controllers