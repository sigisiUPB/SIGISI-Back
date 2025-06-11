from flask import jsonify
from models.activities_researchHotbed import ActivitiesResearchHotbed
from models.projects_researchHotbed import ProjectsResearchHotbed
from models.products_researchHotbed import ProductsResearchHotbed
from models.recognitions_researchHotbed import RecognitionsResearchHotbed
from models.users_research_hotbed import UsersResearchHotbed
from models.users import User
from models.activity_authors import ActivityAuthors
from db.connection import db

def get_activities_by_research_hotbed(research_hotbed_id):
    try:
        print(f"DEBUG: Obteniendo actividades para semillero ID: {research_hotbed_id}")
        
        # Obtener todas las actividades del semillero
        activities = db.session.query(ActivitiesResearchHotbed).join(
            UsersResearchHotbed,
            ActivitiesResearchHotbed.usersResearchHotbed_idusersResearchHotbed == UsersResearchHotbed.idusersResearchHotbed
        ).filter(
            UsersResearchHotbed.researchHotbed_idresearchHotbed == research_hotbed_id
        ).all()

        activities_list = []

        for activity in activities:
            print(f"DEBUG: Procesando actividad ID: {activity.idactivitiesResearchHotbed}")
            
            # CRÍTICO: Obtener autores y co-autores SOLO de la tabla activity_authors
            authors_query = db.session.query(
                ActivityAuthors, UsersResearchHotbed, User
            ).join(
                UsersResearchHotbed, ActivityAuthors.user_research_hotbed_id == UsersResearchHotbed.idusersResearchHotbed
            ).join(
                User, UsersResearchHotbed.user_iduser == User.iduser
            ).filter(
                ActivityAuthors.activity_id == activity.idactivitiesResearchHotbed,
                ActivityAuthors.is_main_author == True
            ).all()

            co_authors_query = db.session.query(
                ActivityAuthors, UsersResearchHotbed, User
            ).join(
                UsersResearchHotbed, ActivityAuthors.user_research_hotbed_id == UsersResearchHotbed.idusersResearchHotbed
            ).join(
                User, UsersResearchHotbed.user_iduser == User.iduser
            ).filter(
                ActivityAuthors.activity_id == activity.idactivitiesResearchHotbed,
                ActivityAuthors.is_main_author == False
            ).all()

            # Extraer nombres de autores principales
            main_authors = [user.name_user for _, _, user in authors_query]
            print(f"DEBUG: Autores principales encontrados: {main_authors}")

            # Extraer nombres de co-autores
            co_authors = [user.name_user for _, _, user in co_authors_query]
            print(f"DEBUG: Co-autores encontrados: {co_authors}")

            # Obtener información del semillero
            creator_user = db.session.query(UsersResearchHotbed).filter_by(
                idusersResearchHotbed=activity.usersResearchHotbed_idusersResearchHotbed
            ).first()
            
            research_hotbed_name = ''
            if creator_user:
                from models.research_hotbed import ResearchHotbed
                hotbed = db.session.query(ResearchHotbed).filter_by(
                    idresearchHotbed=creator_user.researchHotbed_idresearchHotbed
                ).first()
                research_hotbed_name = hotbed.name_researchHotbed if hotbed else ''

            # Crear objeto de actividad
            activity_data = {
                'activity_id': activity.idactivitiesResearchHotbed,
                'title': activity.title_activitiesResearchHotbed,
                'responsible': activity.responsible_activitiesResearchHotbed,  # Ya es el primer autor seleccionado
                'date': activity.date_activitiesResearchHotbed.strftime('%Y-%m-%d'),
                'description': activity.description_activitiesResearchHotbed,
                'type': activity.type_activitiesResearchHotbed,
                'start_time': activity.startTime_activitiesResearchHotbed.strftime('%H:%M') if activity.startTime_activitiesResearchHotbed else None,
                'end_time': activity.endTime_activitiesResearchHotbed.strftime('%H:%M') if activity.endTime_activitiesResearchHotbed else None,
                'duration': activity.duration_activitiesResearchHotbed,
                'approved_free_hours': bool(activity.approvedFreeHours_activitiesResearchHotbed),
                'semester': activity.semester,
                'research_hotbed_name': research_hotbed_name,
                'main_authors': main_authors,  # Solo los de activity_authors
                'co_authors': co_authors       # Solo los de activity_authors
            }

            # Agregar información adicional según el tipo
            if activity.projectsResearchHotbed_idprojectsResearchHotbed:
                project = db.session.query(ProjectsResearchHotbed).filter_by(
                    idprojectsResearchHotbed=activity.projectsResearchHotbed_idprojectsResearchHotbed
                ).first()
                if project:
                    activity_data['project'] = {
                        'name': project.name_projectsResearchHotbed,
                        'reference_number': project.referenceNumber_projectsResearchHotbed,
                        'start_date': project.startDate_projectsResearchHotbed.strftime('%Y-%m-%d'),
                        'end_date': project.endDate_projectsResearchHotbed.strftime('%Y-%m-%d') if project.endDate_projectsResearchHotbed else None,
                        'principal_researcher': project.principalResearcher_projectsResearchHotbed
                    }

            if activity.productsResearchHotbed_idproductsResearchHotbed:
                product = db.session.query(ProductsResearchHotbed).filter_by(
                    idproductsResearchHotbed=activity.productsResearchHotbed_idproductsResearchHotbed
                ).first()
                if product:
                    activity_data['product'] = {
                        'category': product.category_productsResearchHotbed,
                        'type': product.type_productsResearchHotbed,
                        'description': product.description_productsResearchHotbed,
                        'date_publication': product.datePublication_productsResearchHotbed.strftime('%Y-%m-%d') if product.datePublication_productsResearchHotbed else None
                    }

            if activity.recognitionsResearchHotbed_idrecognitionsResearchHotbed:
                recognition = db.session.query(RecognitionsResearchHotbed).filter_by(
                    idrecognitionsResearchHotbed=activity.recognitionsResearchHotbed_idrecognitionsResearchHotbed
                ).first()
                if recognition:
                    activity_data['recognition'] = {
                        'name': recognition.name_recognitionsResearchHotbed,
                        'project_name': recognition.projectName_recognitionsResearchHotbed,
                        'participants_names': recognition.participantsNames_recognitionsResearchHotbed,
                        'organization_name': recognition.organizationName_recognitionsResearchHotbed
                    }

            activities_list.append(activity_data)

        print(f"DEBUG: Total actividades procesadas: {len(activities_list)}")
        
        return jsonify({
            'activities': activities_list,
            'total_count': len(activities_list)
        }), 200

    except Exception as e:
        print(f"ERROR en get_activities_by_research_hotbed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500