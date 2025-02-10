from models.users_research_hotbed import UsersResearchHotbed
from db.connection import db

def update_user_in_research_hotbed(user_research_hotbed_id, data):
    """
    Actualiza la información de un usuario dentro de un semillero.
    :param user_research_hotbed_id: ID de la relación usuario-semillero.
    :param data: Datos a actualizar.
    :return: Mensaje de éxito o error.
    """
    # Buscar la relación usuario-semillero en la base de datos
    user_research_hotbed = UsersResearchHotbed.query.get(user_research_hotbed_id)

    if not user_research_hotbed:
        return {"message": "Usuario no encontrado en este semillero"}, 404

    # Campos que se pueden actualizar
    updatable_fields = [
        "status_usersResearchHotbed", "TypeUser_usersResearchHotbed", 
        "observation_usersResearchHotbed", "dateExit_usersResearchHotbed"
    ]

    for field in updatable_fields:
        if field in data:
            setattr(user_research_hotbed, field, data[field])

    # Guardar los cambios en la base de datos
    try:
        db.session.commit()
        return {"message": "Usuario en semillero actualizado con éxito"}, 200
    except Exception as e:
        db.session.rollback()
        return {"message": f"Error al actualizar el usuario en semillero: {str(e)}"}, 500
