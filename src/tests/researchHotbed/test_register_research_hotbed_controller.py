import pytest
from models.research_hotbed import ResearchHotbed
from db.connection import db
from controllers.researchHotbed.register_research_hotbed_controller import create_research_hotbed
from datetime import datetime
import pytz

@pytest.fixture
def setup_database():
    """ Configura la base de datos antes de cada prueba. """
    db.session.query(ResearchHotbed).delete()
    db.session.commit()

def test_create_research_hotbed_success(client, setup_database):
    """ Prueba el registro exitoso de un semillero. """
    data = {
        "name_researchHotbed": "Semillero Innovación",
        "universityBranch_researchHotbed": "Sede Principal",
        "acronym_researchHotbed": "SI",
        "faculty_researchHotbed": "Ingeniería",
        "status_researchHotbed": "Activo"
    }

    response, status_code = create_research_hotbed(data)

    assert status_code == 201
    assert response["message"] == "Semillero registrado con éxito."

    # Verificar que el semillero fue guardado en la base de datos
    research_hotbed = ResearchHotbed.query.filter_by(acronym_researchHotbed="SI").first()
    assert research_hotbed is not None
    assert research_hotbed.name_researchHotbed == "Semillero Innovación"

def test_create_research_hotbed_missing_field(client, setup_database):
    """ Prueba la validación cuando falta un campo obligatorio. """
    data = {
        "name_researchHotbed": "Semillero Ciencia",
        "acronym_researchHotbed": "SC",
        "faculty_researchHotbed": "Ciencias",
        "status_researchHotbed": "Activo"
        # Falta 'universityBranch_researchHotbed'
    }

    response, status_code = create_research_hotbed(data)

    assert status_code == 400
    assert "El campo 'universityBranch_researchHotbed' es obligatorio." in response["message"]

def test_create_research_hotbed_db_error(client, monkeypatch):
    """ Prueba cuando ocurre un error en la base de datos. """
    data = {
        "name_researchHotbed": "Semillero Falla",
        "universityBranch_researchHotbed": "Sede Sur",
        "acronym_researchHotbed": "SF",
        "faculty_researchHotbed": "Ciencias Sociales",
        "status_researchHotbed": "Activo"
    }

    # Simular un error en la base de datos al guardar
    def mock_add(*args, **kwargs):
        raise Exception("Simulated DB Error")

    monkeypatch.setattr(db.session, "add", mock_add)

    response, status_code = create_research_hotbed(data)

    assert status_code == 500
    assert "Error al registrar el semillero" in response["message"]
