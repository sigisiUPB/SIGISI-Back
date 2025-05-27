from flask import jsonify
from models.activities_researchHotbed import ActivitiesResearchHotbed
from models.users_research_hotbed import UsersResearchHotbed
from models.research_hotbed import ResearchHotbed
from models.projects_researchHotbed import ProjectsResearchHotbed
from models.products_researchHotbed import ProductsResearchHotbed
from models.recognitions_researchHotbed import RecognitionsResearchHotbed
from models.activity_authors import ActivityAuthors
import models.users as UserModel
from db.connection import db

def get_user_activities(user_id):
    """
    Obtiene todas las actividades donde el usuario es autor o co-autor.
    :param user_id: ID del usuario.
    :return: Lista de actividades del usuario.
    """
    try:
        # Obtener la clase del modelo de usuario dinámicamente
        UserClass = getattr(UserModel, 'Users', None) or getattr(UserModel, 'users', None) or getattr(UserModel, 'User', None)
        
        if not UserClass:
            return jsonify({"error": "No se pudo encontrar el modelo de usuario"}), 500
        
        # Primero obtener el nombre del usuario actual
        current_user = UserClass.query.filter_by(iduser=user_id).first()
        if not current_user:
            return jsonify({"activities": []}), 200
        
        current_user_name = current_user.name_user

        # Obtener el UsersResearchHotbed del usuario actual
        user_research_hotbed = UsersResearchHotbed.query.filter_by(user_iduser=user_id).first()
        if not user_research_hotbed:
            return jsonify({"activities": []}), 200

        # Consultar actividades donde el usuario es autor o co-autor a través de ActivityAuthors
        activities = db.session.query(
            ActivitiesResearchHotbed,
            ResearchHotbed.name_researchHotbed
        ).join(
            ActivityAuthors,
            ActivitiesResearchHotbed.idactivitiesResearchHotbed == ActivityAuthors.activity_id
        ).join(
            UsersResearchHotbed,
            ActivityAuthors.user_research_hotbed_id == UsersResearchHotbed.idusersResearchHotbed
        ).join(
            ResearchHotbed,
            UsersResearchHotbed.researchHotbed_idresearchHotbed == ResearchHotbed.idresearchHotbed
        ).filter(
            ActivityAuthors.user_research_hotbed_id == user_research_hotbed.idusersResearchHotbed
        ).order_by(
            ActivitiesResearchHotbed.date_activitiesResearchHotbed.desc()
        ).all()

        if not activities:
            return jsonify({"activities": []}), 200

        activities_list = []
        
        for activity_data in activities:
            activity = activity_data[0]
            research_hotbed_name = activity_data[1]

            # Obtener todos los autores y co-autores de esta actividad
            all_authors = db.session.query(
                ActivityAuthors,
                UserClass.name_user
            ).join(
                UsersResearchHotbed,
                ActivityAuthors.user_research_hotbed_id == UsersResearchHotbed.idusersResearchHotbed
            ).join(
                UserClass,
                UsersResearchHotbed.user_iduser == UserClass.iduser
            ).filter(
                ActivityAuthors.activity_id == activity.idactivitiesResearchHotbed
            ).all()

            # Separar autores principales de co-autores
            main_authors = []
            co_authors = []
            
            for author_data in all_authors:
                author_relation = author_data[0]
                author_name = author_data[1]
                
                if author_relation.is_main_author:
                    main_authors.append(author_name)
                else:
                    co_authors.append(author_name)

            # Obtener detalles del proyecto, producto y reconocimiento (código existente)
            project = None
            if activity.projectsResearchHotbed_idprojectsResearchHotbed:
                project = ProjectsResearchHotbed.query.filter_by(
                    idprojectsResearchHotbed=activity.projectsResearchHotbed_idprojectsResearchHotbed
                ).first()

            product = None
            if activity.productsResearchHotbed_idproductsResearchHotbed:
                product = ProductsResearchHotbed.query.filter_by(
                    idproductsResearchHotbed=activity.productsResearchHotbed_idproductsResearchHotbed
                ).first()

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
                "research_hotbed_name": research_hotbed_name,
                "main_authors": main_authors,
                "co_authors": co_authors
            }

            # Agregar detalles adicionales (código existente)
            if project:
                activity_info["project"] = {
                    "name": project.name_projectsResearchHotbed,
                    "reference_number": project.referenceNumber_projectsResearchHotbed,
                    "start_date": project.startDate_projectsResearchHotbed.strftime('%Y-%m-%d'),
                    "end_date": project.endDate_projectsResearchHotbed.strftime('%Y-%m-%d') if project.endDate_projectsResearchHotbed else None,
                    "principal_researcher": project.principalResearcher_projectsResearchHotbed,
                    "co_researchers": project.coResearchers_projectsResearchHotbed
                }

            if product:
                activity_info["product"] = {
                    "category": product.category_productsResearchHotbed,
                    "type": product.type_productsResearchHotbed,
                    "description": product.description_productsResearchHotbed,
                    "date_publication": product.datePublication_productsResearchHotbed.strftime('%Y-%m-%d')
                }

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