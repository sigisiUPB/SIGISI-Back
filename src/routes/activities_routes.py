from flask import Blueprint, request, jsonify
from controllers.activitiesResearchHotbed.get_activities_controller import get_activity_details
from middlewares.auth import token_required
from controllers.activitiesResearchHotbed.register_activities_controller import register_activity
from controllers.activitiesResearchHotbed.update_activities_controller import update_activity

# Crear el Blueprint
activities_routes = Blueprint("activities_routes", __name__)

# Ruta para registrar una actividad
@activities_routes.route("/registerActivity", methods=["POST"])
@token_required
def register_activity_route():
    data = request.json # Obtener los datos de la solicitud
    return register_activity(data)

@activities_routes.route("/getActivity/<int:activity_id>", methods=['GET'])
@token_required
def get_activity(activity_id):
    return get_activity_details(activity_id)

# Ruta para actualizar actividad
@activities_routes.route("/updateActivity/<int:activity_id>", methods=["PUT"])
@token_required
def update_activity_route(activity_id):
    data = request.json
    return update_activity(activity_id, data)