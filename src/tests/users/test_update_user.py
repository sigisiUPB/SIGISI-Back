import pytest
from models.users import User
from controllers.users.update_user import update_user
from db.connection import db
from datetime import datetime, UTC

# Test para actualizar los datos de un usuario existente
def test_update_user_success(client, setup_database):
    # Crear un usuario de prueba con una contraseña
    user_data = {
        'email_user': 'old_email@example.com',
        'password_user': 'oldpassword',  # Contraseña obligatoria
        'idSigaa_user': '12345',
        'name_user': 'Old Name',
        'status_user': 'active',
        'type_user': 'student',
        'academicProgram_user': 'Computer Science',
        'termsAccepted_user': True,
        'termsAcceptedAt_user': datetime.now(UTC),
        'termsVersion_user': '1.0',
        'lastDayLogin_user': None
    }

    # Crear y guardar el usuario
    user = User(**user_data)
    db.session.add(user)
    db.session.commit()

    # Datos para actualizar el usuario
    updated_data = {
        'email_user': 'new_email@example.com',
        'name_user': 'New Name',
        'status_user': 'inactive'
    }

    # Llamar al controlador para actualizar
    response = update_user(user.iduser, updated_data)
    
    # Verificar que la respuesta sea la esperada
    assert response[1] == 200  # Estado 200 (éxito)
    assert response[0]['message'] == "Usuario actualizado con éxito"

    # Verificar que los datos fueron actualizados correctamente
    updated_user = User.query.filter_by(iduser=user.iduser).first()
    assert updated_user.email_user == updated_data['email_user']
    assert updated_user.name_user == updated_data['name_user']
    assert updated_user.status_user == updated_data['status_user']

# Test para intentar actualizar un usuario que no existe
def test_update_user_not_found(client, setup_database):
    # Datos para intentar actualizar un usuario que no existe
    updated_data = {
        'email_user': 'new_email@example.com',
        'name_user': 'New Name',
        'status_user': 'inactive'
    }

    # Llamar al controlador con un ID de usuario que no existe
    response = update_user(9999, updated_data)  # ID de usuario que no existe
    
    # Verificar que la respuesta sea la esperada
    assert response[1] == 404  # Estado 404 (no encontrado)
    assert response[0]['message'] == "Usuario no encontrado"

# Test para intentar actualizar un usuario con datos incompletos
def test_update_user_partial_data(client, setup_database):
    # Crear un usuario de prueba con una contraseña
    user_data = {
        'email_user': 'old_email@example.com',
        'password_user': 'oldpassword',  # Contraseña obligatoria
        'idSigaa_user': '12345',
        'name_user': 'Old Name',
        'status_user': 'active',
        'type_user': 'student',
        'academicProgram_user': 'Computer Science',
        'termsAccepted_user': True,
        'termsAcceptedAt_user': datetime.now(UTC),
        'termsVersion_user': '1.0',
        'lastDayLogin_user': None
    }

    user = User(**user_data)
    db.session.add(user)
    db.session.commit()

    # Datos parcialmente incompletos para actualizar
    updated_data = {
        'email_user': 'new_email@example.com'
    }

    # Llamar al controlador para actualizar
    response = update_user(user.iduser, updated_data)
    
    # Verificar que la respuesta sea la esperada
    assert response[1] == 200  # Estado 200 (éxito)
    assert response[0]['message'] == "Usuario actualizado con éxito"

    # Verificar que solo el campo email_user haya cambiado
    updated_user = User.query.filter_by(iduser=user.iduser).first()
    assert updated_user.email_user == updated_data['email_user']
    assert updated_user.name_user == user.name_user  # No debería haber cambiado
    assert updated_user.status_user == user.status_user  # No debería haber cambiado

# Test para intentar actualizar con datos que causen un error en la base de datos
def test_update_user_db_error(client, setup_database, mocker):
    # Crear un usuario de prueba con una contraseña
    user_data = {
        'email_user': 'old_email@example.com',
        'password_user': 'oldpassword',  # Contraseña obligatoria
        'idSigaa_user': '12345',
        'name_user': 'Old Name',
        'status_user': 'active',
        'type_user': 'student',
        'academicProgram_user': 'Computer Science',
        'termsAccepted_user': True,
        'termsAcceptedAt_user': datetime.now(UTC),
        'termsVersion_user': '1.0',
        'lastDayLogin_user': None
    }

    user = User(**user_data)
    db.session.add(user)
    db.session.commit()

    # Simular un error en la base de datos (por ejemplo, una violación de clave única)
    mocker.patch('db.connection.db.session.commit', side_effect=Exception("Error en la base de datos"))

    # Datos para actualizar
    updated_data = {
        'email_user': 'new_email@example.com',
        'name_user': 'New Name'
    }

    # Llamar al controlador para actualizar
    response = update_user(user.iduser, updated_data)
    
    # Verificar que la respuesta sea la esperada (error en la base de datos)
    assert response[1] == 500  # Estado 500 (error interno del servidor)
    assert "Error al actualizar el usuario" in response[0]['message']
