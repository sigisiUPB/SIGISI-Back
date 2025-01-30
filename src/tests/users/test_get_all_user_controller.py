import pytest
from models.users import User
from datetime import datetime, timezone
from db.connection import db
from controllers.users.get_all_users_controller import get_all_users_data  # Asumiendo que el controlador está en controllers/user_controller.py

@pytest.fixture
def setup_database():
    # Crear usuarios de prueba y agregarlos a la base de datos
    user_data_1 = {
        'email_user': 'user1@example.com',
        'password_user': 'password',
        'idSigaa_user': '12345',
        'name_user': 'User One',
        'status_user': 'active',
        'type_user': 'student',
        'academicProgram_user': 'Mathematics',
        'termsAccepted_user': True,
        'termsAcceptedAt_user': datetime.now(timezone.utc),
        'termsVersion_user': '1.0',
        'lastDayLogin_user': None
    }
    user_data_2 = {
        'email_user': 'user2@example.com',
        'password_user': 'password',
        'idSigaa_user': '67890',
        'name_user': 'User Two',
        'status_user': 'inactive',
        'type_user': 'teacher',
        'academicProgram_user': 'Physics',
        'termsAccepted_user': False,
        'termsAcceptedAt_user': datetime.now(timezone.utc),
        'termsVersion_user': '1.1',
        'lastDayLogin_user': None
    }

    user1 = User(**user_data_1)
    user2 = User(**user_data_2)

    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()

    return [user1, user2]  # Retorna los usuarios creados para ser usados en las pruebas

def test_get_all_users_data_success(client, setup_database):
    # Obtener todos los usuarios de la base de datos
    response_data, status_code = get_all_users_data()

    # Verificar que la respuesta sea la esperada
    assert status_code == 200
    assert len(response_data['users']) == 2  # Asegurarse de que haya 2 usuarios
    assert response_data['users'][0]['name_user'] == 'User One'
    assert response_data['users'][1]['name_user'] == 'User Two'

def test_get_all_users_data_empty(client):
    # Limpiar la base de datos para simular un escenario donde no hay usuarios
    db.session.query(User).delete()
    db.session.commit()

    # Obtener todos los usuarios de la base de datos
    response_data, status_code = get_all_users_data()

    # Verificar que la respuesta sea la esperada
    assert status_code == 200
    assert response_data['users'] == []  # No debe haber usuarios
