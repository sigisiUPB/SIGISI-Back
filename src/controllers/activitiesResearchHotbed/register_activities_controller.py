from datetime import datetime
from flask import jsonify
from models.projects_researchHotbed import ProjectsResearchHotbed
from models.products_researchHotbed import ProductsResearchHotbed
from models.recognitions_researchHotbed import RecognitionsResearchHotbed
from models.activities_researchHotbed import ActivitiesResearchHotbed
from models.activity_authors import ActivityAuthors
from models.users_research_hotbed import UsersResearchHotbed
from utils.semester_utils import get_current_semester
from db.connection import db

def register_activity(data):
    try:
        # Validar que se hayan proporcionado autores
        authors_ids = data.get('authors_ids', [])
        co_authors_ids = data.get('co_authors_ids', [])
        
        if not authors_ids:
            return jsonify({"error": "Debe especificar al menos un autor principal"}), 400

        # Validar que los usuarios pertenezcan al semillero
        all_user_ids = authors_ids + co_authors_ids
        valid_users = UsersResearchHotbed.query.filter(
            UsersResearchHotbed.user_iduser.in_(all_user_ids)
        ).all()
        
        valid_user_ids = [user.user_iduser for user in valid_users]
        
        # Verificar que todos los usuarios sean válidos
        for user_id in all_user_ids:
            if user_id not in valid_user_ids:
                return jsonify({"error": f"El usuario con ID {user_id} no pertenece a ningún semillero"}), 400

        # Obtener el semestre (puede venir del frontend o calcularlo automáticamente)
        semester = data.get('semester', get_current_semester())

        # Registrar el proyecto si se incluye en los datos
        project_id = None
        if 'project' in data and data['project']:
            project_data = data['project']
            co_researchers = project_data.get('co_researchers', '')
            if co_researchers:
                co_researchers = ', '.join([name.strip() for name in co_researchers.split(',')])
                
            project = ProjectsResearchHotbed(
                name_projectsResearchHotbed=project_data['name'],
                referenceNumber_projectsResearchHotbed=project_data['reference_number'],
                startDate_projectsResearchHotbed=datetime.strptime(project_data['start_date'], '%Y-%m-%d'),
                endDate_projectsResearchHotbed=datetime.strptime(project_data['end_date'], '%Y-%m-%d') if project_data.get('end_date') else None,
                principalResearcher_projectsResearchHotbed=project_data['principal_researcher'],
                coResearchers_projectsResearchHotbed=co_researchers
            )
            db.session.add(project)
            db.session.flush()
            project_id = project.idprojectsResearchHotbed

        # Registrar el producto si se incluye en los datos
        product_id = None
        if 'product' in data and data['product']:
            product_data = data['product']
            product = ProductsResearchHotbed(
                category_productsResearchHotbed=product_data['category'],
                type_productsResearchHotbed=product_data['type'],
                description_productsResearchHotbed=product_data['description'],
                datePublication_productsResearchHotbed=datetime.strptime(product_data['date_publication'], '%Y-%m-%d')
            )
            db.session.add(product)
            db.session.flush()
            product_id = product.idproductsResearchHotbed

        # Registrar el reconocimiento si se incluye en los datos
        recognition_id = None
        if 'recognition' in data and data['recognition']:
            recognition_data = data['recognition']
            recognition = RecognitionsResearchHotbed(
                name_recognitionsResearchHotbed=recognition_data['name'],
                projectName_recognitionsResearchHotbed=recognition_data['project_name'],
                participantsNames_recognitionsResearchHotbed=recognition_data['participants_names'],
                organizationName_recognitionsResearchHotbed=recognition_data['organization_name']
            )
            db.session.add(recognition)
            db.session.flush()
            recognition_id = recognition.idrecognitionsResearchHotbed

        # Obtener el usersResearchHotbed del primer autor
        main_author_research_hotbed = UsersResearchHotbed.query.filter_by(
            user_iduser=authors_ids[0]
        ).first()
        
        if not main_author_research_hotbed:
            return jsonify({"error": "El autor principal no pertenece a ningún semillero"}), 400

        # Registrar la actividad
        activity = ActivitiesResearchHotbed(
            title_activitiesResearchHotbed=data['title'],
            responsible_activitiesResearchHotbed=data['responsible'],
            date_activitiesResearchHotbed=datetime.strptime(data['date'], '%Y-%m-%d'),
            description_activitiesResearchHotbed=data['description'],
            type_activitiesResearchHotbed=data['type'],
            startTime_activitiesResearchHotbed=datetime.strptime(data['start_time'], '%H:%M').time() if data.get('start_time') else None,
            endTime_activitiesResearchHotbed=datetime.strptime(data['end_time'], '%H:%M').time() if data.get('end_time') else None,
            duration_activitiesResearchHotbed=data.get('duration'),
            approvedFreeHours_activitiesResearchHotbed=data.get('approved_free_hours'),
            semester=semester,
            usersResearchHotbed_idusersResearchHotbed=main_author_research_hotbed.idusersResearchHotbed,
            projectsResearchHotbed_idprojectsResearchHotbed=project_id,
            productsResearchHotbed_idproductsResearchHotbed=product_id,
            recognitionsResearchHotbed_idrecognitionsResearchHotbed=recognition_id
        )

        db.session.add(activity)
        db.session.flush()

        # Crear las relaciones de autoría
        # Agregar autores principales
        for author_id in authors_ids:
            author_research_hotbed = UsersResearchHotbed.query.filter_by(
                user_iduser=author_id
            ).first()
            
            if author_research_hotbed:
                activity_author = ActivityAuthors(
                    activity_id=activity.idactivitiesResearchHotbed,
                    user_research_hotbed_id=author_research_hotbed.idusersResearchHotbed,
                    is_main_author=True
                )
                db.session.add(activity_author)

        # Agregar co-autores
        for co_author_id in co_authors_ids:
            co_author_research_hotbed = UsersResearchHotbed.query.filter_by(
                user_iduser=co_author_id
            ).first()
            
            if co_author_research_hotbed:
                activity_author = ActivityAuthors(
                    activity_id=activity.idactivitiesResearchHotbed,
                    user_research_hotbed_id=co_author_research_hotbed.idusersResearchHotbed,
                    is_main_author=False
                )
                db.session.add(activity_author)

        db.session.commit()

        return jsonify({
            "message": "Actividad registrada exitosamente",
            "activity_id": activity.idactivitiesResearchHotbed,
            "semester": semester,
            "authors_count": len(authors_ids),
            "co_authors_count": len(co_authors_ids)
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error en register_activity: {str(e)}")
        return jsonify({"error": str(e)}), 500