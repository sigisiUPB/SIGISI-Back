import pytest
import hashlib
import jwt
import os
from datetime import datetime, UTC
import pytz
from models.users import User
from controllers.users.login_controller import login_user
from db.connection import db

# Función auxiliar para generar un hash de contraseña (simulando el almacenamiento en la BD)
def hash_password(password):
    salt = os.urandom(16).hex()  # Genera un salt aleatorio
    hashed_password = hashlib.sha256(bytes.fromhex(salt) + password.encode('utf-8')).hexdigest()
    return f"{salt}:{hashed_password}"  # Formato de almacenamiento

# Test para un inicio de sesión exitoso
def test_login_success(client, setup_database):
    # Crear usuario en la base de datos
    hashed_password = hash_password("SecurePassword123")
    user = User(
        email_user="test@example.com",
        password_user=hashed_password,
        idSigaa_user=12345,  # Agregar un valor ficticio
        name_user="Test User",
        status_user="active",
        type_user="student",
        academicProgram_user="Computer Science",
        termsAccepted_user=True,
        termsAcceptedAt_user=datetime.now(UTC),
        termsVersion_user="1.0"
    )
    db.session.add(user)
    db.session.commit()

    # Datos de inicio de sesión
    login_data = {
        "email_user": "test@example.com",
        "password_user": "SecurePassword123"
    }

    # Llamar al controlador de login
    response, status_code = login_user(login_data)

    # Verificar respuesta
    assert status_code == 200
    assert response["message"] == "Inicio de sesión exitoso"
    assert "token" in response  # Verifica que el token JWT se genera correctamente

    # Verificar que la última fecha de inicio de sesión se haya actualizado
    updated_user = User.query.filter_by(email_user="test@example.com").first()
    assert updated_user.lastDayLogin_user is not None

# Test para usuario no encontrado
def test_login_user_not_found(client, setup_database):
    login_data = {
        "email_user": "nonexistent@example.com",
        "password_user": "SomePassword"
    }

    response, status_code = login_user(login_data)

    assert status_code == 404
    assert response["message"] == "Usuario no encontrado"

# Test para contraseña incorrecta
def test_login_wrong_password(client, setup_database):
    # Crear usuario con una contraseña cifrada
    hashed_password = hash_password("CorrectPassword")
    user = User(
        email_user="test@example.com",
        password_user=hashed_password,
        idSigaa_user=12345,  # Agregar un valor ficticio
        name_user="Test User",
        status_user="active",
        type_user="student",
        academicProgram_user="Computer Science",
        termsAccepted_user=True,
        termsAcceptedAt_user=datetime.now(UTC),
        termsVersion_user="1.0"
    )
    db.session.add(user)
    db.session.commit()

    login_data = {
        "email_user": "test@example.com",
        "password_user": "WrongPassword"
    }

    response, status_code = login_user(login_data)

    assert status_code == 401
    assert response["message"] == "Contraseña incorrecta"

# Test para campos faltantes en la petición
@pytest.mark.parametrize("login_data, expected_message", [
    ({"email_user": "", "password_user": "SomePassword"}, "El correo y la contraseña son obligatorios"),
    ({"email_user": "test@example.com", "password_user": ""}, "El correo y la contraseña son obligatorios"),
    ({}, "El correo y la contraseña son obligatorios")
])
def test_login_missing_fields(client, setup_database, login_data, expected_message):
    response, status_code = login_user(login_data)

    assert status_code == 400
    assert response["message"] == expected_message
