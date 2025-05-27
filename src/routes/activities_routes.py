from flask import Blueprint, request, jsonify
from controllers.activitiesResearchHotbed.register_activities_controller import register_activity
from controllers.activitiesResearchHotbed.get_activities_by_research_hotbed_controller import get_activities_by_research_hotbed
from middlewares.auth import token_required  # Cambio aquí

activities_routes = Blueprint('activities_routes', __name__)

@activities_routes.route('/registerActivity', methods=['POST'])
@token_required
def create_activity():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se enviaron datos"}), 400
        
        return register_activity(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@activities_routes.route('/getActivitiesByResearchHotbed/<int:research_hotbed_id>', methods=['GET'])
@token_required
def get_activities_by_research_hotbed_route(research_hotbed_id):
    return get_activities_by_research_hotbed(research_hotbed_id)