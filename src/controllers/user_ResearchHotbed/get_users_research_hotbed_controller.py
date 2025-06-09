from flask import jsonify
from models.users import User
from models.users_research_hotbed import UsersResearchHotbed
from models.research_hotbed import ResearchHotbed
from db.connection import db

def get_users_by_research_hotbed(research_hotbed_id):
    """
    Obtiene TODOS los usuarios asociados a un semillero específico (activos e inactivos).
    :param research_hotbed_id: ID del semillero de investigación.
    :return: Lista de usuarios o mensaje de error.
    """
    try:
        # Verificar si el semillero existe
        research_hotbed = ResearchHotbed.query.get(research_hotbed_id)
        if not research_hotbed:
            return {"message": "Semillero de investigación no encontrado"}, 404

        # CORREGIR: Obtener TODOS los usuarios asociados al semillero (activos e inactivos)
        users_query = db.session.query(User, UsersResearchHotbed)\
            .join(UsersResearchHotbed, User.iduser == UsersResearchHotbed.user_iduser)\
            .filter(UsersResearchHotbed.researchHotbed_idresearchHotbed == research_hotbed_id)\
            .order_by(
                # Activos primero, luego inactivos
                (UsersResearchHotbed.status_usersResearchHotbed == 'Activo').desc(),
                User.name_user.asc()
            )\
            .all()

        if not users_query:
            return {"message": "No se encontraron usuarios en este semillero"}, 404

        # Formatear la respuesta
        users_list = []
        for user, user_research_hotbed in users_query:
            user_data = {
                # IMPORTANTE: Usar idusersResearchHotbed, NO iduser
                "idusersResearchHotbed": user_research_hotbed.idusersResearchHotbed,
                "iduser": user.iduser,  # Mantener para referencia
                "name_user": user.name_user,
                "email_user": user.email_user,
                "idSigaa_user": user.idSigaa_user,
                "status_user": user.status_user,
                "type_user": user.type_user,
                "academicProgram_user": user.academicProgram_user,
                "TypeUser_usersResearchHotbed": user_research_hotbed.TypeUser_usersResearchHotbed,
                "status_usersResearchHotbed": user_research_hotbed.status_usersResearchHotbed,
                "observation_usersResearchHotbed": user_research_hotbed.observation_usersResearchHotbed,
                "dateEnter_usersResearchHotbed": user_research_hotbed.dateEnter_usersResearchHotbed.isoformat() if user_research_hotbed.dateEnter_usersResearchHotbed else None,
                "dateExit_usersResearchHotbed": user_research_hotbed.dateExit_usersResearchHotbed.isoformat() if user_research_hotbed.dateExit_usersResearchHotbed else None
            }
            users_list.append(user_data)

        return {"users": users_list}, 200

    except Exception as e:
        print(f"Error en get_users_by_research_hotbed: {str(e)}")
        return {"message": f"Error interno del servidor: {str(e)}"}, 500
