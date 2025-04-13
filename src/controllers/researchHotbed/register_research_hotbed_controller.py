from models.research_hotbed import ResearchHotbed
from db.connection import db
from flask import jsonify
from datetime import datetime
import pytz

def create_research_hotbed(data):
    """
    Controlador para registrar un nuevo semillero.
    :param data: Diccionario con los datos del semillero.
    :return: Respuesta JSON con éxito o error.
    """
    required_fields = [
        "name_researchHotbed",
        "universityBranch_researchHotbed",
        "acronym_researchHotbed",
        "faculty_researchHotbed",
        "status_researchHotbed",
    ]

    # Verificar campos obligatorios
    for field in required_fields:
        if field not in data:
            return {"message": f"El campo '{field}' es obligatorio."}, 400

    try:
        # Obtener la hora actual en GMT-5
        gmt5_timezone = pytz.timezone("America/Bogota")
        current_time_gmt5 = datetime.now(gmt5_timezone).strftime("%Y-%m-%d %H:%M:%S")

        # Crear el nuevo semillero
        research_hotbed = ResearchHotbed(
            name_researchHotbed=data["name_researchHotbed"],
            universityBranch_researchHotbed=data["universityBranch_researchHotbed"],
            acronym_researchHotbed=data["acronym_researchHotbed"],
            faculty_researchHotbed=data["faculty_researchHotbed"],
            status_researchHotbed=data["status_researchHotbed"],
            dateCreation_researchHotbed=current_time_gmt5  # Fecha de creación en GMT-5
        )

        # Guardar en la base de datos
        db.session.add(research_hotbed)
        db.session.commit()

        new_id = research_hotbed.idresearchHotbed

        return {"message": "Semillero registrado con éxito.", "idresearchHotbed": new_id}, 201

    except Exception as e:
        db.session.rollback()
        return {"message": f"Error al registrar el semillero: {str(e)}"}, 500