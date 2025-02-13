from models.users_research_hotbed import UsersResearchHotbed
from models.research_hotbed import ResearchHotbed
from db.connection import db

def get_research_hotbeds_by_user(user_id):
    """
    Obtiene todos los semilleros a los que pertenece un usuario.
    :param user_id: ID del usuario.
    :return: Lista de semilleros o mensaje de error.
    """
    # Buscar los semilleros en los que está el usuario
    user_hotbeds = db.session.query(
        ResearchHotbed.idresearchHotbed,
        ResearchHotbed.name_researchHotbed,
        ResearchHotbed.universityBranch_researchHotbed,
        ResearchHotbed.acronym_researchHotbed,
        ResearchHotbed.faculty_researchHotbed,
        ResearchHotbed.status_researchHotbed,
        ResearchHotbed.dateCreation_researchHotbed
    ).join(UsersResearchHotbed, ResearchHotbed.idresearchHotbed == UsersResearchHotbed.researchHotbed_idresearchHotbed
    ).filter(UsersResearchHotbed.user_iduser == user_id).all()

    if not user_hotbeds:
        return {"message": "El usuario no pertenece a ningún semillero"}, 404

    # Convertir el resultado en una lista de diccionarios
    hotbeds_list = [
        {
            "id": hotbed.idresearchHotbed,
            "name": hotbed.name_researchHotbed,
            "university_branch": hotbed.universityBranch_researchHotbed,
            "acronym": hotbed.acronym_researchHotbed,
            "faculty": hotbed.faculty_researchHotbed,
            "status": hotbed.status_researchHotbed,
            "date_creation": hotbed.dateCreation_researchHotbed
        }
        for hotbed in user_hotbeds
    ]

    return {"research_hotbeds": hotbeds_list}, 200
