from flask import jsonify
from models.activities_researchHotbed import ActivitiesResearchHotbed
from models.users_research_hotbed import UsersResearchHotbed
from models.research_hotbed import ResearchHotbed
from models.projects_researchHotbed import ProjectsResearchHotbed
from models.products_researchHotbed import ProductsResearchHotbed
from models.recognitions_researchHotbed import RecognitionsResearchHotbed
from db.connection import db

def get_user_activities(user_id):
    """
    Obtiene todas las actividades de un usuario en todos sus semilleros.
    :param user_id: ID del usuario.
    :return: Lista de actividades del usuario.
    """
    try:
        # Consultar todas las actividades del usuario a través de sus relaciones con semilleros
        activities = db.session.query(
            ActivitiesResearchHotbed,
            ResearchHotbed.name_researchHotbed
        ).join(
            UsersResearchHotbed, 
            ActivitiesResearchHotbed.usersResearchHotbed_idusersResearchHotbed == UsersResearchHotbed.idusersResearchHotbed
        ).join(
            ResearchHotbed,
            UsersResearchHotbed.researchHotbed_idresearchHotbed == ResearchHotbed.idresearchHotbed
        ).filter(
            UsersResearchHotbed.user_iduser == user_id
        ).order_by(
            ActivitiesResearchHotbed.date_activitiesResearchHotbed.desc()
        ).all()

        if not activities:
            return jsonify({"activities": []}), 200

        activities_list = []
        
        for activity_data in activities:
            activity = activity_data[0]  # La actividad
            research_hotbed_name = activity_data[1]  # El nombre del semillero

            # Obtener detalles del proyecto asociado (si existe)
            project = None
            if activity.projectsResearchHotbed_idprojectsResearchHotbed:
                project = ProjectsResearchHotbed.query.filter_by(
                    idprojectsResearchHotbed=activity.projectsResearchHotbed_idprojectsResearchHotbed
                ).first()

            # Obtener detalles del producto asociado (si existe)
            product = None
            if activity.productsResearchHotbed_idproductsResearchHotbed:
                product = ProductsResearchHotbed.query.filter_by(
                    idproductsResearchHotbed=activity.productsResearchHotbed_idproductsResearchHotbed
                ).first()

            # Obtener detalles del reconocimiento asociado (si existe)
            recognition = None
            if activity.recognitionsResearchHotbed_idrecognitionsResearchHotbed:
                recognition = RecognitionsResearchHotbed.query.filter_by(
                    idrecognitionsResearchHotbed=activity.recognitionsResearchHotbed_idrecognitionsResearchHotbed
                ).first()

            # Crear el objeto de datos de la actividad
            activity_info = {
                "activity_id": activity.idactivitiesResearchHotbed,
                "title": activity.title_activitiesResearchHotbed,
                "responsible": activity.responsible_activitiesResearchHotbed,
                "date": activity.date_activitiesResearchHotbed.strftime('%Y-%m-%d'),
                "description": activity.description_activitiesResearchHotbed,
                "type": activity.type_activitiesResearchHotbed,
                "start_time": activity.startTime_activitiesResearchHotbed.strftime('%H:%M') if activity.startTime_activitiesResearchHotbed else None,
                "end_time": activity.endTime_activitiesResearchHotbed.strftime('%H:%M') if activity.endTime_activitiesResearchHotbed else None,
                "duration": activity.duration_activitiesResearchHotbed,
                "approved_free_hours": activity.approvedFreeHours_activitiesResearchHotbed,
                "research_hotbed_name": research_hotbed_name
            }

            # Agregar detalles del proyecto si existe
            if project:
                activity_info["project"] = {
                    "name": project.name_projectsResearchHotbed,
                    "reference_number": project.referenceNumber_projectsResearchHotbed,
                    "start_date": project.startDate_projectsResearchHotbed.strftime('%Y-%m-%d'),
                    "end_date": project.endDate_projectsResearchHotbed.strftime('%Y-%m-%d') if project.endDate_projectsResearchHotbed else None,
                    "principal_researcher": project.principalResearcher_projectsResearchHotbed,
                    "co_researchers": project.coResearchers_projectsResearchHotbed
                }

            # Agregar detalles del producto si existe
            if product:
                activity_info["product"] = {
                    "category": product.category_productsResearchHotbed,
                    "type": product.type_productsResearchHotbed,
                    "description": product.description_productsResearchHotbed,
                    "date_publication": product.datePublication_productsResearchHotbed.strftime('%Y-%m-%d')
                }

            # Agregar detalles del reconocimiento si existe
            if recognition:
                activity_info["recognition"] = {
                    "name": recognition.name_recognitionsResearchHotbed,
                    "project_name": recognition.projectName_recognitionsResearchHotbed,
                    "participants_names": recognition.participantsNames_recognitionsResearchHotbed,
                    "organization_name": recognition.organizationName_recognitionsResearchHotbed
                }

            activities_list.append(activity_info)

        return jsonify({"activities": activities_list}), 200

    except Exception as e:
        print(f"Error al obtener actividades del usuario: {str(e)}")
        return jsonify({"error": f"Error al obtener las actividades: {str(e)}"}), 500