from flask import jsonify
from models.activities_researchHotbed import ActivitiesResearchHotbed
from models.projects_researchHotbed import ProjectsResearchHotbed
from models.products_researchHotbed import ProductsResearchHotbed
from models.recognitions_researchHotbed import RecognitionsResearchHotbed
from models.activity_authors import ActivityAuthors
from models.users_research_hotbed import UsersResearchHotbed
from models.users import User
from db.connection import db

def get_activity_details(activity_id):
    """
    Obtiene los detalles completos de una actividad específica.
    """
    try:
        # Obtener la actividad principal
        activity = db.session.query(ActivitiesResearchHotbed).filter_by(
            idactivitiesResearchHotbed=activity_id
        ).first()

        if not activity:
            return jsonify({"error": "Actividad no encontrada"}), 404

        # Construir la respuesta base
        activity_data = {
            "id": activity.idactivitiesResearchHotbed,
            "title": activity.title_activitiesResearchHotbed,
            "responsible": activity.responsible_activitiesResearchHotbed,
            "date": activity.date_activitiesResearchHotbed.isoformat() if activity.date_activitiesResearchHotbed else None,
            "description": activity.description_activitiesResearchHotbed,
            "type": activity.type_activitiesResearchHotbed,
            "start_time": activity.startTime_activitiesResearchHotbed.strftime('%H:%M') if activity.startTime_activitiesResearchHotbed else '',
            "end_time": activity.endTime_activitiesResearchHotbed.strftime('%H:%M') if activity.endTime_activitiesResearchHotbed else '',
            "duration": float(activity.duration_activitiesResearchHotbed) if activity.duration_activitiesResearchHotbed else 0,
            "approved_free_hours": bool(activity.approvedFreeHours_activitiesResearchHotbed) if activity.approvedFreeHours_activitiesResearchHotbed else False,
            "semester": getattr(activity, 'semester', 'semestre-1-2025'),  # CORREGIDO
            "project": None,
            "product": None,
            "recognition": None,
            "authors": [],
            "co_authors": []
        }

        # Obtener datos del proyecto si existe
        if activity.projectsResearchHotbed_idprojectsResearchHotbed:
            project = db.session.query(ProjectsResearchHotbed).filter_by(
                idprojectsResearchHotbed=activity.projectsResearchHotbed_idprojectsResearchHotbed
            ).first()
            
            if project:
                activity_data["project"] = {
                    "name": getattr(project, 'name_projectsResearchHotbed', ''),  # CORREGIDO
                    "reference_number": project.referenceNumber_projectsResearchHotbed,
                    "start_date": project.startDate_projectsResearchHotbed.isoformat() if project.startDate_projectsResearchHotbed else "",
                    "end_date": project.endDate_projectsResearchHotbed.isoformat() if project.endDate_projectsResearchHotbed else "",
                    "principal_researcher": project.principalResearcher_projectsResearchHotbed,
                }

        # Obtener datos del producto si existe
        if activity.productsResearchHotbed_idproductsResearchHotbed:
            product = db.session.query(ProductsResearchHotbed).filter_by(
                idproductsResearchHotbed=activity.productsResearchHotbed_idproductsResearchHotbed
            ).first()
            
            if product:
                activity_data["product"] = {
                    "category": product.category_productsResearchHotbed,
                    "type": product.type_productsResearchHotbed,
                    "description": product.description_productsResearchHotbed,
                    "date_publication": product.datePublication_productsResearchHotbed.isoformat() if hasattr(product, 'datePublication_productsResearchHotbed') and product.datePublication_productsResearchHotbed else ""  # CORREGIDO
                }

        # Obtener datos del reconocimiento si existe
        if activity.recognitionsResearchHotbed_idrecognitionsResearchHotbed:
            recognition = db.session.query(RecognitionsResearchHotbed).filter_by(
                idrecognitionsResearchHotbed=activity.recognitionsResearchHotbed_idrecognitionsResearchHotbed
            ).first()
            
            if recognition:
                activity_data["recognition"] = {
                    "name": getattr(recognition, 'name_recognitionsResearchHotbed', ''),  # CORREGIDO
                    "project_name": recognition.projectName_recognitionsResearchHotbed,
                    "participants_names": getattr(recognition, 'participantsNames_recognitionsResearchHotbed', ''),  # CORREGIDO
                    "organization_name": recognition.organizationName_recognitionsResearchHotbed
                }

        # Obtener autores y co-autores
        try:
            authors_relations = db.session.query(ActivityAuthors, UsersResearchHotbed, User)\
                .join(UsersResearchHotbed, ActivityAuthors.user_research_hotbed_id == UsersResearchHotbed.idusersResearchHotbed)\
                .join(User, UsersResearchHotbed.user_iduser == User.iduser)\
                .filter(ActivityAuthors.activity_id == activity_id)\
                .all()

            authors = []
            co_authors = []

            for author_rel, user_rh, user in authors_relations:
                user_data = {
                    "id": user_rh.idusersResearchHotbed,
                    "name": user.name_user,
                    "email": user.email_user,
                    "type": user_rh.TypeUser_usersResearchHotbed
                }
                
                if author_rel.is_main_author:
                    authors.append(user_data)
                else:
                    co_authors.append(user_data)

            activity_data["authors"] = authors
            activity_data["co_authors"] = co_authors

        except Exception as e:
            print(f"Error al obtener autores: {str(e)}")

        return jsonify({"activity_details": activity_data}), 200

    except Exception as e:
        print(f"Error en get_activity_details: {str(e)}")
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
