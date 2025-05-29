from flask import jsonify
from models.activities_researchHotbed import ActivitiesResearchHotbed
from models.projects_researchHotbed import ProjectsResearchHotbed
from models.products_researchHotbed import ProductsResearchHotbed
from models.recognitions_researchHotbed import RecognitionsResearchHotbed
from models.activity_authors import ActivityAuthors
from db.connection import db

def delete_activity(activity_id):
    try:
        # Buscar la actividad existente
        activity = ActivitiesResearchHotbed.query.get(activity_id)
        if not activity:
            return jsonify({"message": "Actividad no encontrada"}), 404

        # Eliminar las relaciones de autoría primero
        ActivityAuthors.query.filter_by(activity_id=activity_id).delete()

        # Eliminar entidades relacionadas si existen
        if activity.projectsResearchHotbed_idprojectsResearchHotbed:
            project = ProjectsResearchHotbed.query.get(activity.projectsResearchHotbed_idprojectsResearchHotbed)
            if project:
                db.session.delete(project)

        if activity.productsResearchHotbed_idproductsResearchHotbed:
            product = ProductsResearchHotbed.query.get(activity.productsResearchHotbed_idproductsResearchHotbed)
            if product:
                db.session.delete(product)

        if activity.recognitionsResearchHotbed_idrecognitionsResearchHotbed:
            recognition = RecognitionsResearchHotbed.query.get(activity.recognitionsResearchHotbed_idrecognitionsResearchHotbed)
            if recognition:
                db.session.delete(recognition)

        # Finalmente eliminar la actividad
        db.session.delete(activity)
        db.session.commit()

        return jsonify({"message": "Actividad eliminada correctamente"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500