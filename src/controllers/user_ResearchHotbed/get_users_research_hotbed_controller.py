from models.users import User
from models.research_hotbed import ResearchHotbed
from models.users_research_hotbed import UsersResearchHotbed
from db.connection import db

def get_users_by_research_hotbed(research_hotbed_id):
    """
    Obtiene todos los usuarios asociados a un semillero específico.
    :param research_hotbed_id: ID del semillero de investigación.
    :return: Lista de usuarios o mensaje de error.
    """
    # Verificar si el semillero existe
    research_hotbed = ResearchHotbed.query.get(research_hotbed_id)
    if not research_hotbed:
        return {"message": "Semillero de investigación no encontrado"}, 404

    # Obtener los usuarios asociados al semillero
    users = db.session.query(User, UsersResearchHotbed).join(UsersResearchHotbed).filter(
        UsersResearchHotbed.researchHotbed_idresearchHotbed == research_hotbed_id
    ).all()

    # Formatear la respuesta
    users_list = [{
        "iduser": user.iduser,
        "name_user": user.name_user,
        "email_user": user.email_user,
        "idSigaa_user": user.idSigaa_user,
        "status_usersResearchHotbed": relation.status_usersResearchHotbed,
        "TypeUser_usersResearchHotbed": relation.TypeUser_usersResearchHotbed,
        "observation_usersResearchHotbed": relation.observation_usersResearchHotbed,
        "dateEnter_usersResearchHotbed": relation.dateEnter_usersResearchHotbed.strftime('%Y-%m-%d'),
        "dateExit_usersResearchHotbed": relation.dateExit_usersResearchHotbed.strftime('%Y-%m-%d') if relation.dateExit_usersResearchHotbed else None
    } for user, relation in users]

    return {"research_hotbed": research_hotbed.name_researchHotbed, "users": users_list}, 200
