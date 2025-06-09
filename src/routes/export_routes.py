from flask import Blueprint, request, jsonify
from middlewares.auth import token_required
from controllers.export.excel_export_controller import export_research_hotbed_excel
from controllers.export.users_pdf_export_controller import export_user_excel, export_multiple_users_excel

export_routes = Blueprint('export_routes', __name__)

@export_routes.route('/export/research-hotbed/<int:research_hotbed_id>/excel', methods=['GET'])
@token_required
def export_research_hotbed_excel_route(research_hotbed_id):
    """
    Exporta un archivo Excel completo del semillero para el semestre especificado
    """
    try:
        semester = request.args.get('semester')
        
        if not semester:
            return jsonify({"error": "Parámetro 'semester' requerido"}), 400
            
        return export_research_hotbed_excel(research_hotbed_id, semester)
        
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@export_routes.route('/export/user/<int:user_id>/excel', methods=['GET'])
@token_required
def export_user_excel_route(user_id):
    """
    Exporta un archivo Excel individual del usuario para el semestre especificado
    Query parameters:
    - semester: formato 'semestre-1-2025'
    """
    try:
        semester = request.args.get('semester')
        
        if not semester:
            return jsonify({"error": "Parámetro 'semester' requerido"}), 400
            
        return export_user_excel(user_id, semester)
        
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@export_routes.route('/export/users/excel', methods=['POST'])
@token_required
def export_multiple_users_excel_route():
    """
    Exporta un archivo Excel consolidado con múltiples usuarios
    Body JSON:
    {
        "user_ids": [1, 2, 3],
        "semester": "semestre-1-2025"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se enviaron datos"}), 400
            
        user_ids = data.get('user_ids', [])
        semester = data.get('semester')
        
        if not user_ids:
            return jsonify({"error": "Lista de usuarios requerida"}), 400
            
        if not semester:
            return jsonify({"error": "Parámetro 'semester' requerido"}), 400
            
        return export_multiple_users_excel(user_ids, semester)
        
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@export_routes.route('/export/user/<int:user_id>/preview', methods=['GET'])
@token_required
def preview_user_export_data_route(user_id):
    """
    Previsualiza los datos que se incluirán en el Excel del usuario
    """
    try:
        semester = request.args.get('semester')
        
        if not semester:
            return jsonify({"error": "Parámetro 'semester' requerido"}), 400
            
        from controllers.export.users_pdf_export_controller import get_user_research_hotbeds, get_user_activities_by_semester
        from models.users import User
        from utils.semester_utils import format_semester_label_detailed
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        research_hotbeds = get_user_research_hotbeds(user_id)
        activities = get_user_activities_by_semester(user_id, semester)
        
        return jsonify({
            "user": {
                "name": user.name_user,
                "email": user.email_user,
                "idSigaa": user.idSigaa_user,
                "type": user.type_user
            },
            "semester_label": format_semester_label_detailed(semester),
            "stats": {
                "total_research_hotbeds": len(research_hotbeds),
                "total_activities": len(activities),
                "total_hours": sum(a['duration'] for a in activities),
                "approved_activities": len([a for a in activities if a['approved_free_hours']])
            },
            "research_hotbeds_count": len(research_hotbeds),
            "activities_count": len(activities)
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

# Rutas de compatibilidad (alias)
@export_routes.route('/export/user/<int:user_id>/pdf', methods=['GET'])
@token_required
def export_user_pdf_route(user_id):
    """Alias para compatibilidad - redirige a Excel"""
    return export_user_excel_route(user_id)

@export_routes.route('/export/users/pdf', methods=['POST'])
@token_required
def export_multiple_users_pdf_route():
    """Alias para compatibilidad - redirige a Excel"""
    return export_multiple_users_excel_route()