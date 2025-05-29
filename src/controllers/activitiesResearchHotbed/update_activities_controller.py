from flask import jsonify
from models.activities_researchHotbed import ActivitiesResearchHotbed
from models.projects_researchHotbed import ProjectsResearchHotbed
from models.products_researchHotbed import ProductsResearchHotbed
from models.recognitions_researchHotbed import RecognitionsResearchHotbed
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
            project.name_projectsResearchHotbed = data['project'].get('name', project.name_projectsResearchHotbed)
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

            # Eliminar la línea que causa error: name_recognitionsResearchHotbed no se usa en el frontend
            recognition.projectName_recognitionsResearchHotbed = data['recognition'].get('project_name', recognition.projectName_recognitionsResearchHotbed)
            recognition.participantsNames_recognitionsResearchHotbed = data['recognition'].get('participants_names', recognition.participantsNames_recognitionsResearchHotbed)
            recognition.organizationName_recognitionsResearchHotbed = data['recognition'].get('organization_name', recognition.organizationName_recognitionsResearchHotbed)

        db.session.commit()

        return jsonify({"message": "Actividad actualizada correctamente"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
