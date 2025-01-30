import pytest
from models.users import User
from datetime import datetime, timezone
from db.connection import db
from controllers.users.get_user_controller import get_user_data  # Asumiendo que el controlador está en controllers/user_controller.py

@pytest.fixture
def setup_database():
    # Crear un usuario de prueba y agregarlo a la base de datos
    user_data = {
        'email_user': 'user@example.com',
        'password_user': 'password',  # Se asume que este campo no se usará en el controlador
        'idSigaa_user': '12345',
        'name_user': 'Test User',
        'status_user': 'active',
        'type_user': 'student',
        'academicProgram_user': 'Computer Science',
        'termsAccepted_user': True,
        'termsAcceptedAt_user': datetime.now(timezone.utc),
        'termsVersion_user': '1.0',
        'lastDayLogin_user': None
    }
    user = User(**user_data)
    db.session.add(user)
    db.session.commit()
    return user  # Retorna el usuario creado para ser usado en las pruebas

def test_get_user_data_success(client, setup_database):
    # Obtener el ID del usuario creado
    user = setup_database

    # Llamar al controlador para obtener los datos del usuario
    response_data, status_code = get_user_data(user.iduser)

    # Verificar que la respuesta sea la esperada
    assert status_code == 200
    assert response_data['iduser'] == user.iduser
    assert response_data['email_user'] == user.email_user
    assert response_data['idSigaa_user'] == user.idSigaa_user
    assert response_data['name_user'] == user.name_user
    assert response_data['status_user'] == user.status_user
    assert response_data['type_user'] == user.type_user
    assert response_data['academicProgram_user'] == user.academicProgram_user
    assert response_data['termsAccepted_user'] == user.termsAccepted_user
    assert response_data['termsVersion_user'] == user.termsVersion_user
    assert response_data['termsAcceptedAt_user'] == user.termsAcceptedAt_user.strftime('%Y-%m-%d %H:%M:%S')

def test_get_user_data_not_found(client):
    # Llamar al controlador para obtener datos de un usuario que no existe
    response_data, status_code = get_user_data(9999)  # Un ID que no existe en la base de datos

    # Verificar que la respuesta sea la esperada
    assert status_code == 404
    assert response_data['message'] == "Usuario no encontrado"
