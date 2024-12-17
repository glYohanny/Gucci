from flask import jsonify
from models import db, Usuario, Cuenta, Permisos, UsuarioPermisos, Direccion
from werkzeug.security import generate_password_hash
from datetime import datetime

class UserManagementService:
    @staticmethod
    def create_user_with_account_and_permissions(user_data, account_data, permissions_data):
        try:
            # 1. Crear dirección si se proporcionó
            direccion_id = None
            if 'direccion' in user_data and user_data['direccion']:
                nueva_direccion = Direccion(
                    codigo_postal=user_data['direccion'].get('codigo_postal'),
                    ciudad=user_data['direccion'].get('ciudad'),
                    region_id=user_data['direccion'].get('region_id'),
                    comuna_id=user_data['direccion'].get('comuna_id')
                )
                db.session.add(nueva_direccion)
                db.session.flush()
                direccion_id = nueva_direccion.id

            # 2. Crear el usuario
            nuevo_usuario = Usuario(
                tipo_usuario=user_data['tipo_usuario'],
                sexo=user_data['sexo'],
                nombre_completo=user_data['nombre_completo'],
                email=user_data['email'],
                fecha_nacimiento=datetime.strptime(user_data['fecha_nacimiento'], '%Y-%m-%d'),
                direccion_id=direccion_id,
                rut=user_data['rut'],
                telefono=user_data.get('telefono'),
                numero_casa=user_data.get('numero_casa')
            )
            db.session.add(nuevo_usuario)
            db.session.flush()

            # 3. Crear la cuenta asociada
            nueva_cuenta = Cuenta(
                usuario_id=nuevo_usuario.id,
                nombre_usuario=account_data['nombre_usuario'],
                contraseña=generate_password_hash(account_data['contrasena']),
                estado=account_data['estado'],
                cargo=account_data['cargo']
            )
            db.session.add(nueva_cuenta)

            # 4. Asignar permisos
            for modulo, acciones in permissions_data.items():
                for accion, valor in acciones.items():
                    if valor:
                        permiso = Permisos.query.filter_by(
                            modulo=modulo,
                            accion=accion
                        ).first()
                        
                        if not permiso:
                            permiso = Permisos(
                                modulo=modulo,
                                accion=accion,
                                descripcion=f"Permiso para {accion} en {modulo}"
                            )
                            db.session.add(permiso)
                            db.session.flush()

                        usuario_permiso = UsuarioPermisos(
                            usuario_id=nuevo_usuario.id,
                            permiso_id=permiso.id
                        )
                        db.session.add(usuario_permiso)

            db.session.commit()
            return jsonify({
                "success": True,
                "message": "Usuario creado exitosamente",
                "user_id": nuevo_usuario.id
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500