from flask import Blueprint, request, jsonify
from controllers.activitiesResearchHotbed.register_activities_controller import register_activity
from controllers.activitiesResearchHotbed.get_activities_controller import get_activity_details
from controllers.activitiesResearchHotbed.get_activities_by_research_hotbed_controller import get_activities_by_research_hotbed
from controllers.activitiesResearchHotbed.update_activities_controller import update_activity
from controllers.activitiesResearchHotbed.delete_activities_controller import delete_activity
from middlewares.auth import token_required

activities_routes = Blueprint('activities', __name__)

@activities_routes.route('/registerActivity', methods=['POST'])
@token_required
def register_activity_route():
    data = request.get_json()
    return register_activity(data)

@activities_routes.route('/get/activities/<int:activity_id>', methods=['GET'])
@token_required
def get_activity_details_route(activity_id):
    return get_activity_details(activity_id)

@activities_routes.route('/get/research-hotbeds/<int:research_hotbed_id>/activities', methods=['GET'])
@token_required
def get_activities_by_research_hotbed_route(research_hotbed_id):
    return get_activities_by_research_hotbed(research_hotbed_id)

# Ruta adicional para compatibilidad con el frontend existente
@activities_routes.route('/getActivitiesByResearchHotbed/<int:research_hotbed_id>', methods=['GET'])
@token_required
def get_activities_by_research_hotbed_simple_route(research_hotbed_id):
    return get_activities_by_research_hotbed(research_hotbed_id)

@activities_routes.route('/updateActivity/<int:activity_id>', methods=['PUT'])
@token_required
def update_activity_route(activity_id):
    data = request.get_json()
    return update_activity(activity_id, data)

@activities_routes.route('/deleteActivity/<int:activity_id>', methods=['DELETE'])
@token_required
def delete_activity_route(activity_id):
    return delete_activity(activity_id)