from datetime import datetime, timedelta
from models.users import User
from db.connection import db

def mark_inactive_users():
    # Obtener la fecha actual y la fecha límite para inactividad
    current_date = datetime.utcnow()
    threshold_date = current_date - timedelta(days=60)

    # Obtener todos los usuarios cuya última fecha de login es más antigua que la fecha límite
    inactive_users = User.query.filter(User.lastDayLogin_user < threshold_date).all()

    # Actualizar el estado de estos usuarios a "inactive"
    for user in inactive_users:
        user.status_user = 'inactive'
    
    # Guardar los cambios en la base de datos
    db.session.commit()
    print(f"Usuarios marcados como inactivos: {len(inactive_users)}")