from flask import Blueprint, jsonify, request
from models import db, Orden, Cliente, Proveedor
from datetime import datetime
import logging
from sqlalchemy import or_, and_, text
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from decimal import Decimal

# Configuración de logging detallada
logging.basicConfig(
    level=logging.DEBUG,  # Cambiado a DEBUG para más detalle
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

home_bp = Blueprint('home', __name__)

@home_bp.route('/debug-db')
def debug_db():
    """Ruta para depuración de la base de datos"""
    try:
        # Verificar conexión
        db.session.execute(text('SELECT 1'))
        logger.info("Conexión a BD verificada")

        # Obtener información de las tablas
        orden_sample = Orden.query.first()
        cliente_sample = Cliente.query.first()
        proveedor_sample = Proveedor.query.first()

        debug_info = {
            'estado_conexion': 'activa',
            'tablas': {
                'ordenes': {
                    'total': Orden.query.count(),
                    'muestra': {
                        'id': orden_sample.id if orden_sample else None,
                        'tipo_orden': orden_sample.tipo_orden if orden_sample else None,
                        'valor_orden': str(orden_sample.valor_orden) if orden_sample else None,
                        'estado': orden_sample.estado_orden if orden_sample else None
                    } if orden_sample else None
                },
                'clientes': {
                    'total': Cliente.query.count(),
                    'muestra': {
                        'id': cliente_sample.id if cliente_sample else None,
                        'nombre': cliente_sample.nombre_cliente if cliente_sample else None
                    } if cliente_sample else None
                },
                'proveedores': {
                    'total': Proveedor.query.count(),
                    'muestra': {
                        'id': proveedor_sample.id if proveedor_sample else None,
                        'nombre': proveedor_sample.nombre_proveedor if proveedor_sample else None
                    } if proveedor_sample else None
                }
            }
        }
        logger.info(f"Información de depuración recopilada: {debug_info}")
        return jsonify(debug_info)
    except Exception as e:
        logger.error(f"Error en debug-db: {str(e)}")
        return jsonify({'error': str(e)}), 500

@home_bp.route('/ordenes')
def get_ordenes():
    try:
        logger.info("Iniciando consulta de órdenes")
        
        try:
            db.session.execute(text('SELECT 1'))
            logger.info("Conexión a la base de datos verificada")
        except SQLAlchemyError as e:
            logger.error(f"Error de conexión a la base de datos: {str(e)}")
            return jsonify({"error": "Error de conexión a la base de datos"}), 500

        try:
            # Consulta para todas las órdenes
            ordenes = db.session.query(
                Orden.id.label('ID'),
                Orden.valor_orden.label('Valor_de_Orden'),
                Orden.fecha_orden.label('Fecha_de_Orden'),
                Orden.estado_orden.label('Estado'),
                Orden.tipo_orden.label('tipo'),
                Cliente.nombre_cliente,
                Cliente.empresa_cliente,
                Proveedor.nombre_proveedor,
                Proveedor.empresa_proveedor
            ).outerjoin(Cliente, Orden.cliente_id == Cliente.id)\
             .outerjoin(Proveedor, Orden.proveedor_id == Proveedor.id)\
             .all()

            logger.info(f"Total de órdenes encontradas: {len(ordenes)}")

            resultado = []
            for orden in ordenes:
                # Determinar el interlocutor y empresa basado en el tipo de orden
                if orden.tipo == 'Entrada':
                    interlocutor = orden.nombre_proveedor or 'Sin proveedor'
                    empresa = orden.empresa_proveedor or 'Sin empresa'
                else:  # Salida
                    interlocutor = orden.nombre_cliente or 'Sin cliente'
                    empresa = orden.empresa_cliente or 'Sin empresa'

                orden_dict = {
                    'ID': orden.ID,
                    'Interlocutor': interlocutor,
                    'Empresa': empresa,
                    'Valor_de_Orden': float(orden.Valor_de_Orden) if orden.Valor_de_Orden else 0,
                    'Fecha_de_Orden': orden.Fecha_de_Orden.strftime('%Y-%m-%d') if orden.Fecha_de_Orden else None,
                    'Estado': orden.Estado,
                    'tipo': orden.tipo
                }
                logger.debug(f"Procesando orden: {orden_dict}")
                resultado.append(orden_dict)

            logger.info(f"Total de órdenes procesadas: {len(resultado)}")
            if resultado:
                logger.debug(f"Muestra del primer resultado: {resultado[0]}")

            return jsonify(resultado)

        except SQLAlchemyError as e:
            logger.error(f"Error en la consulta de órdenes: {str(e)}")
            return jsonify({"error": "Error al consultar las órdenes"}), 500
            
    except Exception as e:
        logger.error(f"Error inesperado obteniendo órdenes: {str(e)}")
        return jsonify({"error": str(e)}), 500

@home_bp.route('/orden', methods=['POST'])
def create_orden():
    try:
        logger.info("Iniciando creación de orden")
        data = request.get_json()
        logger.info(f"Datos recibidos: {data}")

        # Crear la nueva orden solo con los campos existentes
        nueva_orden = Orden(
            tipo_orden=data['tipo_orden'],
            valor_orden=Decimal(str(data['valor_orden'])),
            fecha_orden=datetime.strptime(data['fecha_orden'], '%Y-%m-%d').date(),
            estado_orden=data['estado_orden']
        )

        # Asignar cliente o proveedor según el tipo
        if data['tipo_orden'] == 'Entrada':
            nueva_orden.proveedor_id = data['interlocutor_id']
            nueva_orden.cliente_id = None
        else:
            nueva_orden.cliente_id = data['interlocutor_id']
            nueva_orden.proveedor_id = None

        db.session.add(nueva_orden)
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": "Orden creada exitosamente",
            "id": nueva_orden.id
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error en create_orden: {str(e)}")
        return jsonify({
            "success": False, 
            "error": str(e)
        }), 500

@home_bp.route('/orden/<int:orden_id>', methods=['PUT'])
def update_orden(orden_id):
    try:
        orden = Orden.query.get_or_404(orden_id)
        data = request.get_json()
        logger.info(f"Actualizando orden {orden_id} con datos: {data}")
        
        # Actualizar campos
        orden.tipo_orden = data['tipo_orden']
        orden.valor_orden = Decimal(str(data['valor_orden']))
        orden.fecha_orden = datetime.strptime(data['fecha_orden'], '%Y-%m-%d').date()
        orden.estado_orden = data['estado_orden']
        
        # Actualizar interlocutor
        if data['tipo_orden'] == 'Entrada':
            orden.proveedor_id = data['interlocutor_id']
            orden.cliente_id = None
            logger.info(f"Actualizando a proveedor_id: {data['interlocutor_id']}")
        else:
            orden.cliente_id = data['interlocutor_id']
            orden.proveedor_id = None
            logger.info(f"Actualizando a cliente_id: {data['interlocutor_id']}")
        
        db.session.commit()
        logger.info(f"Orden {orden_id} actualizada exitosamente")
        
        return jsonify({"success": True, "message": "Orden actualizada exitosamente"})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error actualizando orden {orden_id}: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@home_bp.route('/orden/<int:orden_id>', methods=['DELETE'])
def delete_orden(orden_id):
    try:
        orden = Orden.query.get_or_404(orden_id)
        logger.info(f"Eliminando orden {orden_id}")
        
        db.session.delete(orden)
        db.session.commit()
        
        logger.info(f"Orden {orden_id} eliminada exitosamente")
        return jsonify({"success": True, "message": "Orden eliminada exitosamente"})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error eliminando orden {orden_id}: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@home_bp.route('/proveedores')
def get_proveedores():
    try:
        # Verificar la conexión primero
        db.session.execute(text('SELECT 1'))
        logger.info("Conexión verificada para consulta de proveedores")
        
        try:
            # Solo seleccionar los campos que existen
            proveedores = db.session.query(
                Proveedor.id,
                Proveedor.nombre_proveedor,
                Proveedor.empresa_proveedor
            ).order_by(Proveedor.nombre_proveedor).all()
            
            logger.info(f"Consulta de proveedores ejecutada. Total encontrados: {len(proveedores)}")
            
            resultado = [{
                'id': proveedor.id,
                'nombre_proveedor': proveedor.nombre_proveedor,
                'empresa_proveedor': proveedor.empresa_proveedor
            } for proveedor in proveedores]
            
            return jsonify(resultado)
            
        except SQLAlchemyError as e:
            logger.error(f"Error en la consulta de proveedores: {str(e)}")
            return jsonify({"error": f"Error en la consulta: {str(e)}"}), 500
            
    except Exception as e:
        logger.error(f"Error general en get_proveedores: {str(e)}")
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500

@home_bp.route('/clientes')
def get_clientes():
    try:
        # Verificar la conexión primero
        db.session.execute(text('SELECT 1'))
        logger.info("Conexión verificada para consulta de clientes")
        
        try:
            # Solo seleccionar los campos que existen
            clientes = db.session.query(
                Cliente.id,
                Cliente.nombre_cliente,
                Cliente.empresa_cliente
            ).order_by(Cliente.nombre_cliente).all()
            
            logger.info(f"Consulta de clientes ejecutada. Total encontrados: {len(clientes)}")
            
            resultado = [{
                'id': cliente.id,
                'nombre_cliente': cliente.nombre_cliente,
                'empresa_cliente': cliente.empresa_cliente
            } for cliente in clientes]
            
            return jsonify(resultado)
            
        except SQLAlchemyError as e:
            logger.error(f"Error en la consulta de clientes: {str(e)}")
            return jsonify({"error": f"Error en la consulta: {str(e)}"}), 500
            
    except Exception as e:
        logger.error(f"Error general en get_clientes: {str(e)}")
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500
    
@home_bp.route('/orden/<int:orden_id>', methods=['GET'])
def obtener_orden(orden_id):
    try:
        orden = Orden.query.get_or_404(orden_id)
        
        # Determinar el interlocutor y su ID según el tipo de orden
        if orden.tipo_orden == 'Entrada':
            interlocutor_id = orden.proveedor_id
        else:
            interlocutor_id = orden.cliente_id
        
        return jsonify({
            'id': orden.id,
            'tipo_orden': orden.tipo_orden,
            'interlocutor_id': interlocutor_id,
            'valor_orden': str(orden.valor_orden),
            'fecha_orden': orden.fecha_orden.strftime('%Y-%m-%d'),
            'estado_orden': orden.estado_orden
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
@home_bp.route('/orden/<int:orden_id>', methods=['PUT'])
def actualizar_orden(orden_id):
    try:
        data = request.get_json()
        
        orden = Orden.query.get_or_404(orden_id)

        # Validamos que existan los datos necesarios
        required_fields = ['tipo_orden', 'interlocutor_id', 'valor_orden', 'fecha_orden', 'estado_orden']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'El campo {field} es requerido'}), 400

        # Validamos el tipo de orden
        if data['tipo_orden'] not in ['Entrada', 'Salida']:
            return jsonify({'error': 'Tipo de orden inválido'}), 400

        # Validamos el estado
        if data['estado_orden'] not in ['Pendiente', 'Procesada', 'Cancelada', 'Completada']:
            return jsonify({'error': 'Estado de orden inválido'}), 400

        # Verificamos que el interlocutor exista según el tipo de orden
        if data['tipo_orden'] == 'Entrada':
            proveedor = Proveedor.query.get(data['interlocutor_id'])
            if not proveedor:
                return jsonify({'error': 'Proveedor no encontrado'}), 400
            orden.cliente_id = None
            orden.proveedor_id = data['interlocutor_id']
        else:
            cliente = Cliente.query.get(data['interlocutor_id'])
            if not cliente:
                return jsonify({'error': 'Cliente no encontrado'}), 400
            orden.proveedor_id = None
            orden.cliente_id = data['interlocutor_id']

        # Actualizar los campos de la orden
        orden.tipo_orden = data['tipo_orden']
        try:
            orden.valor_orden = float(data['valor_orden'])
        except ValueError:
            return jsonify({'error': 'El valor de la orden debe ser un número válido'}), 400
            
        try:
            orden.fecha_orden = datetime.strptime(data['fecha_orden'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
            
        orden.estado_orden = data['estado_orden']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Orden actualizada correctamente'
        })
        
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Error de integridad al manejar orden {orden_id}: {str(e)}")
        return jsonify({'error': 'Error de integridad en los datos'}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error SQL al manejar orden {orden_id}: {str(e)}")
        return jsonify({'error': 'Error en la base de datos'}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error inesperado: {str(e)}")
        return jsonify({'error': 'Error inesperado'}), 500