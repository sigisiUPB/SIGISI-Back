import pytest
from models.research_hotbed import ResearchHotbed
from db.connection import db
from controllers.researchHotbed.get_all_research_hotbed_controller import list_research_hotbeds

def test_list_research_hotbeds_success(client, setup_database):
    """ Prueba cuando hay semilleros en la base de datos. """
    # Insertar datos de prueba
    research_hotbed1 = ResearchHotbed(
        name_researchHotbed="Semillero IA",
        universityBranch_researchHotbed="Sede Principal",
        acronym_researchHotbed="SIA",
        faculty_researchHotbed="Ingeniería",
        status_researchHotbed="Activo",
        dateCreation_researchHotbed="2024-02-10 10:00:00",
        deleteDescription_researchHotbed=None
    )

    research_hotbed2 = ResearchHotbed(
        name_researchHotbed="Semillero Robótica",
        universityBranch_researchHotbed="Sede Norte",
        acronym_researchHotbed="SR",
        faculty_researchHotbed="Tecnología",
        status_researchHotbed="Activo",
        dateCreation_researchHotbed="2024-02-11 11:00:00",
        deleteDescription_researchHotbed=None
    )

    db.session.add_all([research_hotbed1, research_hotbed2])
    db.session.commit()

    response, status_code = list_research_hotbeds()

    assert status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["name_researchHotbed"] == "Semillero IA"
    assert data[1]["name_researchHotbed"] == "Semillero Robótica"

def test_list_research_hotbeds_empty(client, setup_database):
    """ Prueba cuando no hay semilleros en la base de datos. """
    response, status_code = list_research_hotbeds()

    assert status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0  # No debe haber elementos en la lista

def test_list_research_hotbeds_db_error(client, monkeypatch):
    """ Prueba cuando ocurre un error en la base de datos. """

    class MockQuery:
        def all(self):
            raise Exception("Simulated DB Error")

    monkeypatch.setattr(ResearchHotbed, "query", MockQuery())

    response, status_code = list_research_hotbeds()

    assert status_code == 500
    assert "Error al listar los semilleros" in response["message"]

