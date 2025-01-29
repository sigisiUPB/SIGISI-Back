from models.users import User

def get_user_data(user_id):
    """
    Controlador para obtener todos los datos del usuario autenticado.
    :param user_id: ID del usuario autenticado (extraído del token).
    :return: Información completa del usuario o un mensaje de error.
    """
    # Buscar al usuario en la base de datos por su ID
    user = User.query.filter_by(iduser=user_id).first()

    if not user:
        return {"message": "Usuario no encontrado"}, 404

    # Construir la respuesta con todos los datos del usuario
    user_data = {
        "iduser": user.iduser,
        "email_user": user.email_user,
        "idSigaa_user": user.idSigaa_user,
        "name_user": user.name_user,
        "status_user": user.status_user,
        "type_user": user.type_user,
        "academicProgram_user": user.academicProgram_user,
        "termsAccepted_user": user.termsAccepted_user,
        "termsAcceptedAt_user": user.termsAcceptedAt_user.strftime('%Y-%m-%d %H:%M:%S'),
        "termsVersion_user": user.termsVersion_user
    }

    return user_data, 200