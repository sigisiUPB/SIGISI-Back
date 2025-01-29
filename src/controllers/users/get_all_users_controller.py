from models.users import User

def get_all_users_data():
    try:
        # Obtener todos los usuarios de la base de datos
        users = User.query.all()

        # Serializar los datos de los usuarios
        users_list = []
        for user in users:
            users_list.append({
                "iduser": user.iduser,
                "email_user": user.email_user,
                "idSigaa_user": user.idSigaa_user,
                "name_user": user.name_user,
                "status_user": user.status_user,
                "type_user": user.type_user,
                "academicProgram_user": user.academicProgram_user,
                "termsAccepted_user": user.termsAccepted_user,
                "termsAcceptedAt_user": user.termsAcceptedAt_user.strftime('%Y-%m-%d %H:%M:%S'),
                "termsVersion_user": user.termsVersion_user
            })

        return {"users": users_list}, 200

    except Exception as e:
        return {"message": "Ocurrió un error al obtener los usuarios", "error": str(e)}, 500