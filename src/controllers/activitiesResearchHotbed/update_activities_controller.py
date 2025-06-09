from flask import jsonify
from models.activities_researchHotbed import ActivitiesResearchHotbed
from models.projects_researchHotbed import ProjectsResearchHotbed
from models.products_researchHotbed import ProductsResearchHotbed
from models.recognitions_researchHotbed import RecognitionsResearchHotbed
from models.users import User
from models.users_research_hotbed import UsersResearchHotbed
from models.activity_authors import ActivityAuthors  # MOVIDO AQUÍ
from db.connection import db
from datetime import datetime

def update_activity(activity_id, data):
    try:
        # Buscar la actividad existente
        activity = ActivitiesResearchHotbed.query.get(activity_id)
        if not activity:
            return jsonify({"message": "Actividad no encontrada"}), 404

        # Actualizar campos de la actividad
        activity.title_activitiesResearchHotbed = data.get('title', activity.title_activitiesResearchHotbed)
        activity.responsible_activitiesResearchHotbed = data.get('responsible', activity.responsible_activitiesResearchHotbed)
        activity.date_activitiesResearchHotbed = datetime.strptime(data['date'], '%Y-%m-%d') if data.get('date') else activity.date_activitiesResearchHotbed
        activity.description_activitiesResearchHotbed = data.get('description', activity.description_activitiesResearchHotbed)
        activity.type_activitiesResearchHotbed = data.get('type', activity.type_activitiesResearchHotbed)
        activity.startTime_activitiesResearchHotbed = datetime.strptime(data['start_time'], '%H:%M').time() if data.get('start_time') else activity.startTime_activitiesResearchHotbed
        activity.endTime_activitiesResearchHotbed = datetime.strptime(data['end_time'], '%H:%M').time() if data.get('end_time') else activity.endTime_activitiesResearchHotbed
        activity.duration_activitiesResearchHotbed = data.get('duration', activity.duration_activitiesResearchHotbed)
        activity.approvedFreeHours_activitiesResearchHotbed = data.get('approved_free_hours', activity.approvedFreeHours_activitiesResearchHotbed)
        
        # Actualizar el semestre si se proporciona
        if 'semester' in data:
            activity.semester = data['semester']

        # Actualizar autores y co-autores si se proporcionan
        if 'authors_ids' in data or 'co_authors_ids' in data:
            # Eliminar todas las relaciones de autoría existentes
            ActivityAuthors.query.filter_by(activity_id=activity.idactivitiesResearchHotbed).delete()
            
            # Validar que todos los autores existan
            all_user_ids = data.get('authors_ids', []) + data.get('co_authors_ids', [])
            for user_id in all_user_ids:
                user_exists = db.session.query(UsersResearchHotbed).filter_by(idusersResearchHotbed=user_id).first()
                if not user_exists:
                    return jsonify({"error": f"El usuario con ID {user_id} no existe en el semillero"}), 400
            
            # Crear nuevas relaciones de autoría para autores principales
            for author_id in data.get('authors_ids', []):
                author_relation = ActivityAuthors(
                    activity_id=activity.idactivitiesResearchHotbed,
                    user_research_hotbed_id=author_id,
                    is_main_author=True
                )
                db.session.add(author_relation)

            # Crear nuevas relaciones de autoría para co-autores
            for co_author_id in data.get('co_authors_ids', []):
                co_author_relation = ActivityAuthors(
                    activity_id=activity.idactivitiesResearchHotbed,
                    user_research_hotbed_id=co_author_id,
                    is_main_author=False
                )
                db.session.add(co_author_relation)
            
            # Actualizar el responsable con el primer autor principal
            if data.get('authors_ids'):
                first_author_urh = db.session.query(UsersResearchHotbed).filter_by(idusersResearchHotbed=data.get('authors_ids')[0]).first()
                if first_author_urh:
                    user_info = db.session.query(User).filter_by(iduser=first_author_urh.user_iduser).first()
                    if user_info:
                        activity.responsible_activitiesResearchHotbed = user_info.name_user

        # Si hay un proyecto asociado para actualizar o crear
        if 'project' in data:
            if activity.projectsResearchHotbed_idprojectsResearchHotbed:
                project = ProjectsResearchHotbed.query.get(activity.projectsResearchHotbed_idprojectsResearchHotbed)
            else:
                project = ProjectsResearchHotbed()
                db.session.add(project)
                db.session.flush()
                activity.projectsResearchHotbed_idprojectsResearchHotbed = project.idprojectsResearchHotbed

            # Actualizar todos los campos incluyendo name
            project.name_projectsResearchHotbed = data['project'].get('name', getattr(project, 'name_projectsResearchHotbed', ''))
            project.referenceNumber_projectsResearchHotbed = data['project'].get('reference_number', project.referenceNumber_projectsResearchHotbed)
            if data['project'].get('start_date'):
                project.startDate_projectsResearchHotbed = datetime.strptime(data['project']['start_date'], '%Y-%m-%d')
            if data['project'].get('end_date'):
                project.endDate_projectsResearchHotbed = datetime.strptime(data['project']['end_date'], '%Y-%m-%d')
            project.principalResearcher_projectsResearchHotbed = data['project'].get('principal_researcher', project.principalResearcher_projectsResearchHotbed)

        # Si hay un producto asociado
        if 'product' in data:
            if activity.productsResearchHotbed_idproductsResearchHotbed:
                product = ProductsResearchHotbed.query.get(activity.productsResearchHotbed_idproductsResearchHotbed)
            else:
                product = ProductsResearchHotbed()
                db.session.add(product)
                db.session.flush()
                activity.productsResearchHotbed_idproductsResearchHotbed = product.idproductsResearchHotbed

            product.category_productsResearchHotbed = data['product'].get('category', product.category_productsResearchHotbed)
            product.type_productsResearchHotbed = data['product'].get('type', product.type_productsResearchHotbed)
            product.description_productsResearchHotbed = data['product'].get('description', product.description_productsResearchHotbed)
            # Actualizar fecha de publicación
            if data['product'].get('date_publication'):
                product.datePublication_productsResearchHotbed = datetime.strptime(data['product']['date_publication'], '%Y-%m-%d')

        # Si hay un reconocimiento asociado
        if 'recognition' in data:
            if activity.recognitionsResearchHotbed_idrecognitionsResearchHotbed:
                recognition = RecognitionsResearchHotbed.query.get(activity.recognitionsResearchHotbed_idrecognitionsResearchHotbed)
            else:
                recognition = RecognitionsResearchHotbed()
                db.session.add(recognition)
                db.session.flush()
                activity.recognitionsResearchHotbed_idrecognitionsResearchHotbed = recognition.idrecognitionsResearchHotbed

            # Actualizar campos del reconocimiento
            recognition.name_recognitionsResearchHotbed = data['recognition'].get('name', getattr(recognition, 'name_recognitionsResearchHotbed', ''))
            recognition.projectName_recognitionsResearchHotbed = data['recognition'].get('project_name', recognition.projectName_recognitionsResearchHotbed)
            recognition.organizationName_recognitionsResearchHotbed = data['recognition'].get('organization_name', recognition.organizationName_recognitionsResearchHotbed)
            
            # AUTO-COMPLETAR participantes con autores actuales (si no se proporciona explícitamente)
            if 'participants_names' not in data['recognition']:
                # Obtener autores actuales de la actividad
                participants = []
                
                activity_authors = db.session.query(ActivityAuthors)\
                    .filter_by(activity_id=activity.idactivitiesResearchHotbed)\
                    .all()
                
                for author_relation in activity_authors:
                    author_urh = db.session.query(UsersResearchHotbed)\
                        .filter_by(idusersResearchHotbed=author_relation.user_research_hotbed_id)\
                        .first()
                    if author_urh:
                        user_info = db.session.query(User).filter_by(iduser=author_urh.user_iduser).first()
                        if user_info:
                            participants.append(user_info.name_user)
                
                recognition.participantsNames_recognitionsResearchHotbed = ', '.join(participants) if participants else ''
            else:
                recognition.participantsNames_recognitionsResearchHotbed = data['recognition']['participants_names']

        db.session.commit()

        return jsonify({"message": "Actividad actualizada correctamente"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error en update_activity: {str(e)}")
        return jsonify({"error": str(e)}), 500
