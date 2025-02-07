from models.research_hotbed import ResearchHotbed
from flask import jsonify

def list_research_hotbeds():
    """
    Controlador para listar todos los semilleros.
    :return: Lista de semilleros en formato JSON.
    """
    try:
        # Consultar todos los semilleros en la base de datos
        research_hotbeds = ResearchHotbed.query.all()

        # Convertir los resultados en un formato serializable (diccionario)
        results = [
            {
                "idresearchHotbed": hotbed.idresearchHotbed,
                "name_researchHotbed": hotbed.name_researchHotbed,
                "universityBranch_researchHotbed": hotbed.universityBranch_researchHotbed,
                "acronym_researchHotbed": hotbed.acronym_researchHotbed,
                "faculty_researchHotbed": hotbed.faculty_researchHotbed,
                "status_researchHotbed": hotbed.status_researchHotbed,
                "dateCreation_researchHotbed": hotbed.dateCreation_researchHotbed,
                "deleteDescription_researchHotbed": hotbed.deleteDescription_researchHotbed,
            }
            for hotbed in research_hotbeds
        ]

        return jsonify(results), 200

    except Exception as e:
        return {"message": f"Error al listar los semilleros: {str(e)}"}, 500