from flask import jsonify
from datetime import datetime
from models.activities_researchHotbed import ActivitiesResearchHotbed
from models.projects_researchHotbed import ProjectsResearchHotbed
from models.products_researchHotbed import ProductsResearchHotbed
from models.recognitions_researchHotbed import RecognitionsResearchHotbed
from models.activity_authors import ActivityAuthors
from models.users_research_hotbed import UsersResearchHotbed  # Corregir el nombre del import
from models.users import User  # También importar User para obtener nombres
from db.connection import db

def register_activity(data):
    try:
        print(f"=== DEBUG REGISTER ACTIVITY ===")
        print(f"Datos completos recibidos: {data}")
        print(f"Authors IDs: {data.get('authors_ids', [])}")
        print(f"Co-authors IDs: {data.get('co_authors_ids', [])}")
        print(f"UserResearchHotbedId: {data.get('userResearchHotbedId')}")
        
        # Validaciones básicas
        if not data.get('title') or not data.get('date') or not data.get('description'):
            return jsonify({"error": "Faltan campos obligatorios"}), 400

        if not data.get('userResearchHotbedId'):
            return jsonify({"error": "ID de usuario en semillero requerido"}), 400

        if not data.get('authors_ids') or len(data.get('authors_ids', [])) == 0:
            return jsonify({"error": "Debe especificar al menos un autor"}), 400

        # Validar que todos los autores existan en la base de datos
        all_user_ids = data.get('authors_ids', []) + data.get('co_authors_ids', [])
        print(f"Validando usuarios: {all_user_ids}")  # Debug
        
        # Consultar todos los usuarios disponibles en la BD para debug
        all_users_in_db = db.session.query(UsersResearchHotbed).all()
        print(f"Usuarios disponibles en BD:")
        for user in all_users_in_db:
            print(f"  - ID: {user.idusersResearchHotbed}, Status: {user.status_usersResearchHotbed}")
        
        for user_id in all_user_ids:
            user_exists = db.session.query(UsersResearchHotbed).filter_by(idusersResearchHotbed=user_id).first()
            if not user_exists:
                print(f"Usuario no encontrado: {user_id}")  # Debug
                return jsonify({"error": f"El usuario con ID {user_id} no existe en el semillero"}), 400
            print(f"Usuario {user_id} encontrado: {user_exists.idusersResearchHotbed}")  # Debug

        # Validar que el userResearchHotbedId también exista
        main_user = db.session.query(UsersResearchHotbed).filter_by(idusersResearchHotbed=data['userResearchHotbedId']).first()
        if not main_user:
            return jsonify({"error": f"El usuario principal con ID {data['userResearchHotbedId']} no existe"}), 400

        # IDs para relaciones
        project_id = None
        product_id = None
        recognition_id = None

        # Procesar según el tipo de actividad
        activity_type = data.get('type', '').lower()

        # Crear proyecto si es necesario
        if activity_type == 'proyecto' and data.get('project'):
            project_data = data['project']
            
            # Usar automáticamente el responsable como investigador principal
            principal_researcher = data.get('responsible', '')
            if not principal_researcher and data.get('authors_ids'):
                # Obtener el nombre del primer autor
                first_author_urh = db.session.query(UsersResearchHotbed).filter_by(idusersResearchHotbed=data.get('authors_ids')[0]).first()
                if first_author_urh:
                    # Obtener el nombre del usuario desde la tabla user
                    user_info = db.session.query(User).filter_by(iduser=first_author_urh.user_iduser).first()
                    principal_researcher = user_info.name_user if user_info else 'Primer autor'
                else:
                    principal_researcher = 'Primer autor seleccionado'
            
            new_project = ProjectsResearchHotbed(
                referenceNumber_projectsResearchHotbed=project_data.get('reference_number', ''),
                startDate_projectsResearchHotbed=datetime.strptime(project_data.get('start_date'), '%Y-%m-%d').date(),
                endDate_projectsResearchHotbed=datetime.strptime(project_data.get('end_date'), '%Y-%m-%d').date() if project_data.get('end_date') else None,
                principalResearcher_projectsResearchHotbed=principal_researcher
            )
            
            db.session.add(new_project)
            db.session.flush()
            project_id = new_project.idprojectsResearchHotbed

        # Crear producto si es necesario
        elif activity_type == 'producto' and data.get('product'):
            product_data = data['product']
            
            new_product = ProductsResearchHotbed(
                category_productsResearchHotbed=product_data.get('category', ''),
                type_productsResearchHotbed=product_data.get('type', ''),
                description_productsResearchHotbed=product_data.get('description', '')
            )
            
            db.session.add(new_product)
            db.session.flush()
            product_id = new_product.idproductsResearchHotbed

        # Crear reconocimiento si es necesario
        elif activity_type == 'reconocimiento' and data.get('recognition'):
            recognition_data = data['recognition']
            
            new_recognition = RecognitionsResearchHotbed(
                projectName_recognitionsResearchHotbed=recognition_data.get('project_name', ''),
                organizationName_recognitionsResearchHotbed=recognition_data.get('organization_name', '')
            )
            
            db.session.add(new_recognition)
            db.session.flush()
            recognition_id = new_recognition.idrecognitionsResearchHotbed

        # Crear la actividad principal
        activity = ActivitiesResearchHotbed(
            title_activitiesResearchHotbed=data['title'],
            responsible_activitiesResearchHotbed=data.get('responsible', ''),
            date_activitiesResearchHotbed=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            description_activitiesResearchHotbed=data['description'],
            type_activitiesResearchHotbed=data.get('type', 'actividad'),
            startTime_activitiesResearchHotbed=datetime.strptime(data['start_time'], '%H:%M').time() if data.get('start_time') else None,
            endTime_activitiesResearchHotbed=datetime.strptime(data['end_time'], '%H:%M').time() if data.get('end_time') else None,
            duration_activitiesResearchHotbed=data.get('duration'),
            approvedFreeHours_activitiesResearchHotbed=1.0 if data.get('approved_free_hours') else 0.0,
            semester=data.get('semester', 'semestre-1-2025'),
            usersResearchHotbed_idusersResearchHotbed=data['userResearchHotbedId'],
            projectsResearchHotbed_idprojectsResearchHotbed=project_id,
            productsResearchHotbed_idproductsResearchHotbed=product_id,
            recognitionsResearchHotbed_idrecognitionsResearchHotbed=recognition_id
        )

        db.session.add(activity)
        db.session.flush()

        print(f"Actividad creada con ID: {activity.idactivitiesResearchHotbed}")  # Debug

        # Crear relaciones de autoría para autores principales
        for author_id in data.get('authors_ids', []):
            print(f"Agregando autor principal: {author_id}")  # Debug
            author_relation = ActivityAuthors(
                activity_id=activity.idactivitiesResearchHotbed,
                user_research_hotbed_id=author_id,
                is_main_author=True
            )
            db.session.add(author_relation)

        # Crear relaciones de autoría para co-autores
        for co_author_id in data.get('co_authors_ids', []):
            print(f"Agregando co-autor: {co_author_id}")  # Debug
            co_author_relation = ActivityAuthors(
                activity_id=activity.idactivitiesResearchHotbed,
                user_research_hotbed_id=co_author_id,
                is_main_author=False
            )
            db.session.add(co_author_relation)

        db.session.commit()
        print("Transacción completada exitosamente")  # Debug

        return jsonify({
            "message": "Actividad registrada exitosamente",
            "activity_id": activity.idactivitiesResearchHotbed
        }), 201

    except ValueError as ve:
        db.session.rollback()
        print(f"Error de valor: {str(ve)}")
        return jsonify({"error": f"Error en formato de fecha: {str(ve)}"}), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error en register_activity: {str(e)}")
        print(f"Datos recibidos: {data}")  # Debug adicional
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500