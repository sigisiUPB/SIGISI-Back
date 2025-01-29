import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

load_dotenv()  # Cargar las variables de entorno del archivo .env

db = SQLAlchemy()

def create_db_uri():
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')

    # Concatena los datos para formar la URL de conexión a la base de datos
    return f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
