import os
from flask import Flask
from db.connection import db, create_db_uri
from routes.user_routes import user_routes  # Aquí importas directamente user_routes
from apscheduler.schedulers.background import BackgroundScheduler
from utils.inactive_users import mark_inactive_users  # Importar la función desde inactiveUser.py
from routes.research_hotbed_routes import research_hotbed_routes
from routes.user_research_hotbed_routes import users_research_hotbed_routes

def create_app():
    app = Flask(__name__) 

    # Configuración de la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = create_db_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # Inicialización de la base de datos
    db.init_app(app)

    # Registro de rutas
    app.register_blueprint(user_routes)  # Rutas de usuarios
    app.register_blueprint(research_hotbed_routes)  # Rutas de semilleros
    app.register_blueprint(users_research_hotbed_routes)

    # Inicialización de APScheduler
    scheduler = BackgroundScheduler()
    
    # Agregar job que marque los usuarios inactivos cada 24 horas
    scheduler.add_job(mark_inactive_users, 'interval', hours=24)

    # Iniciar el scheduler
    scheduler.start()

    return app

if __name__ == "__main__":
    app = create_app()
    port = os.getenv('FLASK_APP_PORT', 5000)
    app.run(host='0.0.0.0', port=port)