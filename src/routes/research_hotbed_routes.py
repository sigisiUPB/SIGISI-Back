from flask import Blueprint, request, jsonify
from controllers.researchHotbed.get_all_research_hotbed_controller import list_research_hotbeds
from controllers.researchHotbed.register_research_hotbed_controller import create_research_hotbed
from controllers.researchHotbed.update_all_research_hotbed import update_research_hotbed
from middlewares.auth import token_required  # Si deseas proteger la ruta con autenticación

# Crear el Blueprint
research_hotbed_routes = Blueprint('research_hotbed_routes', __name__)

# Ruta para registrar un nuevo semillero
@research_hotbed_routes.route('/registerResearchHotbed', methods=['POST'])
@token_required  # Protege la ruta (opcional)
def register_research_hotbed():
    data = request.get_json()

    # Verificar que se enviaron datos
    if not data:
        return jsonify({"message": "No se han enviado datos para registrar."}), 400

    # Llamar al controlador para registrar el semillero
    result, status_code = create_research_hotbed(data)
    return jsonify(result), status_code

# Mostrar todos los semilleros
@research_hotbed_routes.route("/getAllResearchHotbeds", methods=["GET"])
@token_required  # Decorador que protege la ruta
def get_research_hotbeds():
    return list_research_hotbeds()

# Ruta para actualizar un semillero
@research_hotbed_routes.route("/update/researchHotbed/<int:research_hotbed_id>", methods=["PUT"])
@token_required  # Decorador para requerir token válido
def update_research_hotbed_route(research_hotbed_id):
    data = request.json  # Obtener los datos del cuerpo de la solicitud
    return update_research_hotbed(research_hotbed_id, data)