from flask import jsonify
from db.connection import db
from models.activities_researchHotbed import ActivitiesResearchHotbed
from models.users_research_hotbed import UsersResearchHotbed
from models.users import User  # Cambié de 'user' a 'users'
from models.activity_authors import ActivityAuthors

def get_activities_by_research_hotbed(research_hotbed_id):
    try:
        # Obtener actividades a través de ActivityAuthors
        activities_via_authors = db.session.query(ActivitiesResearchHotbed)\
            .join(ActivityAuthors, ActivitiesResearchHotbed.idactivitiesResearchHotbed == ActivityAuthors.activity_id)\
            .join(UsersResearchHotbed, ActivityAuthors.user_research_hotbed_id == UsersResearchHotbed.idusersResearchHotbed)\
            .filter(UsersResearchHotbed.researchHotbed_idresearchHotbed == research_hotbed_id)\
            .all()

        # Obtener actividades a través de la relación directa (implementación actual)
        activities_via_direct = db.session.query(ActivitiesResearchHotbed)\
            .join(UsersResearchHotbed, ActivitiesResearchHotbed.usersResearchHotbed_idusersResearchHotbed == UsersResearchHotbed.idusersResearchHotbed)\
            .filter(UsersResearchHotbed.researchHotbed_idresearchHotbed == research_hotbed_id)\
            .all()

        # Combinar y eliminar duplicados
        activity_ids = set()
        unique_activities = []
        
        for activity in activities_via_authors + activities_via_direct:
            if activity.idactivitiesResearchHotbed not in activity_ids:
                activity_ids.add(activity.idactivitiesResearchHotbed)
                unique_activities.append(activity)
        
        # Ordenar por fecha
        unique_activities.sort(key=lambda x: x.date_activitiesResearchHotbed, reverse=True)

        if not unique_activities:
            return jsonify({"activities": []}), 200

        activities_list = []
        
        for activity in unique_activities:
            # Obtener el usuario responsable
            user_research_hotbed = db.session.query(UsersResearchHotbed)\
                .filter_by(idusersResearchHotbed=activity.usersResearchHotbed_idusersResearchHotbed)\
                .first()
            
            if user_research_hotbed:
                user = db.session.query(User)\
                    .filter_by(iduser=user_research_hotbed.user_iduser)\
                    .first()
                responsible = user.name_user if user else "Usuario no encontrado"
            else:
                responsible = "Usuario no encontrado"

            activity_data = {
                "activity_id": activity.idactivitiesResearchHotbed,
                "title": activity.title_activitiesResearchHotbed,
                "responsible": responsible,
                "date": activity.date_activitiesResearchHotbed.isoformat() if activity.date_activitiesResearchHotbed else None,
                "description": activity.description_activitiesResearchHotbed,
                "type": activity.type_activitiesResearchHotbed,
                "start_time": activity.startTime_activitiesResearchHotbed.isoformat() if activity.startTime_activitiesResearchHotbed else None,
                "end_time": activity.endTime_activitiesResearchHotbed.isoformat() if activity.endTime_activitiesResearchHotbed else None,
                "duration": activity.duration_activitiesResearchHotbed,
                "approved_free_hours": activity.approvedFreeHours_activitiesResearchHotbed
            }

            # Obtener datos relacionados según el tipo
            if activity.type_activitiesResearchHotbed.lower() == 'proyecto' and activity.projectsResearchHotbed_idprojectsResearchHotbed:
                from models.projects_researchHotbed import ProjectsResearchHotbed
                project = db.session.query(ProjectsResearchHotbed)\
                    .filter_by(idprojectsResearchHotbed=activity.projectsResearchHotbed_idprojectsResearchHotbed)\
                    .first()
                if project:
                    activity_data["project"] = {
                        "name": project.name_projectsResearchHotbed,
                        "reference_number": project.referenceNumber_projectsResearchHotbed,
                        "start_date": project.startDate_projectsResearchHotbed.isoformat() if project.startDate_projectsResearchHotbed else None,
                        "end_date": project.endDate_projectsResearchHotbed.isoformat() if project.endDate_projectsResearchHotbed else None,
                        "principal_researcher": project.principalResearcher_projectsResearchHotbed,
                        "co_researchers": project.coResearchers_projectsResearchHotbed
                    }

            if activity.type_activitiesResearchHotbed.lower() == 'producto' and activity.productsResearchHotbed_idproductsResearchHotbed:
                from models.products_researchHotbed import ProductsResearchHotbed
                product = db.session.query(ProductsResearchHotbed)\
                    .filter_by(idproductsResearchHotbed=activity.productsResearchHotbed_idproductsResearchHotbed)\
                    .first()
                if product:
                    activity_data["product"] = {
                        "category": product.category_productsResearchHotbed,
                        "type": product.type_productsResearchHotbed,
                        "description": product.description_productsResearchHotbed,
                        "publication_date": product.datePublication_productsResearchHotbed.isoformat() if product.datePublication_productsResearchHotbed else None
                    }

            if activity.type_activitiesResearchHotbed.lower() == 'reconocimiento' and activity.recognitionsResearchHotbed_idrecognitionsResearchHotbed:
                from models.recognitions_researchHotbed import RecognitionsResearchHotbed
                recognition = db.session.query(RecognitionsResearchHotbed)\
                    .filter_by(idrecognitionsResearchHotbed=activity.recognitionsResearchHotbed_idrecognitionsResearchHotbed)\
                    .first()
                if recognition:
                    activity_data["recognition"] = {
                        "name": recognition.name_recognitionsResearchHotbed,
                        "project_name": recognition.projectName_recognitionsResearchHotbed,
                        "participants": recognition.participantsNames_recognitionsResearchHotbed,
                        "organization": recognition.organizationName_recognitionsResearchHotbed
                    }

            activities_list.append(activity_data)

        return jsonify({"activities": activities_list}), 200

    except Exception as e:
        print(f"Error en get_activities_by_research_hotbed: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500