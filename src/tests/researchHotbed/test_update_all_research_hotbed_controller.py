import pytest
from models.research_hotbed import ResearchHotbed
from db.connection import db
from controllers.researchHotbed.update_all_research_hotbed_controller import update_research_hotbed

def test_update_research_hotbed_success(client, setup_database):
    """Prueba la actualización exitosa de un semillero."""
    # Insertar un semillero de prueba con la fecha de creación
    research_hotbed = ResearchHotbed(
        name_researchHotbed="Semillero IA",
        universityBranch_researchHotbed="Sede Principal",
        acronym_researchHotbed="SIA",
        faculty_researchHotbed="Ingeniería",
        status_researchHotbed="Activo",
        dateCreation_researchHotbed="2024-02-10 10:00:00",  # Agregar un valor válido
        deleteDescription_researchHotbed=None
    )
    db.session.add(research_hotbed)
    db.session.commit()

    # Datos de actualización
    update_data = {
        "name_researchHotbed": "Nuevo Semillero IA",
        "status_researchHotbed": "Inactivo"
    }

    response, status_code = update_research_hotbed(research_hotbed.idresearchHotbed, update_data)

    # Verificar que la respuesta es exitosa
    assert status_code == 200
    assert response["message"] == "Semillero actualizado con éxito"

    # Verificar que los cambios fueron aplicados en la base de datos
    updated_hotbed = db.session.get(ResearchHotbed, research_hotbed.idresearchHotbed)  # Usar session.get()
    assert updated_hotbed.name_researchHotbed == "Nuevo Semillero IA"
    assert updated_hotbed.status_researchHotbed == "Inactivo"


def test_update_research_hotbed_not_found(client, setup_database):
    """Prueba cuando el semillero no existe en la base de datos."""
    # Intentar actualizar un semillero con un ID que no existe
    non_existent_id = 999  # Asumiendo que no existe un semillero con este ID
    update_data = {
        "name_researchHotbed": "Nuevo Semillero IA",
        "status_researchHotbed": "Inactivo"
    }

    # Llamar al controlador para actualizar el semillero
    response, status_code = update_research_hotbed(non_existent_id, update_data)

    # Verificar que el código de estado sea 404
    assert status_code == 404
    assert response["message"] == "Semillero no encontrado"
