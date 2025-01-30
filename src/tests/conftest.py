import pytest
from flask import Flask
from db.connection import db
from models.users import User
from controllers.users.register_controller import create_user

# Fixture para la configuración de la aplicación
@pytest.fixture
def app():
    """Crea y configura una aplicación Flask para pruebas."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # Base de datos en memoria
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    
    with app.app_context():
        db.create_all()  # Crea las tablas de la base de datos
        yield app  # Esto permite que se ejecuten las pruebas
        db.session.remove()
        db.drop_all()  # Limpia la base de datos después de la prueba

# Fixture para el cliente de la aplicación (usado para simular peticiones HTTP)
@pytest.fixture
def client(app):
    """Cliente de pruebas de Flask."""
    return app.test_client()

# Fixture para preparar la base de datos antes de cada test
@pytest.fixture
def setup_database(app):
    """Inicializa la base de datos antes de cada test."""
    with app.app_context():
        db.create_all()  # Crea las tablas de la base de datos
        yield  # Se ejecutan las pruebas
        db.session.remove()
        db.drop_all()  # Limpia la base de datos después de cada prueba
