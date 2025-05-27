from flask import Blueprint, request, jsonify
from middlewares.auth import token_required  # Asegúrate de que sea así
from controllers.users.register_controller import create_user
from controllers.users.login_controller import login_user
from controllers.users.get_user_controller import get_user_data
from controllers.users.update_user import update_user
from controllers.users.get_all_users_controller import get_all_users_data
from controllers.users.get_user_activities_controller import get_user_activities

user_routes = Blueprint('user_routes', __name__)

# Ruta para registrar usuarios
@user_routes.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()

    if not data:
        return jsonify({"message": "No se ha enviado ningún dato"}), 400

    # Validación básica
    required_fields = [
        'email_user', 'password_user', 'idSigaa_user', 'name_user', 
        'status_user', 'type_user', 'academicProgram_user', 
        'termsAccepted_user', 'termsAcceptedAt_user', 'termsVersion_user'
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Falta el campo {field}"}), 400

    # Validación extra: termsAccepted_user debe ser 0 o 1
    if not isinstance(data['termsAccepted_user'], int) or data['termsAccepted_user'] not in [0, 1]:
        return jsonify({"message": "El campo termsAccepted_user debe ser 0 o 1"}), 400

    # Validación extra: termsAcceptedAt_user debe ser una fecha válida en el formato esperado
    try:
        from datetime import datetime
        datetime.strptime(data['termsAcceptedAt_user'], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({"message": "El campo termsAcceptedAt_user debe estar en formato 'YYYY-MM-DD HH:MM:SS'"}), 400

    # Crear el usuario llamando al controlador
    result, status_code = create_user(data)
    return jsonify(result), status_code

# Ruta para realizar el login
@user_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Validar que se enviaron datos
    if not data:
        return jsonify({"message": "No se ha enviado ningún dato"}), 400

    # Verificar que los campos requeridos están presentes
    required_fields = ['email_user', 'password_user']
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Falta el campo {field}"}), 400

    # Validar que el email tiene un formato correcto
    email = data.get('email_user')
    if not isinstance(email, str) or '@' not in email or '.' not in email:
        return jsonify({"message": "El correo no tiene un formato válido"}), 400

    # Validar que la contraseña no esté vacía y cumpla con un mínimo de caracteres
    password = data.get('password_user')
    if not isinstance(password, str) or len(password) < 8:
        return jsonify({
            "message": "La contraseña es obligatoria y debe tener al menos 8 caracteres"
        }), 400

    # Llamar al controlador para procesar el inicio de sesión
    result, status_code = login_user(data)
    return jsonify(result), status_code

# Obtener la informacion del usuario al que pertenece el token
@user_routes.route('/user', methods=['GET'])
@token_required
def get_authenticated_user():
    try:
        # El usuario autenticado está disponible en request.user gracias al middleware
        user_id = request.user['iduser']
        
        # Obtener la información del usuario llamando al controlador
        result, status_code = get_user_data(user_id)
        
        if status_code == 200:
            return jsonify(result), 200
        else:
            return jsonify(result), status_code
            
    except Exception as e:
        print(f"Error en get_authenticated_user: {str(e)}")
        return jsonify({"message": f"Error interno del servidor: {str(e)}"}), 500

# ruta para actualizar usuarios a los que pertenece el token
@user_routes.route('/user/update', methods=['PUT'])
@token_required
def update_user_route():
    user_data = request.user  # Datos del token decodificado (iduser, email_user)
    user_id = user_data["iduser"]  # ID del usuario autenticado

    # Obtener los datos enviados en el cuerpo de la solicitud
    data = request.get_json()

    if not data:
        return jsonify({"message": "No se han proporcionado datos para actualizar"}), 400

    # Llamar al controlador para actualizar al usuario
    result, status_code = update_user(user_id, data)
    return jsonify(result), status_code

# Ruta para obtener las actividades del usuario autenticado
@user_routes.route('/user/activities', methods=['GET'])
@token_required
def get_user_activities_route():
    """Obtiene las actividades del usuario, opcionalmente filtradas por semestre"""
    try:
        # Obtener el ID del usuario desde el token decodificado (igual que en otras rutas)
        user_id = request.user['iduser']
        
        # Llamar al controlador
        return get_user_activities(user_id)
        
    except KeyError:
        return jsonify({"error": "No se pudo obtener la información del usuario del token"}), 401
    except Exception as e:
        print(f"Error en get_user_activities_route: {str(e)}")
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500

# Ruta para ver todos los usuarios
@user_routes.route('/allUsers', methods=['GET'])
@token_required
def get_all_users():
    result, status_code = get_all_users_data()
    return jsonify(result), status_code

# Ruta para actualizar cualquier usuario (Necesita un token valido)
@user_routes.route('/update/<int:user_id>', methods=['PUT'])
@token_required  # Asegúrate de que la ruta está protegida por el middleware
def update_anyUser_route(user_id):
    data = request.get_json()
    
    # Verificar que los datos fueron enviados
    if not data:
        return jsonify({"message": "No se han enviado datos para actualizar."}), 400

    # Llamar al controlador de actualización con el user_id proporcionado
    result, status_code = update_user(user_id, data)
    return jsonify(result), status_code