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
    """Obtiene actividades del usuario filtradas por semestre usando el campo 'semester' - INCLUYE ACTIVIDADES COMO CO-AUTOR"""
    try:
        # Obtener IDs de semilleros del usuario
        user_research_ids = db.session.query(UsersResearchHotbed.idusersResearchHotbed).filter(
            UsersResearchHotbed.user_iduser == user_id
        ).subquery()
        
        # OPCIÓN 1: Actividades donde el usuario está directamente asociado al semillero
        direct_activities = db.session.query(ActivitiesResearchHotbed).filter(
            ActivitiesResearchHotbed.usersResearchHotbed_idusersResearchHotbed.in_(user_research_ids),
            ActivitiesResearchHotbed.semester == semester
        )
        
        # OPCIÓN 2: Actividades donde el usuario es autor/co-autor (a través de ActivityAuthors)
        authored_activities = db.session.query(ActivitiesResearchHotbed).join(
            ActivityAuthors, ActivitiesResearchHotbed.idactivitiesResearchHotbed == ActivityAuthors.activity_id
        ).filter(
            ActivityAuthors.user_research_hotbed_id.in_(user_research_ids),
            ActivitiesResearchHotbed.semester == semester
        )
        
        # Combinar ambas consultas y eliminar duplicados
        all_activities_query = direct_activities.union(authored_activities).all()
        
        # Procesar actividades
        filtered_activities = []
        processed_ids = set()  # Para evitar duplicados
        
        for activity in all_activities_query:
            # Evitar duplicados
            if activity.idactivitiesResearchHotbed in processed_ids:
                continue
            processed_ids.add(activity.idactivitiesResearchHotbed)
            
            # Obtener autores
            authors_data = get_activity_authors(activity.idactivitiesResearchHotbed)
            
            # Obtener nombre del semillero
            research_hotbed_name = get_research_hotbed_name(activity.usersResearchHotbed_idusersResearchHotbed)
            
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
                'authors': authors_data,
                'research_hotbed_name': research_hotbed_name
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
    """Genera el PDF individual del usuario con colores de la app"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        topMargin=0.8*inch, 
        bottomMargin=0.8*inch, 
        leftMargin=0.7*inch, 
        rightMargin=0.7*inch
    )
    
    # Importar estilos del controlador principal
    from controllers.export.pdf_export_controller import get_standard_styles, get_info_table_style, get_standard_table_style, get_stats_table_style
    
    # Obtener estilos estandarizados
    std_styles = get_standard_styles()
    story = []
    
    # Título principal
    title = Paragraph("REPORTE INDIVIDUAL DE USUARIO", std_styles['title'])
    story.append(title)
    story.append(Spacer(1, 10))
    
    # Información del usuario con colores de la app
    user_info = Paragraph(
        f"<b><font color='#be185d'>{user.name_user}</font></b><br/>"
        f"<font color='#7c2d92'>{format_semester_label_detailed(semester)} | SIGISI - Sistema de Gestión de Semilleros</font>",
        std_styles['normal']
    )
    user_info.alignment = TA_CENTER
    story.append(user_info)
    story.append(Spacer(1, 20))
    
    # Información personal
    story.append(Paragraph("INFORMACIÓN PERSONAL", std_styles['heading']))
    
    personal_data = [
        ['Nombre completo:', user.name_user],
        ['ID SIGAA:', user.idSigaa_user or 'Sin especificar'],
        ['Correo electrónico:', user.email_user],
        ['Programa académico:', user.academicProgram_user[:50] + '...' if user.academicProgram_user and len(user.academicProgram_user) > 50 else user.academicProgram_user or 'Sin especificar'],
        ['Tipo de usuario:', user.type_user],
        ['Estado:', user.status_user],
        ['Fecha de reporte:', datetime.now().strftime('%d/%m/%Y %H:%M')]
    ]
    
    personal_table = Table(personal_data, colWidths=[2*inch, 4.5*inch])
    personal_table.setStyle(get_info_table_style())
    story.append(personal_table)
    story.append(Spacer(1, 20))
    
    # Semilleros de investigación
    story.append(Paragraph("SEMILLEROS DE INVESTIGACIÓN", std_styles['heading']))
    
    if research_hotbeds:
        hotbeds_data = [['Semillero', 'Acrónimo', 'Facultad', 'Rol', 'Estado', 'Ingreso']]
        
        # Calcular el ancho máximo necesario para cada columna
        max_name_length = 0
        max_faculty_length = 0
        max_role_length = 0
        
        for hotbed in research_hotbeds:
            max_name_length = max(max_name_length, len(hotbed['name']))
            max_faculty_length = max(max_faculty_length, len(hotbed['faculty']))
            max_role_length = max(max_role_length, len(hotbed['type']))
        
        # Agregar datos sin truncar
        for hotbed in research_hotbeds:
            hotbeds_data.append([
                hotbed['name'],  # Texto completo
                hotbed['acronym'],
                hotbed['faculty'],  # Texto completo
                hotbed['type'],  # Texto completo
                hotbed['status'],
                hotbed['dateEnter'].strftime('%m/%Y') if hotbed['dateEnter'] else 'N/A'
            ])
        
        # Calcular anchos de columna dinámicamente
        available_width = 6.5 * inch  # Ancho total disponible
        
        # Anchos mínimos y fijos para algunas columnas
        acronym_width = 0.8 * inch
        status_width = 0.8 * inch
        date_width = 0.7 * inch
        
        # Ancho restante para las columnas variables
        remaining_width = available_width - acronym_width - status_width - date_width
        
        # Distribución proporcional basada en contenido
        total_chars = max_name_length + max_faculty_length + max_role_length
        
        if total_chars > 0:
            name_ratio = max_name_length / total_chars
            faculty_ratio = max_faculty_length / total_chars
            role_ratio = max_role_length / total_chars
            
            # Asegurar anchos mínimos
            name_width = max(1.5 * inch, remaining_width * name_ratio)
            faculty_width = max(1.2 * inch, remaining_width * faculty_ratio)
            role_width = max(0.8 * inch, remaining_width * role_ratio)
            
            # Ajustar si excede el ancho disponible
            total_calc = name_width + faculty_width + role_width
            if total_calc > remaining_width:
                scale_factor = remaining_width / total_calc
                name_width *= scale_factor
                faculty_width *= scale_factor
                role_width *= scale_factor
        else:
            # Valores por defecto si no hay datos
            name_width = 2.0 * inch
            faculty_width = 1.5 * inch
            role_width = 1.0 * inch
        
        col_widths = [name_width, acronym_width, faculty_width, role_width, status_width, date_width]
        
        hotbeds_table = Table(hotbeds_data, colWidths=col_widths)
        
        # Estilo especial para tabla responsive
        responsive_table_style = TableStyle([
            # Header - Rosa/Morado degradado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d946ef')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),  # Fuente más pequeña para header
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # Body
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fdf2f8')),
            ('FONTSIZE', (0, 1), (-1, -1), 7),  # Fuente más pequeña para contenido
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#f3e8ff')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            
            # Alineación específica para columnas pequeñas
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),  # Acrónimo centrado
            ('ALIGN', (4, 0), (4, -1), 'CENTER'),  # Estado centrado
            ('ALIGN', (5, 0), (5, -1), 'CENTER'),  # Fecha centrada
            
            # Permitir salto de línea en texto largo
            ('WORDWRAP', (0, 0), (-1, -1), True),
        ])
        
        hotbeds_table.setStyle(responsive_table_style)
        story.append(hotbeds_table)
    else:
        no_hotbeds = Paragraph("No está asociado a ningún semillero de investigación.", std_styles['normal'])
        story.append(no_hotbeds)
    
    story.append(Spacer(1, 20))
    
    # Resumen de actividades
    story.append(Paragraph(f"RESUMEN DE ACTIVIDADES - {format_semester_label_detailed(semester)}", std_styles['heading']))
    
    total_hours = sum(a['duration'] for a in activities)
    approved_activities = len([a for a in activities if a['approved_free_hours']])
    
    stats_data = [
        ['Total actividades', str(len(activities)), 'Horas totales', f'{total_hours}h'],
        ['Aprobadas', str(approved_activities), 'Pendientes', str(len(activities) - approved_activities)],
        ['Proyectos', str(len([a for a in activities if 'proyecto' in a['type'].lower()])), 'Productos', str(len([a for a in activities if 'producto' in a['type'].lower()]))],
        ['Reconocimientos', str(len([a for a in activities if 'reconocimiento' in a['type'].lower()])), 'Otras', str(len([a for a in activities if a['type'].lower() not in ['proyecto', 'producto', 'reconocimiento']]))]
    ]
    
    stats_table = Table(stats_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 1*inch])
    stats_table.setStyle(get_stats_table_style())
    story.append(stats_table)
    story.append(PageBreak())
    
    # Actividades detalladas - INCLUIR INDICADOR DE PARTICIPACIÓN
    story.append(Paragraph(f"ACTIVIDADES DETALLADAS - {format_semester_label_detailed(semester)}", std_styles['heading']))
    
    if activities:
        # Agrupar por tipo
        activity_types = list(set(a['type'] for a in activities))
        
        for activity_type in activity_types:
            type_activities = [a for a in activities if a['type'] == activity_type]
            
            story.append(Paragraph(f"{activity_type.upper()} ({len(type_activities)})", std_styles['subheading']))
            
            for i, activity in enumerate(type_activities, 1):
                # Verificar el rol del usuario en esta actividad
                user_role = get_user_role_in_activity(user.iduser, activity['id'])
                
                # Información básica - SIN CATEGORÍA + ROL DEL USUARIO
                basic_info = [
                    ['Título:', activity['title'][:42] + '...' if len(activity['title']) > 42 else activity['title']],
                    ['Fecha:', activity['date'].strftime('%d/%m/%Y')],
                    ['Semillero:', activity['research_hotbed_name'][:32] + '...' if len(activity['research_hotbed_name']) > 32 else activity['research_hotbed_name']],
                    ['Mi participación:', user_role],  # NUEVO CAMPO
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
                        ['Nombre proyecto:', project['name'][:35] + '...' if len(project['name']) > 35 else project['name']],
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
                        ['Descripción producto:', product['description'][:50] + '...' if len(product['description']) > 50 else product['description']]
                    ])
                
                elif 'recognition_data' in activity:
                    recognition = activity['recognition_data']
                    basic_info.append(['DATOS DEL RECONOCIMIENTO', ''])
                    basic_info.extend([
                        ['Proyecto reconocido:', recognition['project_name'][:35] + '...' if len(recognition['project_name']) > 35 else recognition['project_name']],
                        ['Organización otorgante:', recognition['organization_name'][:35] + '...' if len(recognition['organization_name']) > 35 else recognition['organization_name']]
                    ])
                
                # Autores (MANTENER SOLO ESTAS SECCIONES)
                if activity['authors']['main_authors']:
                    authors_text = ', '.join(activity['authors']['main_authors'])
                    if len(authors_text) > 45:
                        authors_text = authors_text[:45] + '...'
                    basic_info.append(['Autores principales:', authors_text])
                
                if activity['authors']['co_authors']:
                    co_authors_text = ', '.join(activity['authors']['co_authors'])
                    if len(co_authors_text) > 45:
                        co_authors_text = co_authors_text[:45] + '...'
                    basic_info.append(['Co-autores:', co_authors_text])
                
                # Crear tabla de información con colores de la app
                info_table = Table(basic_info, colWidths=[1.7*inch, 4.8*inch])
                
                # Estilo base
                table_style = get_info_table_style()
                
                # Agregar estilo especial para separadores con colores de la app
                for row_idx, row in enumerate(basic_info):
                    if row[0].startswith('DATOS DEL'):
                        table_style.add('BACKGROUND', (0, row_idx), (-1, row_idx), colors.HexColor('#e879f9'))  # Rosa medio
                        table_style.add('TEXTCOLOR', (0, row_idx), (-1, row_idx), colors.white)
                        table_style.add('FONTNAME', (0, row_idx), (-1, row_idx), 'Helvetica-Bold')
                        table_style.add('ALIGN', (0, row_idx), (-1, row_idx), 'CENTER')
                
                info_table.setStyle(table_style)
                story.append(info_table)
                
                # Descripción completa con colores de la app
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

def generate_consolidated_users_pdf(users, semester):
    """Genera un PDF consolidado con colores de la app"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        topMargin=0.8*inch, 
        bottomMargin=0.8*inch, 
        leftMargin=0.5*inch, 
        rightMargin=0.5*inch
    )
    
    # Importar estilos del controlador principal
    from controllers.export.pdf_export_controller import get_standard_styles, get_standard_table_style
    
    # Obtener estilos estandarizados
    std_styles = get_standard_styles()
    story = []
    
    # Título principal
    title = Paragraph("REPORTE CONSOLIDADO DE USUARIOS", std_styles['title'])
    story.append(title)
    story.append(Spacer(1, 10))
    
    # Información general con colores de la app
    general_info = Paragraph(
        f"<font color='#be185d'><b>{format_semester_label_detailed(semester)}</b></font> | <font color='#7c2d92'>{len(users)} usuarios</font><br/>"
        f"<font color='#374151'>SIGISI - Sistema de Gestión de Semilleros<br/>"
        f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}</font>",
        std_styles['normal']
    )
    general_info.alignment = TA_CENTER
    story.append(general_info)
    story.append(Spacer(1, 25))
    
    # Tabla consolidada de usuarios - ACTUALIZADA
    users_data = [['#', 'Nombre', 'ID SIGAA', 'Tipo', 'Actividades', 'Horas']]
    
    for i, user in enumerate(users, 1):
        activities = get_user_activities_by_semester(user.iduser, semester)  # Ahora incluye co-autorías
        total_hours = sum(a['duration'] for a in activities)
        
        # Truncar nombre si es muy largo
        name = user.name_user[:22] + '...' if len(user.name_user) > 22 else user.name_user
        type_user = user.type_user[:10] + '...' if len(user.type_user) > 10 else user.type_user
        
        users_data.append([
            str(i),
            name,
            user.idSigaa_user or 'N/A',
            type_user,
            str(len(activities)),
            f'{total_hours}h'
        ])
    
    users_table = Table(users_data, colWidths=[0.4*inch, 2.8*inch, 1.2*inch, 1.2*inch, 0.8*inch, 0.8*inch])
    users_table.setStyle(get_standard_table_style())
    story.append(users_table)
    
    # Generar PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def get_user_role_in_activity(user_id, activity_id):
    """Determina el rol del usuario en una actividad específica"""
    try:
        # Verificar si es autor principal
        main_author = db.session.query(ActivityAuthors).join(
            UsersResearchHotbed, ActivityAuthors.user_research_hotbed_id == UsersResearchHotbed.idusersResearchHotbed
        ).filter(
            UsersResearchHotbed.user_iduser == user_id,
            ActivityAuthors.activity_id == activity_id,
            ActivityAuthors.is_main_author == True
        ).first()
        
        if main_author:
            return "Autor principal"
        
        # Verificar si es co-autor
        co_author = db.session.query(ActivityAuthors).join(
            UsersResearchHotbed, ActivityAuthors.user_research_hotbed_id == UsersResearchHotbed.idusersResearchHotbed
        ).filter(
            UsersResearchHotbed.user_iduser == user_id,
            ActivityAuthors.activity_id == activity_id,
            ActivityAuthors.is_main_author == False
        ).first()
        
        if co_author:
            return "Co-autor"
        
        # Si no es autor, verificar si es el usuario asociado al semillero de la actividad
        activity = db.session.query(ActivitiesResearchHotbed).filter_by(
            idactivitiesResearchHotbed=activity_id
        ).first()
        
        if activity:
            user_research = db.session.query(UsersResearchHotbed).filter_by(
                idusersResearchHotbed=activity.usersResearchHotbed_idusersResearchHotbed,
                user_iduser=user_id
            ).first()
            
            if user_research:
                return "Miembro del semillero"
        
        return "Participante"
        
    except Exception as e:
        logger.error(f"Error determinando rol del usuario en actividad: {str(e)}")
        return "Participante"