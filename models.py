from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import validates

db = SQLAlchemy()

class Region(db.Model):
    __tablename__ = 'region'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    
    # Relaciones
    comunas = db.relationship('Comuna', backref='region', lazy=True)
    direcciones = db.relationship('Direccion', backref='region', lazy=True)

class Comuna(db.Model):
    __tablename__ = 'comuna'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=False)
    
    # Relaciones
    direcciones = db.relationship('Direccion', backref='comuna', lazy=True)

class Direccion(db.Model):
    __tablename__ = 'direccion'

    id = db.Column(db.Integer, primary_key=True)
    codigo_postal = db.Column(db.String(10))
    ciudad = db.Column(db.String(50), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    comuna_id = db.Column(db.Integer, db.ForeignKey('comuna.id'))
    
    # Relaciones
    usuarios = db.relationship('Usuario', backref='direccion', lazy=True)


class Usuario(db.Model):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    tipo_usuario = db.Column(db.String(50), nullable=False)
    sexo = db.Column(db.Enum('M', 'F', 'Otro'), nullable=False)
    nombre_completo = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    direccion_id = db.Column(db.Integer, db.ForeignKey('direccion.id'))
    rut = db.Column(db.String(20), unique=True, nullable=False)
    numero_casa = db.Column(db.String(10))
    telefono = db.Column(db.String(15))
    foto = db.Column(db.LargeBinary)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    cuenta = db.relationship('Cuenta', backref='usuario', uselist=False, cascade='all, delete-orphan')
    permisos = db.relationship('Permisos', secondary='usuario_permisos', backref='usuarios')

    @validates('email')
    def validate_email(self, key, value):
        if value and '@' not in value:
            raise ValueError('Formato de email inválido')
        return value

    @validates('rut')
    def validate_rut(self, key, value):
        if value and not self.validar_formato_rut(value):
            raise ValueError('Formato de RUT inválido')
        return value

    @staticmethod
    def validar_formato_rut(rut):
        # Implementar validación de formato RUT chileno
        return True  # Implementar lógica real de validación

class Cuenta(db.Model):
    __tablename__ = 'cuenta'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), unique=True)
    nombre_usuario = db.Column(db.String(50), unique=True, nullable=False)
    contraseña = db.Column(db.String(255), nullable=False)
    estado = db.Column(db.Enum('Activo', 'Inactivo'), nullable=False, default='Activo')
    cargo = db.Column(db.String(50))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acceso = db.Column(db.DateTime)

class Permisos(db.Model):
    __tablename__ = 'permisos'

    id = db.Column(db.Integer, primary_key=True)
    modulo = db.Column(db.String(50), nullable=False)
    accion = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(200))
    
    __table_args__ = (
        db.UniqueConstraint('modulo', 'accion', name='unique_modulo_accion'),
    )

class UsuarioPermisos(db.Model):
    __tablename__ = 'usuario_permisos'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    permiso_id = db.Column(db.Integer, db.ForeignKey('permisos.id', ondelete='CASCADE'), nullable=False)
    fecha_asignacion = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'permiso_id', name='unique_usuario_permiso'),
    )

class Cliente(db.Model):
    __tablename__ = 'cliente'

    id = db.Column(db.Integer, primary_key=True)
    nombre_cliente = db.Column(db.String(100), nullable=False)
    empresa_cliente = db.Column(db.String(100), nullable=False)
    rut = db.Column(db.String(20), unique=True)
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(15))
    email = db.Column(db.String(100))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    ordenes = db.relationship('Orden', back_populates='cliente', passive_deletes=True)

    @validates('email')
    def validate_email(self, key, value):
        if value and '@' not in value:
            raise ValueError('Formato de email inválido')
        return value

class Proveedor(db.Model):
    __tablename__ = 'proveedor'

    id = db.Column(db.Integer, primary_key=True)
    nombre_proveedor = db.Column(db.String(100), nullable=False)
    empresa_proveedor = db.Column(db.String(100), nullable=False)
    rut = db.Column(db.String(20), unique=True)
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(15))
    email = db.Column(db.String(100))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    ordenes = db.relationship('Orden', back_populates='proveedor', passive_deletes=True)

    @validates('email')
    def validate_email(self, key, value):
        if value and '@' not in value:
            raise ValueError('Formato de email inválido')
        return value

class Orden(db.Model):
    __tablename__ = 'orden'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id', ondelete='SET NULL'), nullable=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id', ondelete='SET NULL'), nullable=True)
    valor_orden = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_orden = db.Column(db.Date, nullable=False)
    estado_orden = db.Column(db.Enum('Pendiente', 'Procesada', 'Cancelada', 'Completada'), 
                           nullable=False, 
                           default='Pendiente')
    tipo_orden = db.Column(db.Enum('Entrada', 'Salida'), nullable=False)

    cliente = db.relationship('Cliente', back_populates='ordenes')
    proveedor = db.relationship('Proveedor', back_populates='ordenes')

    @validates('tipo_orden', 'cliente_id', 'proveedor_id')
    def validate_orden(self, key, value):
        if key == 'tipo_orden':
            if value not in ['Entrada', 'Salida']:
                raise ValueError('Tipo de orden inválido')
        elif key == 'cliente_id' and value is not None:
            if self.tipo_orden == 'Entrada':
                raise ValueError('Una orden de entrada no puede tener cliente')
        elif key == 'proveedor_id' and value is not None:
            if self.tipo_orden == 'Salida':
                raise ValueError('Una orden de salida no puede tener proveedor')
        return value

class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    tipo_prenda = db.Column(db.String(50), nullable=False)
    talla = db.Column(db.String(20))
    color = db.Column(db.String(30))
    marca = db.Column(db.String(50))
    valor_compra = db.Column(db.Numeric(10, 2), nullable=False)
    valor_venta = db.Column(db.Numeric(10, 2), nullable=False)
    stock_actual = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=5)
    estado = db.Column(db.Enum('Activo', 'Inactivo', 'Descontinuado'), default='Activo')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    ordenes = db.relationship('OrdenProducto', back_populates='producto', cascade='all, delete-orphan')

    @validates('valor_compra', 'valor_venta')
    def validate_valores(self, key, value):
        if value < 0:
            raise ValueError(f'El {key} no puede ser negativo')
        return value

    @validates('stock_actual', 'stock_minimo')
    def validate_stock(self, key, value):
        if value < 0:
            raise ValueError(f'El {key} no puede ser negativo')
        return value

class OrdenProducto(db.Model):
    __tablename__ = 'orden_producto'

    id = db.Column(db.Integer, primary_key=True)
    orden_id = db.Column(db.Integer, db.ForeignKey('orden.id', ondelete='CASCADE'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id', ondelete='CASCADE'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Relaciones
    orden = db.relationship('Orden', backref=db.backref('orden_productos', cascade='all, delete-orphan'))
    producto = db.relationship('Producto', back_populates='ordenes')

    @validates('cantidad')
    def validate_cantidad(self, key, value):
        if value <= 0:
            raise ValueError('La cantidad debe ser mayor a 0')
        return value

    @validates('precio_unitario')
    def validate_precio(self, key, value):
        if value < 0:
            raise ValueError('El precio unitario no puede ser negativo')
        return value

def init_app(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()