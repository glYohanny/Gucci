from flask import Blueprint, jsonify, request
from models import db, Cliente, Proveedor, Orden
from datetime import datetime
import logging
from sqlalchemy import or_, and_, text, func
from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal

# Configuración del logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

interlocutor_bp = Blueprint('interlocutor', __name__, url_prefix='/api')

@interlocutor_bp.route('/interlocutor/lista')
def get_lista():
    try:
        # Obtener todos los clientes y proveedores
        clientes = Cliente.query.all()
        proveedores = Proveedor.query.all()
        
        # Preparar respuesta
        return jsonify({
            'clientes': [{
                'id': c.id,
                'nombre_cliente': c.nombre_cliente,
                'empresa_cliente': c.empresa_cliente,
                'email': c.email,
                'telefono': c.telefono
            } for c in clientes],
            'proveedores': [{
                'id': p.id,
                'nombre_proveedor': p.nombre_proveedor,
                'empresa_proveedor': p.empresa_proveedor,
                'email': p.email,
                'telefono': p.telefono
            } for p in proveedores]
        })
    except Exception as e:
        logger.error(f"Error obteniendo lista de interlocutores: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@interlocutor_bp.route('/cliente/<int:cliente_id>')
def get_cliente_detail(cliente_id):
    try:
        cliente = Cliente.query.get_or_404(cliente_id)
        
        # Obtener todas las órdenes del cliente
        ordenes = db.session.query(
            Orden.id,
            Orden.valor_orden,
            Orden.fecha_orden,
            Orden.estado_orden,
            Orden.tipo_orden
        ).filter(Orden.cliente_id == cliente_id).all()
        
        # Calcular estadísticas
        total_ordenes = len(ordenes)
        valor_total = sum(float(orden.valor_orden) for orden in ordenes) if ordenes else 0
        ultima_orden = max((orden.fecha_orden for orden in ordenes), default=None)
        
        # Preparar respuesta
        cliente_data = {
            'info_interlocutor': {
                'id': cliente.id,
                'nombre': cliente.nombre_cliente,
                'empresa': cliente.empresa_cliente,
                'tipo': 'Cliente',
                'email': cliente.email,
                'telefono': cliente.telefono,
                'direccion': cliente.direccion
            },
            'estadisticas': {
                'total_ordenes': total_ordenes,
                'valor_total': valor_total,
                'ultima_orden': ultima_orden.strftime('%Y-%m-%d') if ultima_orden else None
            },
            'ordenes': [{
                'id': orden.id,
                'tipo': orden.tipo_orden,
                'valor': float(orden.valor_orden),
                'fecha': orden.fecha_orden.strftime('%Y-%m-%d'),
                'estado': orden.estado_orden
            } for orden in ordenes]
        }
        
        return jsonify(cliente_data)
        
    except Exception as e:
        logger.error(f"Error obteniendo detalles del cliente {cliente_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@interlocutor_bp.route('/proveedor/<int:proveedor_id>')
def get_proveedor_detail(proveedor_id):
    try:
        proveedor = Proveedor.query.get_or_404(proveedor_id)
        
        # Obtener todas las órdenes del proveedor
        ordenes = db.session.query(
            Orden.id,
            Orden.valor_orden,
            Orden.fecha_orden,
            Orden.estado_orden,
            Orden.tipo_orden
        ).filter(Orden.proveedor_id == proveedor_id).all()
        
        # Calcular estadísticas
        total_ordenes = len(ordenes)
        valor_total = sum(float(orden.valor_orden) for orden in ordenes) if ordenes else 0
        ultima_orden = max((orden.fecha_orden for orden in ordenes), default=None)
        
        # Preparar respuesta
        proveedor_data = {
            'info_interlocutor': {
                'id': proveedor.id,
                'nombre': proveedor.nombre_proveedor,
                'empresa': proveedor.empresa_proveedor,
                'tipo': 'Proveedor',
                'email': proveedor.email,
                'telefono': proveedor.telefono,
                'direccion': proveedor.direccion
            },
            'estadisticas': {
                'total_ordenes': total_ordenes,
                'valor_total': valor_total,
                'ultima_orden': ultima_orden.strftime('%Y-%m-%d') if ultima_orden else None
            },
            'ordenes': [{
                'id': orden.id,
                'tipo': orden.tipo_orden,
                'valor': float(orden.valor_orden),
                'fecha': orden.fecha_orden.strftime('%Y-%m-%d'),
                'estado': orden.estado_orden
            } for orden in ordenes]
        }
        
        return jsonify(proveedor_data)
        
    except Exception as e:
        logger.error(f"Error obteniendo detalles del proveedor {proveedor_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@interlocutor_bp.route('/cliente/ordenes/<int:cliente_id>')
def get_cliente_ordenes(cliente_id):
    try:
        # Verificar que el cliente existe
        cliente = Cliente.query.get_or_404(cliente_id)
        
        # Obtener órdenes con paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        ordenes = Orden.query.filter_by(cliente_id=cliente_id)\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        # Preparar respuesta
        ordenes_data = {
            'ordenes': [{
                'id': orden.id,
                'tipo': orden.tipo_orden,
                'valor': float(orden.valor_orden),
                'fecha': orden.fecha_orden.strftime('%Y-%m-%d'),
                'estado': orden.estado_orden
            } for orden in ordenes.items],
            'total_pages': ordenes.pages,
            'current_page': page,
            'total_items': ordenes.total
        }
        
        return jsonify(ordenes_data)
        
    except Exception as e:
        logger.error(f"Error obteniendo órdenes del cliente {cliente_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@interlocutor_bp.route('/proveedor/ordenes/<int:proveedor_id>')
def get_proveedor_ordenes(proveedor_id):
    try:
        # Verificar que el proveedor existe
        proveedor = Proveedor.query.get_or_404(proveedor_id)
        
        # Obtener órdenes con paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        ordenes = Orden.query.filter_by(proveedor_id=proveedor_id)\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        # Preparar respuesta
        ordenes_data = {
            'ordenes': [{
                'id': orden.id,
                'tipo': orden.tipo_orden,
                'valor': float(orden.valor_orden),
                'fecha': orden.fecha_orden.strftime('%Y-%m-%d'),
                'estado': orden.estado_orden
            } for orden in ordenes.items],
            'total_pages': ordenes.pages,
            'current_page': page,
            'total_items': ordenes.total
        }
        
        return jsonify(ordenes_data)
        
    except Exception as e:
        logger.error(f"Error obteniendo órdenes del proveedor {proveedor_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@interlocutor_bp.route('/buscar')
def buscar_interlocutores():
    try:
        termino = request.args.get('q', '')
        tipo = request.args.get('tipo', 'todos')  # 'cliente', 'proveedor' o 'todos'
        
        resultados = []
        
        if tipo in ['todos', 'cliente']:
            clientes = Cliente.query.filter(
                or_(
                    Cliente.nombre_cliente.ilike(f'%{termino}%'),
                    Cliente.empresa_cliente.ilike(f'%{termino}%')
                )
            ).all()
            
            resultados.extend([{
                'id': cliente.id,
                'nombre': cliente.nombre_cliente,
                'empresa': cliente.empresa_cliente,
                'tipo': 'Cliente'
            } for cliente in clientes])
            
        if tipo in ['todos', 'proveedor']:
            proveedores = Proveedor.query.filter(
                or_(
                    Proveedor.nombre_proveedor.ilike(f'%{termino}%'),
                    Proveedor.empresa_proveedor.ilike(f'%{termino}%')
                )
            ).all()
            
            resultados.extend([{
                'id': proveedor.id,
                'nombre': proveedor.nombre_proveedor,
                'empresa': proveedor.empresa_proveedor,
                'tipo': 'Proveedor'
            } for proveedor in proveedores])
        
        return jsonify(resultados)
        
    except Exception as e:
        logger.error(f"Error en la búsqueda de interlocutores: {str(e)}")
        return jsonify({"error": str(e)}), 500

@interlocutor_bp.route('/estadisticas')
def get_estadisticas():
    try:
        # Estadísticas generales
        total_clientes = Cliente.query.count()
        total_proveedores = Proveedor.query.count()
        
        # Top 5 clientes por valor total de órdenes
        top_clientes = db.session.query(
            Cliente.id,
            Cliente.nombre_cliente,
            Cliente.empresa_cliente,
            func.sum(Orden.valor_orden).label('total_valor')
        ).join(Orden).group_by(Cliente.id)\
         .order_by(func.sum(Orden.valor_orden).desc())\
         .limit(5).all()
        
        # Top 5 proveedores por valor total de órdenes
        top_proveedores = db.session.query(
            Proveedor.id,
            Proveedor.nombre_proveedor,
            Proveedor.empresa_proveedor,
            func.sum(Orden.valor_orden).label('total_valor')
        ).join(Orden).group_by(Proveedor.id)\
         .order_by(func.sum(Orden.valor_orden).desc())\
         .limit(5).all()
        
        return jsonify({
            'totales': {
                'clientes': total_clientes,
                'proveedores': total_proveedores
            },
            'top_clientes': [{
                'id': cliente.id,
                'nombre': cliente.nombre_cliente,
                'empresa': cliente.empresa_cliente,
                'total_valor': float(cliente.total_valor)
            } for cliente in top_clientes],
            'top_proveedores': [{
                'id': proveedor.id,
                'nombre': proveedor.nombre_proveedor,
                'empresa': proveedor.empresa_proveedor,
                'total_valor': float(proveedor.total_valor)
            } for proveedor in top_proveedores]
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
    # Añadir estas rutas nuevas al archivo existente

# Ruta para crear cliente
@interlocutor_bp.route('/interlocutor/cliente', methods=['POST'])
def create_cliente():
    try:
        data = request.get_json()
        nuevo_cliente = Cliente(
            nombre_cliente=data['nombre_cliente'],
            empresa_cliente=data['empresa_cliente'],
            email=data.get('email'),
            telefono=data.get('telefono'),
            direccion=data.get('direccion')
        )
        
        db.session.add(nuevo_cliente)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Cliente creado exitosamente",
            "id": nuevo_cliente.id
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creando cliente: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

# Ruta para crear proveedor
@interlocutor_bp.route('/interlocutor/proveedor', methods=['POST'])
def create_proveedor():
    try:
        data = request.get_json()
        nuevo_proveedor = Proveedor(
            nombre_proveedor=data['nombre_proveedor'],
            empresa_proveedor=data['empresa_proveedor'],
            email=data.get('email'),
            telefono=data.get('telefono'),
            direccion=data.get('direccion')
        )
        
        db.session.add(nuevo_proveedor)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Proveedor creado exitosamente",
            "id": nuevo_proveedor.id
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creando proveedor: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

# Actualizar la ruta GET/PUT/DELETE para cliente
@interlocutor_bp.route('/interlocutor/cliente/<int:cliente_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_cliente(cliente_id):
    try:
        cliente = Cliente.query.get_or_404(cliente_id)
        
        if request.method == 'GET':
            # Obtener órdenes
            ordenes = db.session.query(
                Orden.id,
                Orden.valor_orden,
                Orden.fecha_orden,
                Orden.estado_orden,
                Orden.tipo_orden
            ).filter(Orden.cliente_id == cliente_id).all()
            
            total_ordenes = len(ordenes)
            valor_total = sum(float(orden.valor_orden) for orden in ordenes) if ordenes else 0
            ultima_orden = max((orden.fecha_orden for orden in ordenes), default=None)
            
            return jsonify({
                'info_interlocutor': {
                    'id': cliente.id,
                    'nombre': cliente.nombre_cliente,
                    'empresa': cliente.empresa_cliente,
                    'tipo': 'Cliente',
                    'email': cliente.email,
                    'telefono': cliente.telefono,
                    'direccion': cliente.direccion
                },
                'estadisticas': {
                    'total_ordenes': total_ordenes,
                    'valor_total': valor_total,
                    'ultima_orden': ultima_orden.strftime('%Y-%m-%d') if ultima_orden else None
                },
                'ordenes': [{
                    'id': orden.id,
                    'tipo': orden.tipo_orden,
                    'valor': float(orden.valor_orden),
                    'fecha': orden.fecha_orden.strftime('%Y-%m-%d'),
                    'estado': orden.estado_orden
                } for orden in ordenes]
            })
            
        elif request.method == 'PUT':
            data = request.get_json()
            cliente.nombre_cliente = data.get('nombre', cliente.nombre_cliente)
            cliente.empresa_cliente = data.get('empresa', cliente.empresa_cliente)
            cliente.email = data.get('email', cliente.email)
            cliente.telefono = data.get('telefono', cliente.telefono)
            cliente.direccion = data.get('direccion', cliente.direccion)
            
            db.session.commit()
            return jsonify({"success": True, "message": "Cliente actualizado exitosamente"})
            
        elif request.method == 'DELETE':
            db.session.delete(cliente)
            db.session.commit()
            return jsonify({"success": True, "message": "Cliente eliminado exitosamente"})
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error manejando cliente {cliente_id}: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

# Actualizar la ruta GET/PUT/DELETE para proveedor
@interlocutor_bp.route('/interlocutor/proveedor/<int:proveedor_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_proveedor(proveedor_id):
    try:
        proveedor = Proveedor.query.get_or_404(proveedor_id)
        
        if request.method == 'GET':
            # Obtener órdenes
            ordenes = db.session.query(
                Orden.id,
                Orden.valor_orden,
                Orden.fecha_orden,
                Orden.estado_orden,
                Orden.tipo_orden
            ).filter(Orden.proveedor_id == proveedor_id).all()
            
            total_ordenes = len(ordenes)
            valor_total = sum(float(orden.valor_orden) for orden in ordenes) if ordenes else 0
            ultima_orden = max((orden.fecha_orden for orden in ordenes), default=None)
            
            return jsonify({
                'info_interlocutor': {
                    'id': proveedor.id,
                    'nombre': proveedor.nombre_proveedor,
                    'empresa': proveedor.empresa_proveedor,
                    'tipo': 'Proveedor',
                    'email': proveedor.email,
                    'telefono': proveedor.telefono,
                    'direccion': proveedor.direccion
                },
                'estadisticas': {
                    'total_ordenes': total_ordenes,
                    'valor_total': valor_total,
                    'ultima_orden': ultima_orden.strftime('%Y-%m-%d') if ultima_orden else None
                },
                'ordenes': [{
                    'id': orden.id,
                    'tipo': orden.tipo_orden,
                    'valor': float(orden.valor_orden),
                    'fecha': orden.fecha_orden.strftime('%Y-%m-%d'),
                    'estado': orden.estado_orden
                } for orden in ordenes]
            })
            
        elif request.method == 'PUT':
            data = request.get_json()
            proveedor.nombre_proveedor = data.get('nombre', proveedor.nombre_proveedor)
            proveedor.empresa_proveedor = data.get('empresa', proveedor.empresa_proveedor)
            proveedor.email = data.get('email', proveedor.email)
            proveedor.telefono = data.get('telefono', proveedor.telefono)
            proveedor.direccion = data.get('direccion', proveedor.direccion)
            
            db.session.commit()
            return jsonify({"success": True, "message": "Proveedor actualizado exitosamente"})
            
        elif request.method == 'DELETE':
            db.session.delete(proveedor)
            db.session.commit()
            return jsonify({"success": True, "message": "Proveedor eliminado exitosamente"})
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error manejando proveedor {proveedor_id}: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400
    
    
@interlocutor_bp.route('/interlocutor/cliente/<int:cliente_id>', methods=['DELETE'])
def delete_cliente(cliente_id):
    try:
        cliente = Cliente.query.get_or_404(cliente_id)
        
        # Verificar si el cliente tiene órdenes asociadas
        if cliente.ordenes:
            return jsonify({
                "success": False, 
                "error": "No se puede eliminar el cliente porque tiene órdenes asociadas. Por favor, elimine primero las órdenes."
            }), 400
            
        db.session.delete(cliente)
        db.session.commit()
        return jsonify({"success": True, "message": "Cliente eliminado exitosamente"})
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error eliminando cliente {cliente_id}: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@interlocutor_bp.route('/interlocutor/proveedor/<int:proveedor_id>', methods=['DELETE'])
def delete_proveedor(proveedor_id):
    try:
        proveedor = Proveedor.query.get_or_404(proveedor_id)
        
        # Verificar si el proveedor tiene órdenes asociadas
        if proveedor.ordenes:
            return jsonify({
                "success": False, 
                "error": "No se puede eliminar el proveedor porque tiene órdenes asociadas. Por favor, elimine primero las órdenes."
            }), 400
            
        db.session.delete(proveedor)
        db.session.commit()
        return jsonify({"success": True, "message": "Proveedor eliminado exitosamente"})
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error eliminando proveedor {proveedor_id}: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400