from flask import Blueprint, request
from controllers.user_ResearchHotbed.add_user_research_hotbed_controller import add_user_to_research_hotbed
from middlewares.auth import token_required
from controllers.user_ResearchHotbed.get_users_research_hotbed_controller import get_users_by_research_hotbed

users_research_hotbed_routes = Blueprint("users_research_hotbed_routes", __name__)


# Ruta para agregar usuarios a un semillero
@users_research_hotbed_routes.route("/research-hotbeds/<int:research_hotbed_id>/users/<int:user_id>", methods=["POST"])
@token_required
def add_user_to_research_hotbed_route(research_hotbed_id, user_id):
    data = request.json  # Obtener datos de la solicitud
    return add_user_to_research_hotbed(user_id, research_hotbed_id, data)

# ruta para listar los usuarios de un semillero
@users_research_hotbed_routes.route("/research-hotbeds/<int:research_hotbed_id>/users", methods=["GET"])
@token_required
def get_users_by_research_hotbed_route(research_hotbed_id):
    return get_users_by_research_hotbed(research_hotbed_id)