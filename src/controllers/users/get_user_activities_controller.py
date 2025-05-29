from flask import jsonify
from db.connection import db
from models.activities_researchHotbed import ActivitiesResearchHotbed
from models.users_research_hotbed import UsersResearchHotbed
from models.users import User
from models.activity_authors import ActivityAuthors
from models.research_hotbed import ResearchHotbed

def get_user_activities(user_id):
    try:
        # Obtener actividades donde el usuario es responsable directo
        direct_activities = db.session.query(ActivitiesResearchHotbed)\
            .join(UsersResearchHotbed, ActivitiesResearchHotbed.usersResearchHotbed_idusersResearchHotbed == UsersResearchHotbed.idusersResearchHotbed)\
            .filter(UsersResearchHotbed.user_iduser == user_id)\
            .all()

        # Obtener actividades donde el usuario es autor principal o co-autor
        authored_activities = db.session.query(ActivitiesResearchHotbed)\
            .join(ActivityAuthors, ActivitiesResearchHotbed.idactivitiesResearchHotbed == ActivityAuthors.activity_id)\
            .join(UsersResearchHotbed, ActivityAuthors.user_research_hotbed_id == UsersResearchHotbed.idusersResearchHotbed)\
            .filter(UsersResearchHotbed.user_iduser == user_id)\
            .all()

        # Combinar y eliminar duplicados
        activity_ids = set()
        unique_activities = []
        
        for activity in direct_activities + authored_activities:
            if activity.idactivitiesResearchHotbed not in activity_ids:
                activity_ids.add(activity.idactivitiesResearchHotbed)
                unique_activities.append(activity)
        
        # Ordenar por fecha (más recientes primero)
        unique_activities.sort(key=lambda x: x.date_activitiesResearchHotbed if x.date_activitiesResearchHotbed else '', reverse=True)

        if not unique_activities:
            return jsonify({"activities": []}), 200

        activities_list = []
        
        for activity in unique_activities:
            # Obtener el usuario responsable
            user_research_hotbed = db.session.query(UsersResearchHotbed)\
                .filter_by(idusersResearchHotbed=activity.usersResearchHotbed_idusersResearchHotbed)\
                .first()
            
            responsible = "Usuario no encontrado"
            research_hotbed_name = "Semillero no encontrado"
            
            if user_research_hotbed:
                user = db.session.query(User)\
                    .filter_by(iduser=user_research_hotbed.user_iduser)\
                    .first()
                if user:
                    responsible = user.name_user
                
                # Obtener nombre del semillero
                research_hotbed = db.session.query(ResearchHotbed)\
                    .filter_by(idresearchHotbed=user_research_hotbed.researchHotbed_idresearchHotbed)\
                    .first()
                if research_hotbed:
                    research_hotbed_name = research_hotbed.name_researchHotbed

            # Obtener autores principales y co-autores
            main_authors = []
            co_authors = []
            user_role = "Responsable"  # Rol por defecto
            
            # Buscar autores en la tabla ActivityAuthors
            activity_authors = db.session.query(ActivityAuthors)\
                .filter_by(activity_id=activity.idactivitiesResearchHotbed)\
                .all()
            
            for author_relation in activity_authors:
                author_user_research_hotbed = db.session.query(UsersResearchHotbed)\
                    .filter_by(idusersResearchHotbed=author_relation.user_research_hotbed_id)\
                    .first()
                
                if author_user_research_hotbed:
                    author_user = db.session.query(User)\
                        .filter_by(iduser=author_user_research_hotbed.user_iduser)\
                        .first()
                    
                    if author_user:
                        author_name = author_user.name_user
                        if author_relation.is_main_author:
                            main_authors.append(author_name)
                            # Si este usuario es autor principal
                            if author_user.iduser == user_id:
                                user_role = "Autor Principal"
                        else:
                            co_authors.append(author_name)
                            # Si este usuario es co-autor
                            if author_user.iduser == user_id:
                                user_role = "Co-autor"

            # Si el usuario es el responsable directo pero no aparece en ActivityAuthors
            current_user = db.session.query(User).filter_by(iduser=user_id).first()
            if current_user and user_research_hotbed and user_research_hotbed.user_iduser == user_id:
                if user_role == "Responsable":  # Solo si no se encontró otro rol
                    user_role = "Responsable"

            activity_data = {
                "activity_id": activity.idactivitiesResearchHotbed,
                "title": activity.title_activitiesResearchHotbed,
                "responsible": responsible,
                "date": activity.date_activitiesResearchHotbed.isoformat() if activity.date_activitiesResearchHotbed else None,
                "description": activity.description_activitiesResearchHotbed,
                "type": activity.type_activitiesResearchHotbed,
                "start_time": activity.startTime_activitiesResearchHotbed.strftime('%H:%M') if activity.startTime_activitiesResearchHotbed else None,
                "end_time": activity.endTime_activitiesResearchHotbed.strftime('%H:%M') if activity.endTime_activitiesResearchHotbed else None,
                "duration": activity.duration_activitiesResearchHotbed,
                "approved_free_hours": activity.approvedFreeHours_activitiesResearchHotbed,
                "main_authors": main_authors,
                "co_authors": co_authors,
                "research_hotbed_name": research_hotbed_name,
                "user_role": user_role  # Nuevo campo para indicar el rol del usuario en esta actividad
            }

            # Obtener datos relacionados según el tipo (proyecto, producto, reconocimiento)
            if activity.type_activitiesResearchHotbed and activity.type_activitiesResearchHotbed.lower() == 'proyecto' and activity.projectsResearchHotbed_idprojectsResearchHotbed:
                try:
                    from models.projects_researchHotbed import ProjectsResearchHotbed
                    project = db.session.query(ProjectsResearchHotbed)\
                        .filter_by(idprojectsResearchHotbed=activity.projectsResearchHotbed_idprojectsResearchHotbed)\
                        .first()
                    if project:
                        activity_data["project"] = {
                            "name": getattr(project, 'name_projectsResearchHotbed', ''),
                            "reference_number": getattr(project, 'referenceNumber_projectsResearchHotbed', ''),
                            "start_date": project.startDate_projectsResearchHotbed.isoformat() if hasattr(project, 'startDate_projectsResearchHotbed') and project.startDate_projectsResearchHotbed else None,
                            "end_date": project.endDate_projectsResearchHotbed.isoformat() if hasattr(project, 'endDate_projectsResearchHotbed') and project.endDate_projectsResearchHotbed else None,
                            "principal_researcher": getattr(project, 'principalResearcher_projectsResearchHotbed', ''),
                            "co_researchers": getattr(project, 'coResearchers_projectsResearchHotbed', '')
                        }
                except Exception as e:
                    print(f"Error loading project data: {e}")

            if activity.type_activitiesResearchHotbed and activity.type_activitiesResearchHotbed.lower() == 'producto' and activity.productsResearchHotbed_idproductsResearchHotbed:
                try:
                    from models.products_researchHotbed import ProductsResearchHotbed
                    product = db.session.query(ProductsResearchHotbed)\
                        .filter_by(idproductsResearchHotbed=activity.productsResearchHotbed_idproductsResearchHotbed)\
                        .first()
                    if product:
                        activity_data["product"] = {
                            "category": getattr(product, 'category_productsResearchHotbed', ''),
                            "type": getattr(product, 'type_productsResearchHotbed', ''),
                            "description": getattr(product, 'description_productsResearchHotbed', ''),
                            "date_publication": product.datePublication_productsResearchHotbed.isoformat() if hasattr(product, 'datePublication_productsResearchHotbed') and product.datePublication_productsResearchHotbed else None
                        }
                except Exception as e:
                    print(f"Error loading product data: {e}")

            if activity.type_activitiesResearchHotbed and activity.type_activitiesResearchHotbed.lower() == 'reconocimiento' and activity.recognitionsResearchHotbed_idrecognitionsResearchHotbed:
                try:
                    from models.recognitions_researchHotbed import RecognitionsResearchHotbed
                    recognition = db.session.query(RecognitionsResearchHotbed)\
                        .filter_by(idrecognitionsResearchHotbed=activity.recognitionsResearchHotbed_idrecognitionsResearchHotbed)\
                        .first()
                    if recognition:
                        activity_data["recognition"] = {
                            "name": getattr(recognition, 'name_recognitionsResearchHotbed', ''),
                            "project_name": getattr(recognition, 'projectName_recognitionsResearchHotbed', ''),
                            "participants_names": getattr(recognition, 'participantsNames_recognitionsResearchHotbed', ''),
                            "organization_name": getattr(recognition, 'organizationName_recognitionsResearchHotbed', '')
                        }
                except Exception as e:
                    print(f"Error loading recognition data: {e}")

            activities_list.append(activity_data)

        return jsonify({"activities": activities_list}), 200

    except Exception as e:
        print(f"Error en get_user_activities: {str(e)}")
        return jsonify({"error": "Error interno del servidor", "details": str(e)}), 500