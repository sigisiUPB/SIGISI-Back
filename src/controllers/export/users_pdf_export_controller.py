from flask import jsonify, make_response
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime
import logging

from models.users import User
from models.users_research_hotbed import UsersResearchHotbed
from models.research_hotbed import ResearchHotbed
from models.activities_researchHotbed import ActivitiesResearchHotbed
from models.activity_authors import ActivityAuthors
from db.connection import db
from utils.semester_utils import format_semester_label_detailed, is_valid_semester

logger = logging.getLogger(__name__)

def export_user_pdf(user_id, semester):
    """
    Genera un PDF individual para un usuario específico
    """
    try:
        # Validaciones
        if not semester or not is_valid_semester(semester):
            return jsonify({"error": "Semestre inválido"}), 400
            
        # Obtener usuario
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        # Obtener datos del usuario
        research_hotbeds = get_user_research_hotbeds(user_id)
        activities = get_user_activities_by_semester(user_id, semester)
        
        # Generar PDF
        pdf_buffer = generate_user_pdf_report(user, research_hotbeds, activities, semester)
        
        # Crear respuesta
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{user.idSigaa_user}_{user.name_user.replace(" ", "_")}_{semester}.pdf"'
        
        logger.info(f"PDF generado exitosamente para usuario {user_id}, semestre {semester}")
        return response
        
    except Exception as e:
        logger.error(f"Error generando PDF de usuario: {str(e)}")
        return jsonify({"error": f"Error generando PDF: {str(e)}"}), 500

def export_multiple_users_pdf(user_ids, semester):
    """
    Genera un PDF consolidado con múltiples usuarios
    """
    try:
        # Validaciones
        if not semester or not is_valid_semester(semester):
            return jsonify({"error": "Semestre inválido"}), 400
            
        if not user_ids or len(user_ids) == 0:
            return jsonify({"error": "No se especificaron usuarios"}), 400
            
        # Obtener usuarios
        users = User.query.filter(User.iduser.in_(user_ids)).all()
        if not users:
            return jsonify({"error": "No se encontraron usuarios"}), 404
            
        # Generar PDF consolidado
        pdf_buffer = generate_consolidated_users_pdf(users, semester)
        
        # Crear respuesta
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="usuarios_consolidado_{semester}.pdf"'
        
        logger.info(f"PDF consolidado generado exitosamente para {len(users)} usuarios, semestre {semester}")
        return response
        
    except Exception as e:
        logger.error(f"Error generando PDF consolidado: {str(e)}")
        return jsonify({"error": f"Error generando PDF: {str(e)}"}), 500

def get_user_research_hotbeds(user_id):
    """Obtiene los semilleros asociados al usuario"""
    try:
        hotbeds_query = db.session.query(ResearchHotbed, UsersResearchHotbed).join(
            UsersResearchHotbed, ResearchHotbed.idresearchHotbed == UsersResearchHotbed.researchHotbed_idresearchHotbed
        ).filter(
            UsersResearchHotbed.user_iduser == user_id
        ).all()
        
        return [{
            'name': hotbed.name_researchHotbed,
            'acronym': hotbed.acronym_researchHotbed,
            'faculty': hotbed.faculty_researchHotbed,
            'universityBranch': hotbed.universityBranch_researchHotbed,
            'type': user_research.TypeUser_usersResearchHotbed,
            'status': user_research.status_usersResearchHotbed,
            'dateEnter': user_research.dateEnter_usersResearchHotbed
        } for hotbed, user_research in hotbeds_query]
        
    except Exception as e:
        logger.error(f"Error obteniendo semilleros del usuario: {str(e)}")
        return []

def get_user_activities_by_semester(user_id, semester):
    """Obtiene actividades del usuario filtradas por semestre"""
    try:
        # Extraer año y número de semestre
        semester_parts = semester.split('-')
        if len(semester_parts) != 3:
            return []
            
        semester_number = int(semester_parts[1])
        year = int(semester_parts[2])
        
        # Obtener IDs de semilleros del usuario
        user_research_ids = db.session.query(UsersResearchHotbed.idusersResearchHotbed).filter(
            UsersResearchHotbed.user_iduser == user_id
        ).subquery()
        
        # Consulta base de actividades
        activities_query = db.session.query(ActivitiesResearchHotbed).filter(
            ActivitiesResearchHotbed.usersResearchHotbed_idusersResearchHotbed.in_(user_research_ids)
        ).all()
        
        # Filtrar por semestre
        filtered_activities = []
        for activity in activities_query:
            activity_date = activity.date_activitiesResearchHotbed
            activity_year = activity_date.year
            activity_month = activity_date.month
            
            # Determinar semestre (1: Enero-Junio, 2: Julio-Diciembre)
            activity_semester = 1 if activity_month <= 6 else 2
            
            if activity_year == year and activity_semester == semester_number:
                # Obtener autores
                authors_data = get_activity_authors(activity.idactivitiesResearchHotbed)
                
                # Obtener nombre del semillero
                research_hotbed_name = get_research_hotbed_name(activity.usersResearchHotbed_idusersResearchHotbed)
                
                filtered_activities.append({
                    'id': activity.idactivitiesResearchHotbed,
                    'title': activity.title_activitiesResearchHotbed,
                    'responsible': activity.responsible_activitiesResearchHotbed,
                    'date': activity.date_activitiesResearchHotbed,
                    'description': activity.description_activitiesResearchHotbed,
                    'type': activity.type_activitiesResearchHotbed,
                    'duration': activity.duration_activitiesResearchHotbed or 0,
                    'approved_free_hours': bool(activity.approvedFreeHours_activitiesResearchHotbed),
                    'authors': authors_data,
                    'research_hotbed_name': research_hotbed_name
                })
                
        return filtered_activities
        
    except Exception as e:
        logger.error(f"Error obteniendo actividades del usuario: {str(e)}")
        return []

