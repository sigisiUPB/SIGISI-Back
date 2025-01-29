from models.users import User
from flask import jsonify
from datetime import datetime, timedelta
import pytz  # Para manejar zonas horarias
import hashlib
import jwt
import os
from db.connection import db  # Asegúrate de importar la conexión de la base de datos

def verify_password(stored_password, provided_password):
    # Verifica si la contraseña proporcionada coincide con el hash almacenado
    salt, stored_hash = stored_password.split(':')  # Extraemos el salt y el hash
    new_hash = hashlib.sha256(bytes.fromhex(salt) + provided_password.encode('utf-8')).hexdigest()
    return new_hash == stored_hash  # Comparamos el hash generado con el almacenado

def login_user(data):
    # Controlador para manejar el inicio de sesión
    email = data.get('email_user')
    password = data.get('password_user')

    # Verificar que los campos requeridos están presentes
    if not email or not password:
        return {"message": "El correo y la contraseña son obligatorios"}, 400

    # Buscar al usuario en la base de datos por correo
    user = User.query.filter_by(email_user=email).first()

    if not user:
        return {"message": "Usuario no encontrado"}, 404

    # Verificar la contraseña
    if not verify_password(user.password_user, password):
        return {"message": "Contraseña incorrecta"}, 401

    # Configurar la zona horaria GMT-5
    gmt_minus_5 = pytz.timezone('Etc/GMT+5')  # En pytz, GMT+5 representa UTC-5

    # Obtener la hora actual en la zona horaria GMT-5
    now_gmt_minus_5 = datetime.now(gmt_minus_5)

    # Actualizar la última fecha de inicio de sesión
    try:
        user.lastDayLogin_user = now_gmt_minus_5
        db.session.commit()  # Guardar los cambios en la base de datos
    except Exception as e:
        return {"message": "Error al actualizar la última fecha de inicio de sesión", "error": str(e)}, 500

    # Generar un token JWT
    secret_key = os.getenv('SECRET_KEY')  # Asegúrate de definir esta variable de entorno
    expiration = now_gmt_minus_5 + timedelta(hours=1)  # El token expira en 1 hora
    payload = {
        "iduser": user.iduser,
        "email_user": user.email_user,
        "exp": expiration
    }
    token = jwt.encode(payload, secret_key, algorithm="HS256")

    return {
        "message": "Inicio de sesión exitoso",
        "token": token,
    }, 200