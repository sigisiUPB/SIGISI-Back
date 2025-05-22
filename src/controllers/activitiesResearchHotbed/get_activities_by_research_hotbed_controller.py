from flask import jsonify
from models.activities_researchHotbed import ActivitiesResearchHotbed
from models.projects_researchHotbed import ProjectsResearchHotbed
from models.products_researchHotbed import ProductsResearchHotbed
from models.recognitions_researchHotbed import RecognitionsResearchHotbed
from models.users_research_hotbed import UsersResearchHotbed
from db.connection import db

def get_activities_by_research_hotbed(research_hotbed_id):
    try:
        # Consultar todas las actividades del semillero a través de los usuarios
        activities = db.session.query(ActivitiesResearchHotbed)\
            .join(UsersResearchHotbed, ActivitiesResearchHotbed.usersResearchHotbed_idusersResearchHotbed == UsersResearchHotbed.idusersResearchHotbed)\
            .filter(UsersResearchHotbed.researchHotbed_idresearchHotbed == research_hotbed_id)\
            .order_by(ActivitiesResearchHotbed.date_activitiesResearchHotbed.desc())\
            .all()

        if not activities:
            return jsonify({"activities": []}), 200

        activities_list = []
        
        for activity in activities:
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

            # Crear el objeto de actividad
            activity_data = {
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
            }

            # Agregar detalles del proyecto si existe
            if project:
                activity_data["project"] = {
                    "name": project.name_projectsResearchHotbed,
                    "reference_number": project.referenceNumber_projectsResearchHotbed,
                    "start_date": project.startDate_projectsResearchHotbed.strftime('%Y-%m-%d'),
                    "end_date": project.endDate_projectsResearchHotbed.strftime('%Y-%m-%d') if project.endDate_projectsResearchHotbed else None,
                    "principal_researcher": project.principalResearcher_projectsResearchHotbed,
                    "co_researchers": project.coResearchers_projectsResearchHotbed
                }

            # Agregar detalles del producto si existe
            if product:
                activity_data["product"] = {
                    "category": product.category_productsResearchHotbed,
                    "type": product.type_productsResearchHotbed,
                    "description": product.description_productsResearchHotbed,
                    "date_publication": product.datePublication_productsResearchHotbed.strftime('%Y-%m-%d')
                }

            # Agregar detalles del reconocimiento si existe
            if recognition:
                activity_data["recognition"] = {
                    "name": recognition.name_recognitionsResearchHotbed,
                    "project_name": recognition.projectName_recognitionsResearchHotbed,
                    "participants_names": recognition.participantsNames_recognitionsResearchHotbed,
                    "organization_name": recognition.organizationName_recognitionsResearchHotbed
                }

            activities_list.append(activity_data)

        return jsonify({"activities": activities_list}), 200

    except Exception as e:
        print(f"Error en get_activities_by_research_hotbed: {str(e)}")
        return jsonify({"error": str(e)}), 500