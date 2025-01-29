from functools import wraps
from flask import request, jsonify
import jwt
import os

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Obtener el token del encabezado Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"message": "Token no proporcionado"}), 401

        try:
            # Decodificar el token
            secret_key = os.getenv('SECRET_KEY')
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])

            # Agregar el usuario decodificado al objeto request
            request.user = {
                "iduser": payload["iduser"],
                "email_user": payload["email_user"]
            }

        except jwt.ExpiredSignatureError:
            return jsonify({"message": "El token ha expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token inválido"}), 401

        return f(*args, **kwargs)
    return decorated
