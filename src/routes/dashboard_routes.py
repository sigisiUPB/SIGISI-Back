from flask import Blueprint, jsonify, request  # AGREGAR request
from middlewares.auth import token_required
from controllers.dashboard.dashboard_controller import get_dashboard_stats, get_user_research_hotbeds

dashboard_routes = Blueprint('dashboard_routes', __name__)

@dashboard_routes.route('/getUserResearchHotbeds', methods=['GET'])
@token_required
def get_user_research_hotbeds_route():
    """Obtiene los semilleros de investigación del usuario autenticado"""
    try:
        user_id = request.user['iduser']
        return get_user_research_hotbeds(user_id)
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@dashboard_routes.route('/dashboard/stats', methods=['GET'])
@token_required
def get_dashboard_stats_route():
    """Obtiene las estadísticas del dashboard para el usuario autenticado"""
    try:
        user_id = request.user['iduser']
        return get_dashboard_stats(user_id)
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500