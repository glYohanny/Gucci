from flask import Blueprint, render_template, request, jsonify, current_app
from models import Direccion, Usuario, db
from services.user_management_service import UserManagementService
import mysql.connector
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

empleados_bp = Blueprint('empleados', __name__)

def get_db_connection():
    logger.info("Intentando establecer conexión con la base de datos...")
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="Mypassword",
            database="gushi"
        )
        logger.info("Conexión exitosa con la base de datos")
        return connection
    except Exception as e:
        logger.error(f"Error al conectar con la base de datos: {str(e)}")
        raise

@empleados_bp.route('/')
def index():
    try:
        return render_template('empleados.html')
    except Exception as e:
        logger.error(f"Error al renderizar la página: {str(e)}")
        return jsonify({"error": str(e)}), 500

@empleados_bp.route('/tabla_empleados')
def tabla_empleados():
    logger.info("Iniciando consulta de tabla_empleados")
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = '''
            SELECT 
                u.id AS 'ID',
                u.nombre_completo AS 'Nombre_Completo',
                u.rut AS 'RUT',
                u.sexo AS 'Sexo',
                u.telefono AS 'Teléfono',
                u.email AS 'email',
                u.tipo_usuario AS 'Tipo_Usuario',
                c.estado AS 'Estado'
            FROM usuario u
            LEFT JOIN cuenta c ON u.id = c.usuario_id
        '''
        logger.info(f"Ejecutando query: {query}")
        
        cursor.execute(query)
        empleados = cursor.fetchall()
        logger.info(f"Datos obtenidos: {len(empleados)} empleados")
        
        # Formatear RUT
        for empleado in empleados:
            rut = empleado['RUT']
            if rut and len(rut) > 1:
                empleado['RUT'] = f"{rut[:-1]}-{rut[-1]}"
        
        return jsonify(empleados)
    
    except Exception as e:
        logger.error(f"Error en tabla_empleados: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
    finally:
        if 'conn' in locals():
            conn.close()
            logger.info("Conexión cerrada")

@empleados_bp.route('/regiones')
def get_regiones():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id, nombre FROM region ORDER BY nombre')
        regiones = cursor.fetchall()
        logger.info(f"Regiones obtenidas: {len(regiones)}")
        return jsonify(regiones)
    except Exception as e:
        logger.error(f"Error obteniendo regiones: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@empleados_bp.route('/comunas/<int:region_id>')
def get_comunas(region_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id, nombre FROM comuna WHERE region_id = %s ORDER BY nombre', (region_id,))
        comunas = cursor.fetchall()
        logger.info(f"Comunas obtenidas para región {region_id}: {len(comunas)}")
        return jsonify(comunas)
    except Exception as e:
        logger.error(f"Error obteniendo comunas: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@empleados_bp.route('/guardar', methods=['POST'])
def guardar_empleado():
    logger.info("Iniciando proceso de guardar empleado")
    try:
        data = request.get_json()
        logger.info(f"Datos recibidos: {data}")
        
        # Validar campos requeridos
        required_fields = [
            'tipo_usuario', 'sexo', 'nombre_completo', 'email', 
            'fecha_nacimiento', 'rut', 'nombre_usuario', 'contrasena'
        ]
        
        for field in required_fields:
            if field not in data or not data[field]:
                logger.error(f"Campo requerido faltante: {field}")
                return jsonify({
                    "success": False,
                    "error": f"El campo {field} es obligatorio"
                }), 400

        # Estructurar datos
        user_data = {
            'tipo_usuario': data['tipo_usuario'],
            'sexo': data['sexo'],
            'nombre_completo': data['nombre_completo'],
            'email': data['email'],
            'fecha_nacimiento': data['fecha_nacimiento'],
            'rut': data['rut'],
            'telefono': data.get('telefono'),
            'numero_casa': data.get('numero_casa'),
            'direccion': data.get('direccion')
        }
        
        account_data = {
            'nombre_usuario': data['nombre_usuario'],
            'contrasena': data['contrasena'],
            'estado': data.get('estado', 'Activo'),
            'cargo': data.get('cargo', '')
        }
        
        permissions_data = data.get('permisos', {})
        
        logger.info("Datos estructurados correctamente")
        
        # Llamar al servicio
        result = UserManagementService.create_user_with_account_and_permissions(
            user_data,
            account_data,
            permissions_data
        )
        
        logger.info("Proceso completado exitosamente")
        return result
        
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@empleados_bp.route('/eliminar/<int:empleado_id>', methods=['DELETE'])
def eliminar_empleado(empleado_id):
    logger.info(f"Iniciando eliminación de empleado ID: {empleado_id}")
    try:
        empleado = Usuario.query.get_or_404(empleado_id)
        db.session.delete(empleado)
        db.session.commit()
        logger.info(f"Empleado {empleado_id} eliminado exitosamente")
        return jsonify({"success": True, "message": "Empleado eliminado correctamente"})
    except Exception as e:
        logger.error(f"Error eliminando empleado: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    
#editar empleados

@empleados_bp.route('/obtener/<int:empleado_id>', methods=['GET'])
def obtener_empleado(empleado_id):
    logger.info(f"Obteniendo datos del empleado ID: {empleado_id}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = '''
            SELECT 
                u.*,
                c.nombre_usuario,
                c.estado,
                c.cargo,
                d.ciudad,
                d.codigo_postal,
                d.region_id,
                d.comuna_id
            FROM usuario u
            LEFT JOIN cuenta c ON u.id = c.usuario_id
            LEFT JOIN direccion d ON u.direccion_id = d.id
            WHERE u.id = %s
        '''
        
        cursor.execute(query, (empleado_id,))
        empleado = cursor.fetchone()
        
        if not empleado:
            return jsonify({"success": False, "error": "Empleado no encontrado"}), 404

        return jsonify({
            "success": True,
            "data": empleado
        })

    except Exception as e:
        logger.error(f"Error obteniendo empleado: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()
            
@empleados_bp.route('/validar-region-comuna', methods=['POST'])
def validar_region_comuna():
    logger.info("Iniciando validación de relación región-comuna")
    try:
        data = request.get_json()
        region_id = data.get('region_id')
        comuna_id = data.get('comuna_id')
        
        if not region_id or not comuna_id:
            return jsonify({
                'success': False,
                'error': 'Se requieren region_id y comuna_id'
            }), 400
            
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar si la comuna pertenece a la región
        cursor.execute('''
            SELECT COUNT(*) as count 
            FROM comuna 
            WHERE id = %s AND region_id = %s
        ''', (comuna_id, region_id))
        
        result = cursor.fetchone()
        
        if result['count'] == 0:
            return jsonify({
                'success': False,
                'error': 'La comuna no pertenece a la región seleccionada'
            }), 400
            
        return jsonify({
            'success': True,
            'message': 'Validación exitosa'
        })
        
    except Exception as e:
        logger.error(f"Error en validación región-comuna: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if 'conn' in locals():
            conn.close()        
            
@empleados_bp.route('/actualizar/<int:empleado_id>', methods=['PUT'])
def actualizar_empleado(empleado_id):
    logger.info(f"Actualizando empleado ID: {empleado_id}")
    try:
        data = request.get_json()
        usuario = Usuario.query.get_or_404(empleado_id)
        
        # Actualizar datos básicos
        for campo in ['nombre_completo', 'email', 'telefono', 'tipo_usuario', 'numero_casa', 'sexo']:
            if campo in data:
                setattr(usuario, campo, data[campo])

        # Actualizar dirección si cambió
        if 'direccion' in data and data['direccion']:
            if usuario.direccion_id:
                direccion = Direccion.query.get(usuario.direccion_id)
            else:
                direccion = Direccion()
                db.session.add(direccion)
                usuario.direccion = direccion

            for campo in ['ciudad', 'codigo_postal', 'region_id', 'comuna_id']:
                if campo in data['direccion']:
                    setattr(direccion, campo, data['direccion'][campo])

        db.session.commit()
        logger.info(f"Empleado {empleado_id} actualizado exitosamente")
        return jsonify({"success": True, "message": "Empleado actualizado correctamente"})

    except Exception as e:
        logger.error(f"Error actualizando empleado: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500