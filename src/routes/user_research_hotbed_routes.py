from flask import Blueprint, request
from controllers.user_ResearchHotbed.add_user_research_hotbed_controller import add_user_to_research_hotbed
from middlewares.auth import token_required
from controllers.user_ResearchHotbed.get_users_research_hotbed_controller import get_users_by_research_hotbed
from controllers.user_ResearchHotbed.update_user_research_hotbed_controller import update_user_in_research_hotbed
from controllers.user_ResearchHotbed.get_research_hotbeds_by_user_controller import get_research_hotbeds_by_user

users_research_hotbed_routes = Blueprint("users_research_hotbed_routes", __name__)


# Ruta para agregar usuarios a un semillero
@users_research_hotbed_routes.route("/add/user-research-hotbeds/<int:research_hotbed_id>/users/<int:user_id>", methods=["POST"])
@token_required
def add_user_to_research_hotbed_route(research_hotbed_id, user_id):
    data = request.json  # Obtener datos de la solicitud
    return add_user_to_research_hotbed(user_id, research_hotbed_id, data)

# ruta para listar los usuarios de un semillero
@users_research_hotbed_routes.route("/get/user-research-hotbeds/<int:research_hotbed_id>/users", methods=["GET"])
@token_required
def get_users_by_research_hotbed_route(research_hotbed_id):
    return get_users_by_research_hotbed(research_hotbed_id)

# Ruta para actualizar usuarios que pertenecen a un semillero
@users_research_hotbed_routes.route("/update/users-research-hotbeds/<int:user_research_hotbed_id>", methods=["PUT"])
@token_required
def update_user_in_research_hotbed_route(user_research_hotbed_id):
    data = request.json
    return update_user_in_research_hotbed(user_research_hotbed_id, data)

# Ruta para listar los semilleros a los que pertenece un usuario
@users_research_hotbed_routes.route("/get/users/<int:user_id>/by/research-hotbeds", methods=["GET"])
@token_required
def get_research_hotbeds_by_user_route(user_id):
    return get_research_hotbeds_by_user(user_id)