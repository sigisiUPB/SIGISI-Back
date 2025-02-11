from models.users import User
from db.connection import db
from datetime import datetime
import hashlib 
import os      

def hash_password(password):
    """Genera un hash SHA-256 con un salt único"""
    salt = os.urandom(16)  # Genera un salt único (16 bytes)
    hashed_password = hashlib.sha256(salt + password.encode('utf-8')).hexdigest()
    return f"{salt.hex()}:{hashed_password}"  # Guardamos salt y hash juntos

def create_user(data):
    # Verificar si ya existe un usuario con el mismo correo o ID Sigaa
    existing_user = User.query.filter(
        (User.email_user == data['email_user']) | 
        (User.idSigaa_user == data['idSigaa_user'])
    ).first()

    if existing_user:
        return {"message": "El usuario ya existe con ese correo o ID Sigaa"}, 400

    # Cifrar la contraseña usando SHA-256 con un salt
    hashed_password = hash_password(data['password_user'])

    # Crear el usuario con la contraseña cifrada
    user = User(
        email_user=data['email_user'],
        password_user=hashed_password,  # Guardar hash + salt
        idSigaa_user=data['idSigaa_user'],
        name_user=data['name_user'],
        status_user=data['status_user'],
        type_user=data['type_user'],
        academicProgram_user=data['academicProgram_user'],
        termsAccepted_user=bool(data['termsAccepted_user']),
        termsAcceptedAt_user=datetime.strptime(data['termsAcceptedAt_user'], '%Y-%m-%d %H:%M:%S'),
        termsVersion_user=data['termsVersion_user']
    )
    
    # Guardar el usuario en la base de datos
    db.session.add(user)
    db.session.commit()

    return {"message": "Usuario registrado con éxito", "user": user.iduser}, 201