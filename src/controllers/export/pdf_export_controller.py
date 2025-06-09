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

from models.research_hotbed import ResearchHotbed
from models.users_research_hotbed import UsersResearchHotbed
from models.users import User
from models.activities_researchHotbed import ActivitiesResearchHotbed
from models.activity_authors import ActivityAuthors
from db.connection import db
from utils.semester_utils import format_semester_label_detailed, is_valid_semester

logger = logging.getLogger(__name__)

# ESTILOS GLOBALES ESTANDARIZADOS CON COLORES DE LA APP
def get_standard_styles():
    """Estilos estandarizados para todos los PDFs con colores de la aplicación"""
    styles = getSampleStyleSheet()
    
    return {
        'title': ParagraphStyle(
            'StandardTitle',
            parent=styles['Title'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1f2937'),
            fontName='Helvetica-Bold'
        ),
        'heading': ParagraphStyle(
            'StandardHeading',
            parent=styles['Heading1'],
            fontSize=12,
            spaceAfter=12,
            textColor=colors.HexColor('#7c2d92'),  # Morado de la app
            fontName='Helvetica-Bold'
        ),
        'subheading': ParagraphStyle(
            'StandardSubheading',
            parent=styles['Heading2'],
            fontSize=10,
            spaceAfter=8,
            textColor=colors.HexColor('#be185d'),  # Rosa de la app
            fontName='Helvetica-Bold'
        ),
        'normal': ParagraphStyle(
            'StandardNormal',
            parent=styles['Normal'],
            fontSize=9,
            leading=11,
            textColor=colors.HexColor('#374151')
        ),
        'small': ParagraphStyle(
            'StandardSmall',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#6b7280')
        )
    }

def get_standard_table_style():
    """Estilo estandarizado para tablas con colores de la app"""
    return TableStyle([
        # Header - Rosa/Morado degradado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d946ef')),  # Rosa vibrante
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        
        # Body
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fdf2f8')),  # Rosa muy claro
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#f3e8ff')),  # Lila claro
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8)
    ])

def get_info_table_style():
    """Estilo para tablas de información con colores de la app"""
    return TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#a21caf')),  # Morado medio
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#374151')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#f3e8ff')),  # Lila claro
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fdf2f8')),  # Rosa muy claro
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
    ])

def get_stats_table_style():
    """Estilo para tablas de estadísticas con colores de la app"""
    return TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#c026d3')),  # Rosa fuerte
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fae8ff')),  # Lila muy claro
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#be185d')),  # Rosa fuerte
        ('TEXTCOLOR', (3, 0), (3, -1), colors.HexColor('#be185d')),  # Rosa fuerte
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
    ])

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
    """Obtiene TODOS los miembros del semillero (activos e inactivos)"""
    try:
        # CAMBIO: Eliminar filtro de status para mostrar todos los miembros
        members_query = db.session.query(User, UsersResearchHotbed).join(
            UsersResearchHotbed, User.iduser == UsersResearchHotbed.user_iduser
        ).filter(
            UsersResearchHotbed.researchHotbed_idresearchHotbed == research_hotbed_id
            # Removido: UsersResearchHotbed.status_usersResearchHotbed == 'Activo'
        ).order_by(
            # Activos primero (Activo = 1, otros = 0), luego alfabético
            (UsersResearchHotbed.status_usersResearchHotbed == 'Activo').desc(),
            User.name_user.asc()
        ).all()
        
        return [{
            'name': user.name_user,
            'email': user.email_user,
            'idSigaa': user.idSigaa_user,
            'type': user_research.TypeUser_usersResearchHotbed,
            'dateEnter': user_research.dateEnter_usersResearchHotbed,
            'dateExit': user_research.dateExit_usersResearchHotbed,  # Campo que SÍ existe
            'observation': user_research.observation_usersResearchHotbed,  # Usar observation en lugar de exitReason
            'status': user_research.status_usersResearchHotbed
        } for user, user_research in members_query]
        
    except Exception as e:
        logger.error(f"Error obteniendo miembros: {str(e)}")
        return []

