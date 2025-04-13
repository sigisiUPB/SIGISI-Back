from models.users import User
from models.research_hotbed import ResearchHotbed
from models.users_research_hotbed import UsersResearchHotbed
from db.connection import db
from datetime import datetime, UTC

def add_user_to_research_hotbed(user_id, research_hotbed_id, data):
    """
    Agrega un usuario a un semillero de investigación.
    :param user_id: ID del usuario.
    :param research_hotbed_id: ID del semillero.
    :param data: Datos adicionales (estado, tipo de usuario, observaciones).
    :return: Mensaje de éxito o error.
    """
    # Verificar si el usuario y el semillero existen
    user = User.query.get(user_id)
    research_hotbed = ResearchHotbed.query.get(research_hotbed_id)

    if not user:
        return {"message": "Usuario no encontrado"}, 404
    if not research_hotbed:
        return {"message": "Semillero de investigación no encontrado"}, 404

    # Verificar si el usuario ya está en el semillero
    existing_entry = UsersResearchHotbed.query.filter_by(user_iduser=user_id, researchHotbed_idresearchHotbed=research_hotbed_id).first()
    if existing_entry:
        return {"message": "El usuario ya está asociado a este semillero"}, 400

    # Crear nueva relación usuario-semillero
    new_entry = UsersResearchHotbed(
        status_usersResearchHotbed=data.get("status_usersResearchHotbed", "active"),
        TypeUser_usersResearchHotbed=data.get("TypeUser_usersResearchHotbed", "Estudiante"),
        observation_usersResearchHotbed=data.get("observation_usersResearchHotbed", None),
        dateEnter_usersResearchHotbed=datetime.now(UTC).date(),
        researchHotbed_idresearchHotbed=research_hotbed_id,
        user_iduser=user_id
    )

    # Guardar en la base de datos
    try:
        db.session.add(new_entry)
        db.session.commit()
        return {"message": "Usuario agregado al semillero con éxito"}, 201
    except Exception as e:
        db.session.rollback()
        return {"message": f"Error al agregar usuario al semillero: {str(e)}"}, 500
