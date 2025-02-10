from models.users_research_hotbed import UsersResearchHotbed
from db.connection import db

def delete_user_from_research_hotbed(user_research_hotbed_id):
    """
    Elimina la relación de un usuario con un semillero.
    :param user_research_hotbed_id: ID de la relación usuario-semillero.
    :return: Mensaje de éxito o error.
    """
    # Buscar la relación usuario-semillero
    user_research_hotbed = UsersResearchHotbed.query.get(user_research_hotbed_id)

    if not user_research_hotbed:
        return {"message": "Usuario no encontrado en este semillero"}, 404

    try:
        db.session.delete(user_research_hotbed)
        db.session.commit()
        return {"message": "Usuario eliminado del semillero con éxito"}, 200
    except Exception as e:
        db.session.rollback()
        return {"message": f"Error al eliminar el usuario del semillero: {str(e)}"}, 500
