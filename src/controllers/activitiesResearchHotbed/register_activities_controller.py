from datetime import datetime
from flask import jsonify
from models.projects_researchHotbed import ProjectsResearchHotbed
from models.products_researchHotbed import ProductsResearchHotbed
from models.recognitions_researchHotbed import RecognitionsResearchHotbed
from models.activities_researchHotbed import ActivitiesResearchHotbed
from db.connection import db

def register_activity(data):
    try:
        # Registrar el proyecto si se incluye en los datos
        project_id = None
        if 'project' in data:
            project_data = data['project']
            # Procesar co_researchers como una cadena de nombres separados por comas
            co_researchers = project_data.get('co_researchers', '')
            if co_researchers:
                co_researchers = ', '.join(co_researchers.split(','))  # Se asegura que esté en un formato correcto (cadena separada por comas)
                
            project = ProjectsResearchHotbed(
                name_projectsResearchHotbed=project_data['name'],
                referenceNumber_projectsResearchHotbed=project_data['reference_number'],
                startDate_projectsResearchHotbed=datetime.strptime(project_data['start_date'], '%Y-%m-%d'),
                endDate_projectsResearchHotbed=datetime.strptime(project_data['end_date'], '%Y-%m-%d') if project_data.get('end_date') else None,
                principalResearcher_projectsResearchHotbed=project_data['principal_researcher'],
                coResearchers_projectsResearchHotbed=co_researchers  # Guardamos como cadena separada por comas
            )
            db.session.add(project)
            db.session.flush()  # Para obtener su ID automáticamente
            project_id = project.idprojectsResearchHotbed

        # Registrar el producto si se incluye en los datos
        product_id = None
        if 'product' in data:
            product_data = data['product']
            product = ProductsResearchHotbed(
                category_productsResearchHotbed=product_data['category'],
                type_productsResearchHotbed=product_data['type'],
                description_productsResearchHotbed=product_data['description'],
                datePublication_productsResearchHotbed=datetime.strptime(product_data['date_publication'], '%Y-%m-%d')
            )
            db.session.add(product)
            db.session.flush()  # Para obtener su ID automáticamente
            product_id = product.idproductsResearchHotbed

        # Registrar el reconocimiento si se incluye en los datos
        recognition_id = None
        if 'recognition' in data:
            recognition_data = data['recognition']
            recognition = RecognitionsResearchHotbed(
                name_recognitionsResearchHotbed=recognition_data['name'],
                projectName_recognitionsResearchHotbed=recognition_data['project_name'],
                participantsNames_recognitionsResearchHotbed=recognition_data['participants_names'],
                organizationName_recognitionsResearchHotbed=recognition_data['organization_name']
            )
            db.session.add(recognition)
            db.session.flush()  # Para obtener su ID automáticamente
            recognition_id = recognition.idrecognitionsResearchHotbed

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
            usersResearchHotbed_idusersResearchHotbed=data['user_research_hotbed_id'],  # ID del usuario que está creando la actividad
            projectsResearchHotbed_idprojectsResearchHotbed=project_id,
            productsResearchHotbed_idproductsResearchHotbed=product_id,
            recognitionsResearchHotbed_idrecognitionsResearchHotbed=recognition_id
        )

        db.session.add(activity)
        db.session.commit()

        return jsonify({
            "message": "Actividad registrada exitosamente",
            "activity_id": activity.idactivitiesResearchHotbed
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
