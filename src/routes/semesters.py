from flask import Blueprint, jsonify, request
from utils.semester_utils import get_available_semesters, get_current_semester, format_semester_label
from middlewares.auth import token_required

semester_routes = Blueprint('semester_routes', __name__)

@semester_routes.route('/semesters', methods=['GET'])
@token_required  # Agregar este decorador
def get_semesters():
    """Obtiene la lista de semestres disponibles"""
    try:
        start_year = int(request.args.get('start_year', 2024))
        future_years = int(request.args.get('future_years', 2))
        
        semesters = get_available_semesters(start_year, future_years)
        
        # Formatear para el frontend
        formatted_semesters = [
            {
                'value': semester,
                'label': format_semester_label(semester)
            }
            for semester in semesters
        ]
        
        # Ordenar por año y semestre (más recientes primero)
        formatted_semesters.reverse()
        
        return jsonify({
            'semesters': formatted_semesters,
            'current_semester': get_current_semester()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@semester_routes.route('/semesters/current', methods=['GET'])
@token_required  # Agregar este decorador
def get_current_semester_route():
    """Obtiene el semestre actual"""
    try:
        current = get_current_semester()
        return jsonify({
            'current_semester': current,
            'label': format_semester_label(current)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500