from flask import jsonify
from db.connection import db
from models.users import User
from models.users_research_hotbed import UsersResearchHotbed
from models.research_hotbed import ResearchHotbed
from models.activities_researchHotbed import ActivitiesResearchHotbed
from models.activity_authors import ActivityAuthors
from utils.semester_utils import get_current_semester
from datetime import datetime

def get_user_research_hotbeds(user_id):
    """
    Obtiene los semilleros de investigación donde participa el usuario
    """
    try:
        # Obtener semilleros activos donde el usuario participa
        research_hotbeds_query = db.session.query(ResearchHotbed, UsersResearchHotbed)\
            .join(UsersResearchHotbed, ResearchHotbed.idresearchHotbed == UsersResearchHotbed.researchHotbed_idresearchHotbed)\
            .filter(UsersResearchHotbed.user_iduser == user_id)\
            .filter(UsersResearchHotbed.status_usersResearchHotbed == 'Activo')\
            .filter(ResearchHotbed.status_researchHotbed == 'Activo')\
            .all()

        if not research_hotbeds_query:
            return jsonify({"research_hotbeds": []}), 200

        research_hotbeds_list = []
        
        for research_hotbed, user_research_hotbed in research_hotbeds_query:
            # Contar actividades del usuario en este semillero
            activities_count = get_user_activities_count_in_research_hotbed(user_id, research_hotbed.idresearchHotbed)
            
            # Obtener última actividad
            last_activity = get_last_activity_in_research_hotbed(user_id, research_hotbed.idresearchHotbed)
            
            research_hotbed_data = {
                "id": research_hotbed.idresearchHotbed,
                "name": research_hotbed.name_researchHotbed,
                "acronym": research_hotbed.acronym_researchHotbed,
                "university_branch": research_hotbed.universityBranch_researchHotbed,
                "faculty": research_hotbed.faculty_researchHotbed,
                "user_role": user_research_hotbed.TypeUser_usersResearchHotbed,
                "activities_count": activities_count,
                "last_activity": last_activity
            }
            
            research_hotbeds_list.append(research_hotbed_data)

        return jsonify({"research_hotbeds": research_hotbeds_list}), 200

    except Exception as e:
        print(f"Error en get_user_research_hotbeds: {str(e)}")
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500

def get_dashboard_stats(user_id):
    """
    Obtiene las estadísticas del dashboard para el usuario
    """
    try:
        current_semester = get_current_semester()
        
        # Obtener actividades del usuario (como responsable o autor)
        direct_activities = db.session.query(ActivitiesResearchHotbed)\
            .join(UsersResearchHotbed, ActivitiesResearchHotbed.usersResearchHotbed_idusersResearchHotbed == UsersResearchHotbed.idusersResearchHotbed)\
            .filter(UsersResearchHotbed.user_iduser == user_id)\
            .all()

        # Actividades como autor
        authored_activities = db.session.query(ActivitiesResearchHotbed)\
            .join(ActivityAuthors, ActivitiesResearchHotbed.idactivitiesResearchHotbed == ActivityAuthors.activity_id)\
            .join(UsersResearchHotbed, ActivityAuthors.user_research_hotbed_id == UsersResearchHotbed.idusersResearchHotbed)\
            .filter(UsersResearchHotbed.user_iduser == user_id)\
            .all()

        # Combinar y eliminar duplicados
        activity_ids = set()
        all_activities = []
        
        for activity in direct_activities + authored_activities:
            if activity.idactivitiesResearchHotbed not in activity_ids:
                activity_ids.add(activity.idactivitiesResearchHotbed)
                all_activities.append(activity)

        # Estadísticas generales
        total_activities = len(all_activities)
        
        # Actividades del semestre actual
        current_semester_activities = len([
            a for a in all_activities 
            if getattr(a, 'semester', None) == current_semester
        ])
        
        # Actividades pendientes de aprobación (sin horas libres aprobadas)
        pending_approvals = len([
            a for a in all_activities 
            if not a.approvedFreeHours_activitiesResearchHotbed
        ])
        
        # Total de horas libres
        total_free_hours = sum([
            float(a.duration_activitiesResearchHotbed or 0) 
            for a in all_activities 
            if a.approvedFreeHours_activitiesResearchHotbed
        ])

        stats = {
            "total_activities": total_activities,
            "pending_approvals": pending_approvals,
            "this_semester_activities": current_semester_activities,
            "total_free_hours": int(total_free_hours)
        }

        return jsonify(stats), 200

    except Exception as e:
        print(f"Error en get_dashboard_stats: {str(e)}")
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500

def get_user_activities_count_in_research_hotbed(user_id, research_hotbed_id):
    """
    Cuenta las actividades del usuario en un semillero específico
    """
    try:
        # Actividades como responsable directo
        direct_count = db.session.query(ActivitiesResearchHotbed)\
            .join(UsersResearchHotbed, ActivitiesResearchHotbed.usersResearchHotbed_idusersResearchHotbed == UsersResearchHotbed.idusersResearchHotbed)\
            .filter(UsersResearchHotbed.user_iduser == user_id)\
            .filter(UsersResearchHotbed.researchHotbed_idresearchHotbed == research_hotbed_id)\
            .count()

        # Actividades como autor
        authored_count = db.session.query(ActivitiesResearchHotbed)\
            .join(ActivityAuthors, ActivitiesResearchHotbed.idactivitiesResearchHotbed == ActivityAuthors.activity_id)\
            .join(UsersResearchHotbed, ActivityAuthors.user_research_hotbed_id == UsersResearchHotbed.idusersResearchHotbed)\
            .filter(UsersResearchHotbed.user_iduser == user_id)\
            .filter(UsersResearchHotbed.researchHotbed_idresearchHotbed == research_hotbed_id)\
            .count()

        # Para evitar contar duplicados, obtenemos IDs únicos
        direct_ids = db.session.query(ActivitiesResearchHotbed.idactivitiesResearchHotbed)\
            .join(UsersResearchHotbed, ActivitiesResearchHotbed.usersResearchHotbed_idusersResearchHotbed == UsersResearchHotbed.idusersResearchHotbed)\
            .filter(UsersResearchHotbed.user_iduser == user_id)\
            .filter(UsersResearchHotbed.researchHotbed_idresearchHotbed == research_hotbed_id)\
            .all()

        authored_ids = db.session.query(ActivitiesResearchHotbed.idactivitiesResearchHotbed)\
            .join(ActivityAuthors, ActivitiesResearchHotbed.idactivitiesResearchHotbed == ActivityAuthors.activity_id)\
            .join(UsersResearchHotbed, ActivityAuthors.user_research_hotbed_id == UsersResearchHotbed.idusersResearchHotbed)\
            .filter(UsersResearchHotbed.user_iduser == user_id)\
            .filter(UsersResearchHotbed.researchHotbed_idresearchHotbed == research_hotbed_id)\
            .all()

        # Combinar y contar únicos
        unique_ids = set([id[0] for id in direct_ids] + [id[0] for id in authored_ids])
        return len(unique_ids)

    except Exception as e:
        print(f"Error en get_user_activities_count_in_research_hotbed: {str(e)}")
        return 0

def get_last_activity_in_research_hotbed(user_id, research_hotbed_id):
    """
    Obtiene la fecha de la última actividad del usuario en un semillero
    """
    try:
        # Actividades como responsable directo
        direct_activities = db.session.query(ActivitiesResearchHotbed)\
            .join(UsersResearchHotbed, ActivitiesResearchHotbed.usersResearchHotbed_idusersResearchHotbed == UsersResearchHotbed.idusersResearchHotbed)\
            .filter(UsersResearchHotbed.user_iduser == user_id)\
            .filter(UsersResearchHotbed.researchHotbed_idresearchHotbed == research_hotbed_id)\
            .all()

        # Actividades como autor
        authored_activities = db.session.query(ActivitiesResearchHotbed)\
            .join(ActivityAuthors, ActivitiesResearchHotbed.idactivitiesResearchHotbed == ActivityAuthors.activity_id)\
            .join(UsersResearchHotbed, ActivityAuthors.user_research_hotbed_id == UsersResearchHotbed.idusersResearchHotbed)\
            .filter(UsersResearchHotbed.user_iduser == user_id)\
            .filter(UsersResearchHotbed.researchHotbed_idresearchHotbed == research_hotbed_id)\
            .all()

        # Combinar todas las actividades
        all_activities = direct_activities + authored_activities
        
        if not all_activities:
            return None

        # Encontrar la actividad más reciente
        latest_activity = max(all_activities, key=lambda x: x.date_activitiesResearchHotbed if x.date_activitiesResearchHotbed else datetime.min.date())
        
        if latest_activity.date_activitiesResearchHotbed:
            return latest_activity.date_activitiesResearchHotbed.isoformat()
        
        return None

    except Exception as e:
        print(f"Error en get_last_activity_in_research_hotbed: {str(e)}")
        return None