def get_activities_by_semester(research_hotbed_id, semester):
    """Obtiene actividades filtradas por semestre usando el campo 'semester' de la actividad"""
    try:
        # Consulta base de actividades filtradas por el campo semester
        activities_query = db.session.query(ActivitiesResearchHotbed).filter(
            ActivitiesResearchHotbed.usersResearchHotbed_idusersResearchHotbed.in_(
                db.session.query(UsersResearchHotbed.idusersResearchHotbed).filter(
                    UsersResearchHotbed.researchHotbed_idresearchHotbed == research_hotbed_id
                )
            ),
            ActivitiesResearchHotbed.semester == semester  # Filtrar por el campo semester
        ).all()
        
        # Procesar actividades
        filtered_activities = []
        for activity in activities_query:
            # Obtener autores
            authors_data = get_activity_authors(activity.idactivitiesResearchHotbed)
            
            activity_data = {
                'id': activity.idactivitiesResearchHotbed,
                'title': activity.title_activitiesResearchHotbed,
                'responsible': activity.responsible_activitiesResearchHotbed,
                'date': activity.date_activitiesResearchHotbed,
                'description': activity.description_activitiesResearchHotbed,
                'type': activity.type_activitiesResearchHotbed,
                'duration': activity.duration_activitiesResearchHotbed or 0,
                'start_time': activity.startTime_activitiesResearchHotbed,
                'end_time': activity.endTime_activitiesResearchHotbed,
                'approved_free_hours': bool(activity.approvedFreeHours_activitiesResearchHotbed),
                'reference_number': getattr(activity, 'reference_number', None),
                'publication_date': getattr(activity, 'publication_date', None),
                'organization_name': getattr(activity, 'organization_name', None),
                'authors': authors_data
            }
            
            # Obtener datos específicos según el tipo
            if (activity.type_activitiesResearchHotbed and 
                activity.type_activitiesResearchHotbed.lower() == 'proyecto' and 
                activity.projectsResearchHotbed_idprojectsResearchHotbed):
                
                from models.projects_researchHotbed import ProjectsResearchHotbed
                project = db.session.query(ProjectsResearchHotbed).filter_by(
                    idprojectsResearchHotbed=activity.projectsResearchHotbed_idprojectsResearchHotbed
                ).first()
                if project:
                    activity_data['project_data'] = {
                        'name': project.name_projectsResearchHotbed or 'Sin especificar',
                        'reference_number': project.referenceNumber_projectsResearchHotbed,
                        'start_date': project.startDate_projectsResearchHotbed,
                        'end_date': project.endDate_projectsResearchHotbed
                    }
            
            elif (activity.type_activitiesResearchHotbed and 
                  activity.type_activitiesResearchHotbed.lower() == 'producto' and 
                  activity.productsResearchHotbed_idproductsResearchHotbed):
                
                from models.products_researchHotbed import ProductsResearchHotbed
                product = db.session.query(ProductsResearchHotbed).filter_by(
                    idproductsResearchHotbed=activity.productsResearchHotbed_idproductsResearchHotbed
                ).first()
                if product:
                    activity_data['product_data'] = {
                        'category': product.category_productsResearchHotbed,
                        'type': product.type_productsResearchHotbed,
                        'description': product.description_productsResearchHotbed
                    }
            
            elif (activity.type_activitiesResearchHotbed and 
                  activity.type_activitiesResearchHotbed.lower() == 'reconocimiento' and 
                  activity.recognitionsResearchHotbed_idrecognitionsResearchHotbed):
                
                from models.recognitions_researchHotbed import RecognitionsResearchHotbed
                recognition = db.session.query(RecognitionsResearchHotbed).filter_by(
                    idrecognitionsResearchHotbed=activity.recognitionsResearchHotbed_idrecognitionsResearchHotbed
                ).first()
                if recognition:
                    activity_data['recognition_data'] = {
                        'project_name': recognition.projectName_recognitionsResearchHotbed,
                        'organization_name': recognition.organizationName_recognitionsResearchHotbed
                    }
            
            filtered_activities.append(activity_data)
                
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
    """Genera el PDF usando estilos con colores de la app"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        topMargin=0.8*inch, 
        bottomMargin=0.8*inch, 
        leftMargin=0.7*inch, 
        rightMargin=0.7*inch
    )
    
    # Obtener estilos estandarizados
    std_styles = get_standard_styles()
    story = []
    
    # Título principal con colores de la app
    title = Paragraph("REPORTE DE SEMILLERO DE INVESTIGACIÓN", std_styles['title'])
    story.append(title)
    story.append(Spacer(1, 10))
    
    # Subtítulo con información del semillero en colores de la app
    semillero_info = Paragraph(
        f"<b><font color='#be185d'>{research_hotbed.name_researchHotbed} ({research_hotbed.acronym_researchHotbed})</font></b><br/>"
        f"<font color='#7c2d92'>{format_semester_label_detailed(semester)} | {research_hotbed.faculty_researchHotbed} | {research_hotbed.universityBranch_researchHotbed}</font>",
        std_styles['normal']
    )
    semillero_info.alignment = TA_CENTER
    story.append(semillero_info)
    story.append(Spacer(1, 20))
    
    # Información del semillero
    info_data = [
        ['Semillero:', research_hotbed.name_researchHotbed],
        ['Acrónimo:', research_hotbed.acronym_researchHotbed],
        ['Facultad:', research_hotbed.faculty_researchHotbed],
        ['Sede:', research_hotbed.universityBranch_researchHotbed],
        ['Semestre:', format_semester_label_detailed(semester)],
        ['Fecha de reporte:', datetime.now().strftime('%d/%m/%Y %H:%M')]
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4.5*inch])
    info_table.setStyle(get_info_table_style())
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # Resumen estadístico - ACTUALIZADO para mostrar activos e inactivos
    story.append(Paragraph("RESUMEN ESTADÍSTICO", std_styles['heading']))
    
    # Usar el mismo criterio de filtrado que en la tabla
    active_members = [m for m in members if m['status'] == 'Activo']
    inactive_members = [m for m in members if m['status'] != 'Activo']
    total_hours = sum(a['duration'] for a in activities)
    approved_activities = len([a for a in activities if a['approved_free_hours']])
    
    stats_data = [
        ['Total miembros', str(len(members)), 'Miembros activos', str(len(active_members))],
        ['Miembros inactivos', str(len(inactive_members)), 'Horas totales', f'{total_hours}h'],
        ['Total actividades', str(len(activities)), 'Actividades aprobadas', str(approved_activities)],
        ['Proyectos', str(len([a for a in activities if 'proyecto' in a['type'].lower()])), 'Productos', str(len([a for a in activities if 'producto' in a['type'].lower()]))],
        ['Reconocimientos', str(len([a for a in activities if 'reconocimiento' in a['type'].lower()])), 'Pendientes', str(len(activities) - approved_activities)]
    ]
    
    stats_table = Table(stats_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 1*inch])
    stats_table.setStyle(get_stats_table_style())
    story.append(stats_table)
    story.append(Spacer(1, 20))
    
    # Tabla de miembros - MOSTRAR TODOS CON STATUS, FECHA DE SALIDA Y OBSERVACIÓN
    story.append(Paragraph("MIEMBROS DEL SEMILLERO", std_styles['heading']))
    
    if members:
        # Separar activos e inactivos para mostrar activos primero
        active_members = [m for m in members if m['status'] == 'Activo']
        inactive_members = [m for m in members if m['status'] != 'Activo']
        sorted_members = active_members + inactive_members
        
        # Incluir columnas para fecha de salida y observación
        members_data = [['Nombre', 'ID SIGAA', 'Tipo', 'Estado', 'F. Ingreso', 'F. Salida', 'Observación']]
        
        for member in sorted_members:
            name = member['name'][:18] + '...' if len(member['name']) > 18 else member['name']
            type_user = member['type'][:8] + '...' if len(member['type']) > 8 else member['type']
            
            # Formatear fechas
            date_enter = member['dateEnter'].strftime('%m/%Y') if member['dateEnter'] else 'N/A'
            date_exit = member['dateExit'].strftime('%m/%Y') if member['dateExit'] else '-'
            
            # Formatear observación
            observation = ''
            if member['observation']:
                observation = member['observation'][:12] + '...' if len(member['observation']) > 12 else member['observation']
            else:
                observation = '-' if member['status'] == 'Activo' else 'Sin observación'
            
            members_data.append([
                name,
                member['idSigaa'] or 'N/A',
                type_user,
                member['status'],
                date_enter,
                date_exit,
                observation
            ])
        
        # Ajustar anchos de columna para incluir nuevos campos
        # Reducir algunos anchos para hacer espacio para fecha de salida y observación
        members_table = Table(members_data, colWidths=[1.4*inch, 0.8*inch, 0.8*inch, 0.6*inch, 0.6*inch, 0.6*inch, 1.0*inch])
        
        # Estilo con colores diferentes para activos/inactivos
        table_style = get_standard_table_style()
        
        # Agregar colores especiales para miembros inactivos
        for row_idx, member in enumerate(sorted_members, 1):  # Saltar header, empezar desde 1
            if member['status'] != 'Activo':  # Si no es activo
                table_style.add('BACKGROUND', (0, row_idx), (-1, row_idx), colors.HexColor('#fee2e2'))  # Fondo rojo claro
                table_style.add('TEXTCOLOR', (0, row_idx), (-1, row_idx), colors.HexColor('#7f1d1d'))  # Texto rojo oscuro
        
        # Ajustar alineación para las columnas de fecha
        table_style.add('ALIGN', (4, 0), (5, -1), 'CENTER')  # Centrar fechas
        table_style.add('FONTSIZE', (0, 0), (-1, -1), 7)  # Reducir tamaño de fuente para que quepa todo
        
        members_table.setStyle(table_style)
        story.append(members_table)
        
    else:
        story.append(Paragraph("No se encontraron miembros en este semillero.", std_styles['normal']))
    
    story.append(PageBreak())
    
    # Actividades detalladas
    story.append(Paragraph(f"ACTIVIDADES DETALLADAS - {format_semester_label_detailed(semester)}", std_styles['heading']))
    
    if activities:
        # Agrupar por tipo
        activity_types = list(set(a['type'] for a in activities))
        
        for activity_type in activity_types:
            type_activities = [a for a in activities if a['type'] == activity_type]
            
            story.append(Paragraph(f"{activity_type.upper()} ({len(type_activities)})", std_styles['subheading']))
            
            for i, activity in enumerate(type_activities, 1):
                # Información básica - SIN CATEGORÍA
                basic_info = [
                    ['Título:', activity['title'][:50] + '...' if len(activity['title']) > 50 else activity['title']],
                    ['Fecha:', activity['date'].strftime('%d/%m/%Y')],
                    ['Duración:', f"{activity['duration']} horas"],
                    ['Horario:', f"{activity['start_time']} - {activity['end_time']}" if activity['start_time'] and activity['end_time'] else 'No especificado'],
                    ['Horas libres:', 'Aprobadas' if activity['approved_free_hours'] else 'Pendientes']
                ]
                
                # Datos adicionales según disponibilidad
                if activity['reference_number']:
                    basic_info.append(['Número de referencia:', activity['reference_number']])
                
                if activity['publication_date']:
                    basic_info.append(['Fecha publicación:', activity['publication_date'].strftime('%d/%m/%Y')])
                
                if activity['organization_name']:
                    basic_info.append(['Organización:', activity['organization_name']])
                
                # Información específica según el tipo - SIN INVESTIGADORES EN PROYECTOS
                if 'project_data' in activity:
                    project = activity['project_data']
                    basic_info.append(['DATOS DEL PROYECTO', ''])
                    basic_info.extend([
                        ['Nombre proyecto:', project['name'][:40] + '...' if len(project['name']) > 40 else project['name']],
                        ['Ref. proyecto:', project['reference_number']],
                        ['Fecha inicio:', project['start_date'].strftime('%d/%m/%Y') if project['start_date'] else 'N/A'],
                        ['Fecha fin:', project['end_date'].strftime('%d/%m/%Y') if project['end_date'] else 'N/A']
                    ])
                
                elif 'product_data' in activity:
                    product = activity['product_data']
                    basic_info.append(['DATOS DEL PRODUCTO', ''])
                    basic_info.extend([
                        ['Categoría producto:', product['category']],
                        ['Tipo producto:', product['type']],
                        ['Descripción producto:', product['description'][:60] + '...' if len(product['description']) > 60 else product['description']]
                    ])
                
                elif 'recognition_data' in activity:
                    recognition = activity['recognition_data']
                    basic_info.append(['DATOS DEL RECONOCIMIENTO', ''])
                    basic_info.extend([
                        ['Proyecto reconocido:', recognition['project_name'][:40] + '...' if len(recognition['project_name']) > 40 else recognition['project_name']],
                        ['Organización otorgante:', recognition['organization_name'][:40] + '...' if len(recognition['organization_name']) > 40 else recognition['organization_name']]
                    ])
                
                # Autores (MANTENER SOLO ESTAS SECCIONES)
                if activity['authors']['main_authors']:
                    authors_text = ', '.join(activity['authors']['main_authors'])
                    if len(authors_text) > 50:
                        authors_text = authors_text[:50] + '...'
                    basic_info.append(['Autores principales:', authors_text])
                
                if activity['authors']['co_authors']:
                    co_authors_text = ', '.join(activity['authors']['co_authors'])
                    if len(co_authors_text) > 50:
                        co_authors_text = co_authors_text[:50] + '...'
                    basic_info.append(['Co-autores:', co_authors_text])
                
                # Crear tabla de información con estilo especial para separadores
                info_table = Table(basic_info, colWidths=[1.8*inch, 4.7*inch])
                
                # Estilo base
                table_style = get_info_table_style()
                
                # Agregar estilo especial para separadores
                for row_idx, row in enumerate(basic_info):
                    if row[0].startswith('DATOS DEL'):
                        table_style.add('BACKGROUND', (0, row_idx), (-1, row_idx), colors.HexColor('#e879f9'))  # Rosa medio
                        table_style.add('TEXTCOLOR', (0, row_idx), (-1, row_idx), colors.white)
                        table_style.add('FONTNAME', (0, row_idx), (-1, row_idx), 'Helvetica-Bold')
                        table_style.add('ALIGN', (0, row_idx), (-1, row_idx), 'CENTER')
                
                info_table.setStyle(table_style)
                story.append(info_table)
                
                # Descripción completa
                if activity['description']:
                    story.append(Spacer(1, 8))
                    desc_paragraph = Paragraph(f"<b><font color='#be185d'>Descripción:</font></b> {activity['description']}", std_styles['small'])
                    story.append(desc_paragraph)
                
                story.append(Spacer(1, 15))
                
    else:
        no_activities = Paragraph(f"No se encontraron actividades para {format_semester_label_detailed(semester)}.", std_styles['normal'])
        story.append(no_activities)
    
    # Generar PDF
    doc.build(story)
    buffer.seek(0)
    return buffer