from flask import jsonify
from models.activities_researchHotbed import ActivitiesResearchHotbed
from models.projects_researchHotbed import ProjectsResearchHotbed
from models.products_researchHotbed import ProductsResearchHotbed
from models.recognitions_researchHotbed import RecognitionsResearchHotbed
from models.users_research_hotbed import UsersResearchHotbed
from db.connection import db

def get_activity_details(activity_id):
    try:
        # Consultar la actividad por su ID
        activity = ActivitiesResearchHotbed.query.filter_by(idactivitiesResearchHotbed=activity_id).first()

        if not activity:
            return jsonify({"message": "Actividad no encontrada"}), 404

        # Obtener detalles del proyecto asociado (si existe)
        project = None
        if activity.projectsResearchHotbed_idprojectsResearchHotbed:
            project = ProjectsResearchHotbed.query.filter_by(idprojectsResearchHotbed=activity.projectsResearchHotbed_idprojectsResearchHotbed).first()

        # Obtener detalles del producto asociado (si existe)
        product = None
        if activity.productsResearchHotbed_idproductsResearchHotbed:
            product = ProductsResearchHotbed.query.filter_by(idproductsResearchHotbed=activity.productsResearchHotbed_idproductsResearchHotbed).first()

        # Obtener detalles del reconocimiento asociado (si existe)
        recognition = None
        if activity.recognitionsResearchHotbed_idrecognitionsResearchHotbed:
            recognition = RecognitionsResearchHotbed.query.filter_by(idrecognitionsResearchHotbed=activity.recognitionsResearchHotbed_idrecognitionsResearchHotbed).first()

        # Obtener detalles del usuario asociado (si existe)
        user = None
        if activity.usersResearchHotbed_idusersResearchHotbed:
            user = UsersResearchHotbed.query.filter_by(idusersResearchHotbed=activity.usersResearchHotbed_idusersResearchHotbed).first()

        # Crear el objeto de respuesta con toda la información
        activity_details = {
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

        # Agregar detalles del proyecto, producto, reconocimiento y usuario si existen
        if project:
            activity_details["project"] = {
                "name": project.name_projectsResearchHotbed,
                "reference_number": project.referenceNumber_projectsResearchHotbed,
                "start_date": project.startDate_projectsResearchHotbed.strftime('%Y-%m-%d'),
                "end_date": project.endDate_projectsResearchHotbed.strftime('%Y-%m-%d') if project.endDate_projectsResearchHotbed else None,
                "principal_researcher": project.principalResearcher_projectsResearchHotbed,
                "co_researchers": project.coResearchers_projectsResearchHotbed
            }

        if product:
            activity_details["product"] = {
                "category": product.category_productsResearchHotbed,
                "type": product.type_productsResearchHotbed,
                "description": product.description_productsResearchHotbed,
                "date_publication": product.datePublication_productsResearchHotbed.strftime('%Y-%m-%d')
            }

        if recognition:
            activity_details["recognition"] = {
                "name": recognition.name_recognitionsResearchHotbed,
                "project_name": recognition.projectName_recognitionsResearchHotbed,
                "participants_names": recognition.participantsNames_recognitionsResearchHotbed,
                "organization_name": recognition.organizationName_recognitionsResearchHotbed
            }

        if user:
            activity_details["user"] = {
                "name": user.user.name_user, 
                "email": user.user.email_user,
                "idSigaa": user.user.idSigaa_user
            }


        return jsonify({"activity_details": activity_details}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
