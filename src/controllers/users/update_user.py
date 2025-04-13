import hashlib
import os
from models.users import User
from db.connection import db

def hash_password(password):
    """
    Genera un hash seguro para la contraseña utilizando SHA-256 con un salt aleatorio.
    """
    salt = os.urandom(16).hex()  # Genera un salt aleatorio de 16 bytes en formato hexadecimal
    hashed_password = hashlib.sha256(bytes.fromhex(salt) + password.encode('utf-8')).hexdigest()
    return f"{salt}:{hashed_password}"  # Guardamos salt y hash juntos

def update_user(user_id, data):
    """
    Controlador para actualizar los datos de un usuario.
    :param user_id: ID del usuario a actualizar.
    :param data: Datos enviados por el cliente para actualizar.
    :return: Mensaje de éxito o error.
    """
    # Buscar al usuario en la base de datos
    user = User.query.filter_by(iduser=user_id).first()

    if not user:
        return {"message": "Usuario no encontrado"}, 404

    # Definir los campos permitidos para actualización
    updatable_fields = [
        "email_user", "idSigaa_user", "name_user", 
        "status_user", "type_user", "academicProgram_user"
    ]

    # Actualizar los campos proporcionados en la solicitud
    for field in updatable_fields:
        if field in data:
            setattr(user, field, data[field])  # Actualiza dinámicamente el campo

    # Si el usuario proporciona una nueva contraseña, la hasheamos antes de guardarla
    if "password_user" in data:
        new_password = data["password_user"]
        if new_password.strip():  # Verificamos que la contraseña no esté vacía
            user.password_user = hash_password(new_password)

    # Guardar los cambios en la base de datos
    try:
        db.session.commit()
        return {"message": "Usuario actualizado con éxito"}, 200
    except Exception as e:
        db.session.rollback()
        return {"message": f"Error al actualizar el usuario: {str(e)}"}, 500
