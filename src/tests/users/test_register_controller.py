import pytest
from datetime import datetime
from models.users import User
from controllers.users.register_controller import create_user

# Test para crear un usuario correctamente
def test_create_user_success(client, setup_database):
    data = {
        'email_user': 'test@example.com',
        'password_user': 'SecurePassword123',
        'idSigaa_user': '12345',
        'name_user': 'Test User',
        'status_user': 'active',
        'type_user': 'student',
        'academicProgram_user': 'Computer Science',
        'termsAccepted_user': True,
        'termsAcceptedAt_user': '2025-01-01 10:00:00',
        'termsVersion_user': '1.0'
    }

    response = create_user(data)
    
    assert response[1] == 201  # Verifica que el estado sea 201 (creado)
    assert response[0]['message'] == "Usuario registrado con éxito"
    assert 'user' in response[0]  # Verifica que el ID del usuario esté en la respuesta

# Test para verificar si un usuario duplicado no se puede registrar
def test_create_user_duplicate(client, setup_database):
    data = {
        'email_user': 'test@example.com',
        'password_user': 'SecurePassword123',
        'idSigaa_user': '12345',
        'name_user': 'Test User',
        'status_user': 'active',
        'type_user': 'student',
        'academicProgram_user': 'Computer Science',
        'termsAccepted_user': True,
        'termsAcceptedAt_user': '2025-01-01 10:00:00',
        'termsVersion_user': '1.0'
    }

    # Registra el primer usuario
    create_user(data)

    # Intenta registrar el mismo usuario (debería fallar)
    response = create_user(data)
    
    assert response[1] == 400  # Verifica que el estado sea 400 (error)
    assert response[0]['message'] == "El usuario ya existe con ese correo o ID Sigaa"

# Test para verificar que la contraseña se encripte correctamente
def test_password_hashing(client, setup_database):
    data = {
        'email_user': 'test@example.com',
        'password_user': 'SecurePassword123',
        'idSigaa_user': '12345',
        'name_user': 'Test User',
        'status_user': 'active',
        'type_user': 'student',
        'academicProgram_user': 'Computer Science',
        'termsAccepted_user': True,
        'termsAcceptedAt_user': '2025-01-01 10:00:00',
        'termsVersion_user': '1.0'
    }

    # Crea el usuario
    create_user(data)

    # Obtiene el usuario de la base de datos
    user = User.query.filter_by(email_user='test@example.com').first()
    
    # Verifica que la contraseña en la base de datos no sea la misma que la ingresada
    # porque está cifrada
    assert user.password_user != data['password_user']
