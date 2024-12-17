from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from models import db, Producto, Orden, OrdenProducto
from datetime import datetime
import logging
from sqlalchemy import or_, and_, text, func
from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

inventario_bp = Blueprint('inventario', __name__)

# Rutas para renderizar templates
@inventario_bp.route('/inventario')
def inventario():
    return render_template('inventario.html')

@inventario_bp.route('/inventario/detalle')
def inventario_detalle():
    producto_id = request.args.get('id')
    if not producto_id:
        return redirect(url_for('inventario.inventario'))
    return render_template('inventario-detalle.html')

# Rutas API
@inventario_bp.route('/api/inventario/lista', methods=['GET'])
def get_lista():
    try:
        # Aplicar filtros si existen
        query = Producto.query

        # Filtrar por estado si se especifica
        estado = request.args.get('estado')
        if estado:
            query = query.filter(Producto.estado == estado)

        # Ordenar por columna si se especifica
        sort_by = request.args.get('sort_by', 'id')
        direction = request.args.get('direction', 'asc')
        
        if hasattr(Producto, sort_by):
            order_column = getattr(Producto, sort_by)
            if direction == 'desc':
                order_column = order_column.desc()
            query = query.order_by(order_column)

        productos = query.all()
        
        return jsonify({
            'productos': [{
                'id': p.id,
                'codigo': p.codigo,
                'nombre': p.nombre,
                'tipo_prenda': p.tipo_prenda,
                'stock_actual': p.stock_actual,
                'estado': p.estado
            } for p in productos]
        })
    except Exception as e:
        logger.error(f"Error obteniendo lista de productos: {str(e)}")
        return jsonify({"error": str(e)}), 500

@inventario_bp.route('/api/inventario/producto/<int:producto_id>')
def get_producto_detail(producto_id):
    try:
        producto = Producto.query.get_or_404(producto_id)
        
        # Obtener órdenes relacionadas
        ordenes_relacionadas = db.session.query(
            Orden.id,
            Orden.fecha_orden,
            Orden.tipo_orden,
            Orden.estado_orden,
            OrdenProducto.cantidad,
            OrdenProducto.precio_unitario
        ).join(
            OrdenProducto
        ).filter(
            OrdenProducto.producto_id == producto_id
        ).order_by(Orden.fecha_orden.desc()).limit(10).all()
        
        return jsonify({
            'info_producto': {
                'id': producto.id,
                'codigo': producto.codigo,
                'nombre': producto.nombre,
                'descripcion': producto.descripcion,
                'tipo_prenda': producto.tipo_prenda,
                'talla': producto.talla,
                'color': producto.color,
                'marca': producto.marca,
                'valor_compra': float(producto.valor_compra),
                'valor_venta': float(producto.valor_venta),
                'stock_actual': producto.stock_actual,
                'stock_minimo': producto.stock_minimo,
                'estado': producto.estado,
                'fecha_creacion': producto.fecha_creacion.strftime('%Y-%m-%d'),
                'fecha_actualizacion': producto.fecha_actualizacion.strftime('%Y-%m-%d')
            },
            'estadisticas': {
                'total_ordenes': len(ordenes_relacionadas),
                'ultima_actualizacion': producto.fecha_actualizacion.strftime('%Y-%m-%d'),
                'margen': float(((producto.valor_venta - producto.valor_compra) / producto.valor_compra * 100))
            },
            'ordenes': [{
                'id': orden.id,
                'fecha': orden.fecha_orden.strftime('%Y-%m-%d'),
                'tipo': orden.tipo_orden,
                'estado': orden.estado_orden,
                'cantidad': orden.cantidad,
                'precio_unitario': float(orden.precio_unitario)
            } for orden in ordenes_relacionadas]
        })
    except Exception as e:
        logger.error(f"Error obteniendo detalles del producto {producto_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@inventario_bp.route('/api/inventario/producto', methods=['POST'])
def create_producto():
    try:
        data = request.get_json()
        
        # Verificar si ya existe un producto con el mismo código
        if Producto.query.filter_by(codigo=data['codigo']).first():
            return jsonify({
                "success": False,
                "error": "Ya existe un producto con este código"
            }), 400
        
        nuevo_producto = Producto(
            codigo=data['codigo'],
            nombre=data['nombre'],
            descripcion=data.get('descripcion'),
            tipo_prenda=data['tipo_prenda'],
            talla=data.get('talla'),
            color=data.get('color'),
            marca=data.get('marca'),
            valor_compra=data['valor_compra'],
            valor_venta=data['valor_venta'],
            stock_actual=data.get('stock_actual', 0),
            stock_minimo=data.get('stock_minimo', 5),
            estado=data.get('estado', 'Activo')
        )
        
        db.session.add(nuevo_producto)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Producto creado exitosamente",
            "id": nuevo_producto.id
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creando producto: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@inventario_bp.route('/api/inventario/producto/<int:producto_id>', methods=['PUT', 'DELETE'])
def manage_producto(producto_id):
    try:
        producto = Producto.query.get_or_404(producto_id)
        
        if request.method == 'PUT':
            data = request.get_json()
            
            # Actualizar campos
            for campo in ['nombre', 'descripcion', 'tipo_prenda', 'talla', 
                         'color', 'marca', 'valor_compra', 'valor_venta', 
                         'stock_minimo', 'estado']:
                if campo in data:
                    setattr(producto, campo, data[campo])
            
            producto.fecha_actualizacion = datetime.utcnow()
            
            db.session.commit()
            return jsonify({
                "success": True,
                "message": "Producto actualizado exitosamente"
            })
            
        elif request.method == 'DELETE':
            # Verificar si tiene órdenes asociadas
            if producto.ordenes:
                return jsonify({
                    "success": False,
                    "error": "No se puede eliminar el producto porque tiene órdenes asociadas"
                }), 400
                
            db.session.delete(producto)
            db.session.commit()
            return jsonify({
                "success": True,
                "message": "Producto eliminado exitosamente"
            })
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error manejando producto {producto_id}: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@inventario_bp.route('/api/inventario/buscar')
def buscar_productos():
    try:
        termino = request.args.get('q', '')
        
        productos = Producto.query.filter(
            or_(
                Producto.nombre.ilike(f'%{termino}%'),
                Producto.codigo.ilike(f'%{termino}%'),
                Producto.tipo_prenda.ilike(f'%{termino}%')
            )
        ).order_by(Producto.nombre).all()
        
        return jsonify([{
            'id': p.id,
            'codigo': p.codigo,
            'nombre': p.nombre,
            'tipo_prenda': p.tipo_prenda,
            'stock_actual': p.stock_actual,
            'estado': p.estado
        } for p in productos])
        
    except Exception as e:
        logger.error(f"Error en la búsqueda de productos: {str(e)}")
        return jsonify({"error": str(e)}), 500