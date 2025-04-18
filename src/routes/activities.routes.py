from flask import Blueprint
from controllers.activitiesResearchHotbed.activities_controller import activities_bp

# Creamos un blueprint agrupador de rutas
activities_routes = Blueprint('activities_routes', __name__)

# Registramos las rutas del controlador de actividades
activities_routes.register_blueprint(activities_bp, url_prefix='/activities')
