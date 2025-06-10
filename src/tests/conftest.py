import pytest
import warnings
from flask import Flask
from db.connection import db
from models.users import User
from controllers.users.register_controller import create_user

# Suprimir warnings de deprecación para los tests
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Suprimir warnings específicos de SQLAlchemy
warnings.filterwarnings("ignore", message=".*The default datetime adapter is deprecated.*")
warnings.filterwarnings("ignore", message=".*Coercing Subquery object into a select.*")
warnings.filterwarnings("ignore", message=".*The Query.get.*method is considered legacy.*")

# Suprimir todos los warnings de SQLAlchemy
try:
    import sqlalchemy.exc
    warnings.filterwarnings("ignore", category=sqlalchemy.exc.SAWarning)
    warnings.filterwarnings("ignore", category=sqlalchemy.exc.LegacyAPIWarning)
except ImportError:
    pass

# Fixture para la configuración de la aplicación
@pytest.fixture
def app():
    """Crea y configura una aplicación Flask para pruebas."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # Base de datos en memoria
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Inicializar la base de datos con la aplicación
    db.init_app(app)
    
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        yield app
        # Limpiar después de cada test
        db.session.remove()
        db.drop_all()

# Fixture para el cliente de la aplicación (usado para simular peticiones HTTP)
@pytest.fixture
def client(app):
    """Crea un cliente de prueba para la aplicación."""
    return app.test_client()

# Fixture para preparar la base de datos antes de cada test
@pytest.fixture
def setup_database(app):
    """Prepara la base de datos con datos iniciales para las pruebas."""
    with app.app_context():
        # Crear tablas si no existen
        db.create_all()
        yield db
        # Limpiar después de la prueba
        db.session.rollback()
