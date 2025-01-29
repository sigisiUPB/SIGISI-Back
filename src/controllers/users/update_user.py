from models.users import User
from db.connection import db

def update_user(user_id, data):
    """
    Controlador para actualizar los datos del usuario autenticado.
    :param user_id: ID del usuario autenticado (extraído del token).
    :param data: Datos enviados por el cliente para actualizar.
    :return: Mensaje de éxito o error.
    """
    # Buscar al usuario en la base de datos
    user = User.query.filter_by(iduser=user_id).first()

    if not user:
        return {"message": "Usuario no encontrado"}, 404

    # Actualizar solo los campos proporcionados en la solicitud
    updatable_fields = [
        "email_user", "idSigaa_user", "name_user", 
        "status_user", "type_user", "academicProgram_user"
    ]
    for field in updatable_fields:
        if field in data:
            setattr(user, field, data[field])  # Actualiza dinámicamente el campo

    # Guardar los cambios en la base de datos
    try:
        db.session.commit()
        return {"message": "Usuario actualizado con éxito"}, 200
    except Exception as e:
        db.session.rollback()
        return {"message": f"Error al actualizar el usuario: {str(e)}"}, 500