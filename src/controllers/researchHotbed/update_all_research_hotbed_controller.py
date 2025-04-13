from flask import jsonify
from models.research_hotbed import ResearchHotbed
from db.connection import db

def update_research_hotbed(research_hotbed_id, data):
    """
    Controlador para actualizar un semillero.
    :param research_hotbed_id: ID del semillero a actualizar.
    :param data: Datos enviados por el cliente para actualizar.
    :return: Mensaje de éxito o error.
    """
    # Buscar el semillero en la base de datos
    research_hotbed = ResearchHotbed.query.filter_by(idresearchHotbed=research_hotbed_id).first()

    if not research_hotbed:
        return {"message": "Semillero no encontrado"}, 404

    # Actualizar solo los campos proporcionados
    updatable_fields = [
        "name_researchHotbed",
        "universityBranch_researchHotbed",
        "acronym_researchHotbed",
        "faculty_researchHotbed",
        "status_researchHotbed",
        "deleteDescription_researchHotbed"
    ]
    for field in updatable_fields:
        if field in data:
            setattr(research_hotbed, field, data[field])

    # Guardar los cambios en la base de datos
    try:
        db.session.commit()
        return {"message": "Semillero actualizado con éxito"}, 200
    except Exception as e:
        db.session.rollback()
        return {"message": f"Error al actualizar el semillero: {str(e)}"}, 500