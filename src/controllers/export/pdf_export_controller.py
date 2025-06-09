from flask import jsonify, make_response
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO
from datetime import datetime
import logging

from models.research_hotbed import ResearchHotbed
from models.users_research_hotbed import UsersResearchHotbed
from models.users import User
from models.activities_researchHotbed import ActivitiesResearchHotbed
from models.activity_authors import ActivityAuthors
from db.connection import db
from utils.semester_utils import format_semester_label, format_semester_label_detailed, is_valid_semester

logger = logging.getLogger(__name__)

def export_research_hotbed_pdf(research_hotbed_id, semester):
    """
    Genera un PDF completo del semillero para el semestre especificado
    """
    try:
        # Validaciones
        if not semester or not is_valid_semester(semester):
            return jsonify({"error": "Semestre inválido"}), 400
            
        # Obtener datos del semillero
        research_hotbed = ResearchHotbed.query.get(research_hotbed_id)
        if not research_hotbed:
            return jsonify({"error": "Semillero no encontrado"}), 404
            
        # Obtener miembros activos
        members = get_active_members(research_hotbed_id)
        
        # Obtener actividades del semestre
        activities = get_activities_by_semester(research_hotbed_id, semester)
        
        # Generar PDF
        pdf_buffer = generate_pdf_report(research_hotbed, members, activities, semester)
        
        # Crear respuesta
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{research_hotbed.acronym_researchHotbed}_{semester}_reporte.pdf"'
        
        logger.info(f"PDF generado exitosamente para semillero {research_hotbed_id}, semestre {semester}")
        return response
        
    except Exception as e:
        logger.error(f"Error generando PDF: {str(e)}")
        return jsonify({"error": f"Error generando PDF: {str(e)}"}), 500

def get_active_members(research_hotbed_id):
    """Obtiene miembros activos del semillero"""
    try:
        members_query = db.session.query(User, UsersResearchHotbed).join(
            UsersResearchHotbed, User.iduser == UsersResearchHotbed.user_iduser
        ).filter(
            UsersResearchHotbed.researchHotbed_idresearchHotbed == research_hotbed_id,
            UsersResearchHotbed.status_usersResearchHotbed == 'Activo'
        ).all()
        
        return [{
            'name': user.name_user,
            'email': user.email_user,
            'idSigaa': user.idSigaa_user,
            'type': user_research.TypeUser_usersResearchHotbed,
            'dateEnter': user_research.dateEnter_usersResearchHotbed,
            'status': user_research.status_usersResearchHotbed
        } for user, user_research in members_query]
        
    except Exception as e:
        logger.error(f"Error obteniendo miembros: {str(e)}")
        return []

def get_activities_by_semester(research_hotbed_id, semester):
    """Obtiene actividades filtradas por semestre"""
    try:
        # Extraer año y número de semestre
        semester_parts = semester.split('-')
        if len(semester_parts) != 3:
            return []
            
        semester_number = int(semester_parts[1])
        year = int(semester_parts[2])
        
        # Consulta base de actividades
        activities_query = db.session.query(ActivitiesResearchHotbed).filter(
            ActivitiesResearchHotbed.usersResearchHotbed_idusersResearchHotbed.in_(
                db.session.query(UsersResearchHotbed.idusersResearchHotbed).filter(
                    UsersResearchHotbed.researchHotbed_idresearchHotbed == research_hotbed_id
                )
            )
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
                
                filtered_activities.append({
                    'id': activity.idactivitiesResearchHotbed,
                    'title': activity.title_activitiesResearchHotbed,
                    'responsible': activity.responsible_activitiesResearchHotbed,
                    'date': activity.date_activitiesResearchHotbed,
                    'description': activity.description_activitiesResearchHotbed,
                    'type': activity.type_activitiesResearchHotbed,
                    'duration': activity.duration_activitiesResearchHotbed or 0,
                    'approved_free_hours': bool(activity.approvedFreeHours_activitiesResearchHotbed),
                    'authors': authors_data
                })
                
        return filtered_activities
        
    except Exception as e:
        logger.error(f"Error obteniendo actividades: {str(e)}")
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

def generate_pdf_report(research_hotbed, members, activities, semester):
    """Genera el PDF usando ReportLab"""
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
        textColor=colors.HexColor('#db2777')
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
    title = Paragraph("REPORTE DE SEMILLERO DE INVESTIGACIÓN", title_style)
    story.append(title)
    
    # Información del semillero
    info_style = ParagraphStyle('Info', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER)
    semillero_info = Paragraph(
        f"<b>{research_hotbed.name_researchHotbed} ({research_hotbed.acronym_researchHotbed})</b><br/>"
        f"{format_semester_label_detailed(semester)} | {research_hotbed.faculty_researchHotbed} | {research_hotbed.universityBranch_researchHotbed}",
        info_style
    )
    story.append(semillero_info)
    story.append(Spacer(1, 20))
    
    # Resumen estadístico
    story.append(Paragraph("RESUMEN ESTADÍSTICO", heading_style))
    
    active_members = [m for m in members if m['status'] == 'Activo']
    total_hours = sum(a['duration'] for a in activities)
    approved_activities = len([a for a in activities if a['approved_free_hours']])
    
    stats_data = [
        ['Indicador', 'Valor'],
        ['Total de miembros activos', str(len(active_members))],
        [f'Total de actividades ({format_semester_label(semester)})', str(len(activities))],
        [f'Horas totales registradas', f'{total_hours} horas'],
        ['Actividades con horas libres aprobadas', str(approved_activities)],
        ['Proyectos', str(len([a for a in activities if 'proyecto' in a['type'].lower()]))],
        ['Productos', str(len([a for a in activities if 'producto' in a['type'].lower()]))],
        ['Reconocimientos', str(len([a for a in activities if 'reconocimiento' in a['type'].lower()]))]
    ]
    
    stats_table = Table(stats_data, colWidths=[4*inch, 1.5*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#db2777')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(stats_table)
    story.append(Spacer(1, 20))
    
    # Tabla de miembros
    story.append(Paragraph("MIEMBROS DEL SEMILLERO", heading_style))
    
    if active_members:
        members_data = [['Nombre', 'ID SIGAA', 'Tipo', 'Fecha de Ingreso']]
        for member in active_members:
            members_data.append([
                member['name'],
                member['idSigaa'],
                member['type'],
                member['dateEnter'].strftime('%d/%m/%Y') if member['dateEnter'] else 'N/A'
            ])
        
        members_table = Table(members_data, colWidths=[2.5*inch, 1*inch, 1.5*inch, 1*inch])
        members_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#db2777')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(members_table)
    else:
        story.append(Paragraph("No se encontraron miembros activos.", styles['Normal']))
    
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
                    ['Horas libres aprobadas:', 'Sí' if activity['approved_free_hours'] else 'No']
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
                    ('VALIGN', (0, 0), (-1, -1), 'TOP')
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