def get_activity_authors(activity_id):
    """Obtiene los autores de una actividad"""
    try:
        authors_query = db.session.query(User, ActivityAuthors).join(
            UsersResearchHotbed, ActivityAuthors.user_research_hotbed_id == UsersResearchHotbed.idusersResearchHotbed
        ).join(
            User, UsersResearchHotbed.user_iduser == User.iduser
        ).filter(
            ActivityAuthors.activity_id == activity_id
        ).all()
        
        main_authors = []
        co_authors = []
        
        for user, author_relation in authors_query:
            if author_relation.is_main_author:
                main_authors.append(user.name_user)
            else:
                co_authors.append(user.name_user)
                
        return {
            'main_authors': main_authors,
            'co_authors': co_authors
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo autores: {str(e)}")
        return {'main_authors': [], 'co_authors': []}

def get_research_hotbed_name(user_research_hotbed_id):
    """Obtiene el nombre del semillero por ID de user_research_hotbed"""
    try:
        result = db.session.query(ResearchHotbed.name_researchHotbed).join(
            UsersResearchHotbed, ResearchHotbed.idresearchHotbed == UsersResearchHotbed.researchHotbed_idresearchHotbed
        ).filter(
            UsersResearchHotbed.idusersResearchHotbed == user_research_hotbed_id
        ).first()
        
        return result[0] if result else 'Semillero no especificado'
        
    except Exception as e:
        logger.error(f"Error obteniendo nombre del semillero: {str(e)}")
        return 'Semillero no especificado'

def generate_user_pdf_report(user, research_hotbeds, activities, semester):
    """Genera el PDF individual del usuario usando ReportLab"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2563eb')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.HexColor('#374151')
    )
    
    # Contenido del PDF
    story = []
    
    # Título principal
    title = Paragraph("REPORTE INDIVIDUAL DE USUARIO", title_style)
    story.append(title)
    
    # Información del usuario
    info_style = ParagraphStyle('Info', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER)
    user_info = Paragraph(
        f"<b>{user.name_user}</b><br/>"
        f"{format_semester_label_detailed(semester)} | SIGISI - Sistema de Gestión de Semilleros",
        info_style
    )
    story.append(user_info)
    story.append(Spacer(1, 20))
    
    # Información personal
    story.append(Paragraph("INFORMACIÓN PERSONAL", heading_style))
    
    personal_data = [
        ['Nombre completo:', user.name_user],
        ['ID SIGAA:', user.idSigaa_user or 'Sin especificar'],
        ['Correo electrónico:', user.email_user],
        ['Programa académico:', user.academicProgram_user or 'Sin especificar'],
        ['Tipo de usuario:', user.type_user],
        ['Estado:', user.status_user],
        ['Fecha de reporte:', datetime.now().strftime('%d/%m/%Y')]
    ]
    
    personal_table = Table(personal_data, colWidths=[3*inch, 3*inch])
    personal_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#374151'))
    ]))
    
    story.append(personal_table)
    story.append(Spacer(1, 20))
    
    # Semilleros de investigación
    story.append(Paragraph("SEMILLEROS DE INVESTIGACIÓN", heading_style))
    
    if research_hotbeds:
        hotbeds_data = [['Semillero', 'Acrónimo', 'Facultad', 'Rol', 'Estado', 'Fecha Ingreso']]
        for hotbed in research_hotbeds:
            hotbeds_data.append([
                hotbed['name'],
                hotbed['acronym'],
                hotbed['faculty'],
                hotbed['type'],
                hotbed['status'],
                hotbed['dateEnter'].strftime('%d/%m/%Y') if hotbed['dateEnter'] else 'N/A'
            ])
        
        hotbeds_table = Table(hotbeds_data, colWidths=[2*inch, 0.8*inch, 1.5*inch, 1*inch, 0.8*inch, 1*inch])
        hotbeds_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8)
        ]))
        
        story.append(hotbeds_table)
    else:
        no_hotbeds = Paragraph("No está asociado a ningún semillero de investigación.", styles['Normal'])
        story.append(no_hotbeds)
    
    story.append(Spacer(1, 20))
    
    # Resumen de actividades
    story.append(Paragraph(f"RESUMEN DE ACTIVIDADES - {format_semester_label_detailed(semester)}", heading_style))
    
    total_hours = sum(a['duration'] for a in activities)
    approved_activities = len([a for a in activities if a['approved_free_hours']])
    
    stats_data = [
        ['Indicador', 'Valor'],
        ['Total de actividades reportadas', str(len(activities))],
        ['Horas totales registradas', f'{total_hours} horas'],
        ['Actividades con horas libres aprobadas', str(approved_activities)],
        ['Actividades pendientes de aprobación', str(len(activities) - approved_activities)],
        ['Proyectos', str(len([a for a in activities if 'proyecto' in a['type'].lower()]))],
        ['Productos', str(len([a for a in activities if 'producto' in a['type'].lower()]))],
        ['Reconocimientos', str(len([a for a in activities if 'reconocimiento' in a['type'].lower()]))]
    ]
    
    stats_table = Table(stats_data, colWidths=[4*inch, 1.5*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('TEXTCOLOR', (1, 1), (1, -1), colors.HexColor('#2563eb'))
    ]))
    
    story.append(stats_table)
    story.append(PageBreak())
    
    # Actividades detalladas
    story.append(Paragraph(f"ACTIVIDADES DETALLADAS - {format_semester_label_detailed(semester)}", heading_style))
    
    if activities:
        # Agrupar por tipo
        activity_types = list(set(a['type'] for a in activities))
        
        for activity_type in activity_types:
            type_activities = [a for a in activities if a['type'] == activity_type]
            
            story.append(Paragraph(f"{activity_type.upper()} ({len(type_activities)})", heading_style))
            
            for i, activity in enumerate(type_activities, 1):
                # Título de la actividad
                activity_title = Paragraph(f"{i}. {activity['title']}", styles['Heading2'])
                story.append(activity_title)
                
                # Información básica
                info_data = [
                    ['Responsable:', activity['responsible']],
                    ['Fecha:', activity['date'].strftime('%d/%m/%Y')],
                    ['Duración:', f"{activity['duration']} horas"],
                    ['Horas libres aprobadas:', 'Sí' if activity['approved_free_hours'] else 'No'],
                    ['Semillero:', activity['research_hotbed_name']]
                ]
                
                if activity['authors']['main_authors']:
                    info_data.append(['Autores principales:', ', '.join(activity['authors']['main_authors'])])
                
                if activity['authors']['co_authors']:
                    info_data.append(['Co-autores:', ', '.join(activity['authors']['co_authors'])])
                
                info_table = Table(info_data, colWidths=[2*inch, 4*inch])
                info_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280'))
                ]))
                
                story.append(info_table)
                story.append(Spacer(1, 10))
                
                # Descripción
                if activity['description']:
                    desc_style = ParagraphStyle('Description', parent=styles['Normal'], fontSize=9)
                    description = Paragraph(f"<b>Descripción:</b> {activity['description']}", desc_style)
                    story.append(description)
                
                story.append(Spacer(1, 15))
                
    else:
        no_activities = Paragraph(f"No se encontraron actividades para {format_semester_label_detailed(semester)}.", styles['Normal'])
        story.append(no_activities)
    
    # Generar PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer

def generate_consolidated_users_pdf(users, semester):
    """Genera un PDF consolidado con múltiples usuarios"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2563eb')
    )
    
    # Contenido del PDF
    story = []
    
    # Título principal
    title = Paragraph("REPORTE CONSOLIDADO DE USUARIOS", title_style)
    story.append(title)
    
    # Información general
    info_style = ParagraphStyle('Info', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER)
    general_info = Paragraph(
        f"{format_semester_label_detailed(semester)} | {len(users)} usuarios<br/>"
        f"SIGISI - Sistema de Gestión de Semilleros",
        info_style
    )
    story.append(general_info)
    story.append(Spacer(1, 30))
    
    # Tabla consolidada de usuarios
    users_data = [['#', 'Nombre', 'ID SIGAA', 'Email', 'Programa', 'Tipo', 'Actividades', 'Horas']]
    
    for i, user in enumerate(users, 1):
        activities = get_user_activities_by_semester(user.iduser, semester)
        total_hours = sum(a['duration'] for a in activities)
        
        users_data.append([
            str(i),
            user.name_user,
            user.idSigaa_user or 'N/A',
            user.email_user,
            user.academicProgram_user or 'N/A',
            user.type_user,
            str(len(activities)),
            f'{total_hours}h'
        ])
    
    users_table = Table(users_data, colWidths=[0.3*inch, 1.8*inch, 0.8*inch, 1.5*inch, 1.2*inch, 0.8*inch, 0.6*inch, 0.6*inch])
    users_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('ALIGN', (3, 1), (3, -1), 'LEFT'),
        ('ALIGN', (4, 1), (4, -1), 'LEFT')
    ]))
    
    story.append(users_table)
    
    # Generar PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer