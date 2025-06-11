from flask import jsonify
from datetime import datetime
from models.activities_researchHotbed import ActivitiesResearchHotbed
from models.projects_researchHotbed import ProjectsResearchHotbed
from models.products_researchHotbed import ProductsResearchHotbed
from models.recognitions_researchHotbed import RecognitionsResearchHotbed
from models.activity_authors import ActivityAuthors
from models.users_research_hotbed import UsersResearchHotbed
from models.users import User
from db.connection import db

def register_activity(data):
    try:
        print(f"=== DEBUG REGISTER ACTIVITY ===")
        print(f"Datos completos recibidos: {data}")
        
        # Validaciones básicas
        if not data.get('title') or not data.get('date') or not data.get('description'):
            return jsonify({"error": "Faltan campos obligatorios"}), 400

        if not data.get('userResearchHotbedId'):
            return jsonify({"error": "ID de usuario en semillero requerido"}), 400

        if not data.get('authors_ids') or len(data.get('authors_ids', [])) == 0:
            return jsonify({"error": "Debe especificar al menos un autor"}), 400

        # Validar que todos los autores existan
        all_user_ids = data.get('authors_ids', []) + data.get('co_authors_ids', [])
        
        for user_id in all_user_ids:
            user_exists = db.session.query(UsersResearchHotbed).filter_by(idusersResearchHotbed=user_id).first()
            if not user_exists:
                return jsonify({"error": f"El usuario con ID {user_id} no existe en el semillero"}), 400

        # IDs para relaciones
        project_id = None
        product_id = None
        recognition_id = None

        # Procesar según el tipo de actividad
        activity_type = data.get('type', '').lower()

        # Crear proyecto si es necesario
        if activity_type == 'proyecto' and data.get('project'):
            project_data = data['project']
            
            # Usar el primer autor seleccionado como investigador principal
            principal_researcher = ''
            if data.get('authors_ids'):
                first_author_urh = db.session.query(UsersResearchHotbed).filter_by(idusersResearchHotbed=data.get('authors_ids')[0]).first()
                if first_author_urh:
                    user_info = db.session.query(User).filter_by(iduser=first_author_urh.user_iduser).first()
                    principal_researcher = user_info.name_user if user_info else 'Primer autor'
            
            new_project = ProjectsResearchHotbed(
                name_projectsResearchHotbed=project_data.get('name', ''),
                referenceNumber_projectsResearchHotbed=project_data.get('reference_number', ''),
                startDate_projectsResearchHotbed=datetime.strptime(project_data.get('start_date'), '%Y-%m-%d').date(),
                endDate_projectsResearchHotbed=datetime.strptime(project_data.get('end_date'), '%Y-%m-%d').date() if project_data.get('end_date') else None,
                principalResearcher_projectsResearchHotbed=principal_researcher
            )
            
            db.session.add(new_project)
            db.session.flush()
            project_id = new_project.idprojectsResearchHotbed

        elif activity_type == 'producto' and data.get('product'):
            product_data = data['product']
            
            new_product = ProductsResearchHotbed(
                category_productsResearchHotbed=product_data.get('category', ''),
                type_productsResearchHotbed=product_data.get('type', ''),
                description_productsResearchHotbed=product_data.get('description', ''),
                datePublication_productsResearchHotbed=datetime.strptime(product_data.get('date_publication'), '%Y-%m-%d').date() if product_data.get('date_publication') else None
            )
            
            db.session.add(new_product)
            db.session.flush()
            product_id = new_product.idproductsResearchHotbed

        elif activity_type == 'reconocimiento' and data.get('recognition'):
            recognition_data = data['recognition']
            
            # Auto-completar participantes con autores y co-autores
            participants = []
            
            # Agregar autores principales
            for author_id in data.get('authors_ids', []):
                author_urh = db.session.query(UsersResearchHotbed).filter_by(idusersResearchHotbed=author_id).first()
                if author_urh:
                    user_info = db.session.query(User).filter_by(iduser=author_urh.user_iduser).first()
                    if user_info:
                        participants.append(user_info.name_user)
            
            # Agregar co-autores
            for co_author_id in data.get('co_authors_ids', []):
                co_author_urh = db.session.query(UsersResearchHotbed).filter_by(idusersResearchHotbed=co_author_id).first()
                if co_author_urh:
                    user_info = db.session.query(User).filter_by(iduser=co_author_urh.user_iduser).first()
                    if user_info:
                        participants.append(user_info.name_user)
            
            participants_names = ', '.join(participants) if participants else ''
            
            new_recognition = RecognitionsResearchHotbed(
                name_recognitionsResearchHotbed=recognition_data.get('name', ''),
                projectName_recognitionsResearchHotbed=recognition_data.get('project_name', ''),
                participantsNames_recognitionsResearchHotbed=participants_names,
                organizationName_recognitionsResearchHotbed=recognition_data.get('organization_name', '')
            )
            
            db.session.add(new_recognition)
            db.session.flush()
            recognition_id = new_recognition.idrecognitionsResearchHotbed

        # Obtener el nombre del responsable (primer autor seleccionado)
        responsible_name = data.get('responsible', '')
        if not responsible_name and data.get('authors_ids'):
            first_author_urh = db.session.query(UsersResearchHotbed).filter_by(idusersResearchHotbed=data.get('authors_ids')[0]).first()
            if first_author_urh:
                user_info = db.session.query(User).filter_by(iduser=first_author_urh.user_iduser).first()
                responsible_name = user_info.name_user if user_info else 'Autor principal'

        # CLAVE: Crear la actividad con el usuario creador SOLO para tracking, NO para autoría
        activity = ActivitiesResearchHotbed(
            title_activitiesResearchHotbed=data['title'],
            responsible_activitiesResearchHotbed=responsible_name,  # Primer autor seleccionado
            date_activitiesResearchHotbed=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            description_activitiesResearchHotbed=data['description'],
            type_activitiesResearchHotbed=data.get('type', 'actividad'),
            startTime_activitiesResearchHotbed=datetime.strptime(data['start_time'], '%H:%M').time() if data.get('start_time') else None,
            endTime_activitiesResearchHotbed=datetime.strptime(data['end_time'], '%H:%M').time() if data.get('end_time') else None,
            duration_activitiesResearchHotbed=data.get('duration'),
            approvedFreeHours_activitiesResearchHotbed=1.0 if data.get('approved_free_hours') else 0.0,
            semester=data.get('semester', 'semestre-1-2025'),
            usersResearchHotbed_idusersResearchHotbed=data['userResearchHotbedId'],  # Solo para tracking/creación
            projectsResearchHotbed_idprojectsResearchHotbed=project_id,
            productsResearchHotbed_idproductsResearchHotbed=product_id,
            recognitionsResearchHotbed_idrecognitionsResearchHotbed=recognition_id
        )

        db.session.add(activity)
        db.session.flush()

        print(f"DEBUG: Actividad creada con ID: {activity.idactivitiesResearchHotbed}")
        print(f"DEBUG: Responsable asignado: {responsible_name}")
        print(f"DEBUG: Usuario creador (tracking): {data['userResearchHotbedId']}")
        print(f"DEBUG: Autores a registrar: {data.get('authors_ids', [])}")
        print(f"DEBUG: Co-autores a registrar: {data.get('co_authors_ids', [])}")

        # CRÍTICO: Solo crear relaciones de autoría para los usuarios seleccionados
        # NO agregar automáticamente al usuario creador

        # Crear relaciones de autoría para autores principales
        for author_id in data.get('authors_ids', []):
            print(f"DEBUG: Agregando autor principal ID: {author_id}")
            author_relation = ActivityAuthors(
                activity_id=activity.idactivitiesResearchHotbed,
                user_research_hotbed_id=author_id,
                is_main_author=True
            )
            db.session.add(author_relation)

        # Crear relaciones de autoría para co-autores
        for co_author_id in data.get('co_authors_ids', []):
            print(f"DEBUG: Agregando co-autor ID: {co_author_id}")
            co_author_relation = ActivityAuthors(
                activity_id=activity.idactivitiesResearchHotbed,
                user_research_hotbed_id=co_author_id,
                is_main_author=False
            )
            db.session.add(co_author_relation)

        db.session.commit()

        print(f"DEBUG: Actividad registrada exitosamente")

        return jsonify({
            "message": "Actividad registrada exitosamente",
            "activity_id": activity.idactivitiesResearchHotbed
        }), 201

    except ValueError as ve:
        db.session.rollback()
        print(f"ERROR ValueError: {str(ve)}")
        return jsonify({"error": f"Error en formato de fecha: {str(ve)}"}), 400
    except Exception as e:
        db.session.rollback()
        print(f"ERROR Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500