import pytest
from datetime import datetime, date
from models.activities_researchHotbed import ActivitiesResearchHotbed
from models.projects_researchHotbed import ProjectsResearchHotbed
from models.products_researchHotbed import ProductsResearchHotbed
from models.recognitions_researchHotbed import RecognitionsResearchHotbed
from models.activity_authors import ActivityAuthors
from models.users import User
from models.users_research_hotbed import UsersResearchHotbed
from models.research_hotbed import ResearchHotbed
from controllers.activitiesResearchHotbed.register_activities_controller import register_activity
from db.connection import db

@pytest.fixture
def setup_activity_test_data():
    """Fixture para configurar datos de prueba para actividades"""
    
    # Crear usuario de prueba con todos los campos requeridos
    test_user = User(
        name_user="Juan Pérez",
        email_user="juan.perez@test.com",
        password_user="hashed_password",
        idSigaa_user="12345",
        type_user="Estudiante",
        status_user="Activo",
        academicProgram_user="Ingeniería de Sistemas",
        termsAccepted_user=True,
        termsAcceptedAt_user=datetime.now(),
        termsVersion_user="1.0"
    )
    db.session.add(test_user)
    db.session.flush()
    
    # Crear semillero de prueba con todos los campos requeridos
    test_research_hotbed = ResearchHotbed(
        name_researchHotbed="Semillero de Prueba",
        acronym_researchHotbed="SP",
        faculty_researchHotbed="Ingeniería",
        universityBranch_researchHotbed="Principal",
        status_researchHotbed="Activo",
        dateCreation_researchHotbed=datetime.now()
    )
    db.session.add(test_research_hotbed)
    db.session.flush()
    
    # Crear relación usuario-semillero con todos los campos requeridos
    test_user_research = UsersResearchHotbed(
        user_iduser=test_user.iduser,
        researchHotbed_idresearchHotbed=test_research_hotbed.idresearchHotbed,
        TypeUser_usersResearchHotbed="Estudiante",
        status_usersResearchHotbed="Activo",
        dateEnter_usersResearchHotbed=date.today()
    )
    db.session.add(test_user_research)
    db.session.flush()
    
    db.session.commit()
    
    return {
        'user': test_user,
        'research_hotbed': test_research_hotbed,
        'user_research': test_user_research
    }

def test_create_basic_activity_success(client, setup_database, setup_activity_test_data):
    """Prueba la creación exitosa de una actividad básica"""
    
    test_data = setup_activity_test_data
    
    activity_data = {
        'title': 'Actividad de Prueba',
        'date': '2025-06-15',
        'description': 'Descripción de la actividad de prueba',
        'type': 'actividad',
        'start_time': '09:00',
        'end_time': '11:00',
        'duration': 2,
        'approved_free_hours': True,
        'semester': 'semestre-1-2025',
        'userResearchHotbedId': test_data['user_research'].idusersResearchHotbed,
        'authors_ids': [test_data['user_research'].idusersResearchHotbed],
        'co_authors_ids': [],
        'responsible': 'Juan Pérez'
    }
    
    # Ejecutar el controlador
    response, status_code = register_activity(activity_data)
    
    # Verificar respuesta exitosa
    assert status_code == 201
    assert 'message' in response.json
    assert response.json['message'] == 'Actividad registrada exitosamente'
    assert 'activity_id' in response.json
    
    # Verificar que se creó en la base de datos
    activity = ActivitiesResearchHotbed.query.filter_by(
        title_activitiesResearchHotbed='Actividad de Prueba'
    ).first()
    
    assert activity is not None
    assert activity.description_activitiesResearchHotbed == 'Descripción de la actividad de prueba'
    assert activity.type_activitiesResearchHotbed == 'actividad'
    assert activity.duration_activitiesResearchHotbed == 2
    assert activity.semester == 'semestre-1-2025'
    
    # Verificar relación de autoría
    author_relation = ActivityAuthors.query.filter_by(
        activity_id=activity.idactivitiesResearchHotbed
    ).first()
    
    assert author_relation is not None
    assert author_relation.is_main_author == True

def test_create_project_activity_success(client, setup_database, setup_activity_test_data):
    """Prueba la creación exitosa de una actividad tipo proyecto"""
    
    test_data = setup_activity_test_data
    
    activity_data = {
        'title': 'Proyecto de Investigación',
        'date': '2025-06-15',
        'description': 'Descripción del proyecto de investigación',
        'type': 'proyecto',
        'start_time': '08:00',
        'end_time': '12:00',
        'duration': 4,
        'approved_free_hours': False,
        'semester': 'semestre-1-2025',
        'userResearchHotbedId': test_data['user_research'].idusersResearchHotbed,
        'authors_ids': [test_data['user_research'].idusersResearchHotbed],
        'co_authors_ids': [],
        'responsible': 'Juan Pérez',
        'project': {
            'name': 'Sistema de Gestión Académica',
            'reference_number': 'PROJ-2025-001',
            'start_date': '2025-01-15',
            'end_date': '2025-12-15'
        }
    }
    
    # Ejecutar el controlador
    response, status_code = register_activity(activity_data)
    
    # Verificar respuesta exitosa
    assert status_code == 201
    assert 'activity_id' in response.json
    
    # Verificar actividad creada
    activity = ActivitiesResearchHotbed.query.filter_by(
        title_activitiesResearchHotbed='Proyecto de Investigación'
    ).first()
    
    assert activity is not None
    assert activity.type_activitiesResearchHotbed == 'proyecto'
    assert activity.projectsResearchHotbed_idprojectsResearchHotbed is not None
    
    # Verificar proyecto asociado - ARREGLAR deprecated .get()
    project = db.session.get(ProjectsResearchHotbed, activity.projectsResearchHotbed_idprojectsResearchHotbed)
    assert project is not None
    assert project.name_projectsResearchHotbed == 'Sistema de Gestión Académica'
    assert project.referenceNumber_projectsResearchHotbed == 'PROJ-2025-001'

def test_create_product_activity_success(client, setup_database, setup_activity_test_data):
    """Prueba la creación exitosa de una actividad tipo producto"""
    
    test_data = setup_activity_test_data
    
    activity_data = {
        'title': 'Artículo Científico',
        'date': '2025-06-15',
        'description': 'Publicación de artículo en revista indexada',
        'type': 'producto',
        'start_time': '14:00',
        'end_time': '18:00',
        'duration': 4,
        'approved_free_hours': True,
        'semester': 'semestre-1-2025',
        'userResearchHotbedId': test_data['user_research'].idusersResearchHotbed,
        'authors_ids': [test_data['user_research'].idusersResearchHotbed],
        'co_authors_ids': [],
        'responsible': 'Juan Pérez',
        'product': {
            'category': 'Artículo Científico',
            'type': 'Revista Indexada',
            'description': 'Artículo sobre sistemas de información',
            'date_publication': '2025-05-01'
        }
    }
    
    # Ejecutar el controlador
    response, status_code = register_activity(activity_data)
    
    # Verificar respuesta exitosa
    assert status_code == 201
    
    # Verificar actividad creada
    activity = ActivitiesResearchHotbed.query.filter_by(
        title_activitiesResearchHotbed='Artículo Científico'
    ).first()
    
    assert activity is not None
    assert activity.type_activitiesResearchHotbed == 'producto'
    assert activity.productsResearchHotbed_idproductsResearchHotbed is not None
    
    # Verificar producto asociado - ARREGLAR deprecated .get()
    product = db.session.get(ProductsResearchHotbed, activity.productsResearchHotbed_idproductsResearchHotbed)
    assert product is not None
    assert product.category_productsResearchHotbed == 'Artículo Científico'
    assert product.type_productsResearchHotbed == 'Revista Indexada'

def test_create_recognition_activity_success(client, setup_database, setup_activity_test_data):
    """Prueba la creación exitosa de una actividad tipo reconocimiento"""
    
    test_data = setup_activity_test_data
    
    activity_data = {
        'title': 'Premio de Investigación',
        'date': '2025-06-15',
        'description': 'Reconocimiento por mejor proyecto estudiantil',
        'type': 'reconocimiento',
        'start_time': '10:00',
        'end_time': '12:00',
        'duration': 2,
        'approved_free_hours': True,
        'semester': 'semestre-1-2025',
        'userResearchHotbedId': test_data['user_research'].idusersResearchHotbed,
        'authors_ids': [test_data['user_research'].idusersResearchHotbed],
        'co_authors_ids': [],
        'responsible': 'Juan Pérez',
        'recognition': {
            'name': 'Mejor Proyecto Estudiantil 2025',
            'project_name': 'Sistema de Gestión Académica',
            'organization_name': 'Universidad Nacional'
        }
    }
    
    # Ejecutar el controlador
    response, status_code = register_activity(activity_data)
    
    # Verificar respuesta exitosa
    assert status_code == 201
    
    # Verificar actividad creada
    activity = ActivitiesResearchHotbed.query.filter_by(
        title_activitiesResearchHotbed='Premio de Investigación'
    ).first()
    
    assert activity is not None
    assert activity.type_activitiesResearchHotbed == 'reconocimiento'
    assert activity.recognitionsResearchHotbed_idrecognitionsResearchHotbed is not None
    
    # Verificar reconocimiento asociado - ARREGLAR deprecated .get()
    recognition = db.session.get(RecognitionsResearchHotbed, activity.recognitionsResearchHotbed_idrecognitionsResearchHotbed)
    assert recognition is not None
    assert recognition.name_recognitionsResearchHotbed == 'Mejor Proyecto Estudiantil 2025'
    assert recognition.projectName_recognitionsResearchHotbed == 'Sistema de Gestión Académica'
    assert recognition.organizationName_recognitionsResearchHotbed == 'Universidad Nacional'
    # Verificar auto-completado de participantes
    assert 'Juan Pérez' in recognition.participantsNames_recognitionsResearchHotbed

def test_create_activity_missing_required_fields(client, setup_database):
    """Prueba el manejo de errores cuando faltan campos obligatorios"""
    
    # Datos incompletos (falta título)
    activity_data = {
        'date': '2025-06-15',
        'description': 'Descripción sin título',
        'userResearchHotbedId': 1,  # ID genérico
        'authors_ids': [1]
    }
    
    # Ejecutar el controlador
    response, status_code = register_activity(activity_data)
    
    # Verificar error
    assert status_code == 400
    assert 'error' in response.json
    assert 'campos obligatorios' in response.json['error']

def test_create_activity_with_invalid_user(client, setup_database):
    """Prueba el manejo de errores con usuario inexistente"""
    
    activity_data = {
        'title': 'Actividad con usuario inexistente',
        'date': '2025-06-15',
        'description': 'Descripción de prueba',
        'userResearchHotbedId': 99999,  # ID inexistente
        'authors_ids': [99999]  # ID inexistente
    }
    
    # Ejecutar el controlador
    response, status_code = register_activity(activity_data)
    
    # Verificar error
    assert status_code == 400
    assert 'error' in response.json
    assert 'no existe en el semillero' in response.json['error']

def test_create_activity_with_invalid_date_format(client, setup_database, setup_activity_test_data):
    """Prueba el manejo de errores con formato de fecha inválido"""
    
    test_data = setup_activity_test_data
    
    activity_data = {
        'title': 'Actividad con fecha inválida',
        'date': 'fecha-invalida',  # Formato incorrecto
        'description': 'Descripción de prueba',
        'type': 'actividad',
        'userResearchHotbedId': test_data['user_research'].idusersResearchHotbed,  # Usar ID válido
        'authors_ids': [test_data['user_research'].idusersResearchHotbed],  # Usar ID válido
        'co_authors_ids': [],
        'responsible': 'Juan Pérez'
    }
    
    # Ejecutar el controlador
    response, status_code = register_activity(activity_data)
    
    # Verificar error (puede ser error de formato de fecha o error de validación)
    assert status_code == 400
    assert 'error' in response.json
    # El error puede ser sobre formato de fecha o sobre validación de datos
    error_message = response.json['error'].lower()
    assert any(keyword in error_message for keyword in ['fecha', 'format', 'invalid', 'inválid', 'valor']), f"Error message: {response.json['error']}"

def test_create_activity_multiple_authors_and_coauthors(client, setup_database, setup_activity_test_data):
    """Prueba la creación de actividad con múltiples autores y co-autores"""
    
    test_data = setup_activity_test_data
    
    # Crear segundo usuario con todos los campos requeridos
    second_user = User(
        name_user="María González",
        email_user="maria.gonzalez@test.com",
        password_user="hashed_password",
        idSigaa_user="67890",
        type_user="Profesor",
        status_user="Activo",
        academicProgram_user="Ingeniería de Sistemas",
        termsAccepted_user=True,
        termsAcceptedAt_user=datetime.now(),
        termsVersion_user="1.0"
    )
    db.session.add(second_user)
    db.session.flush()
    
    second_user_research = UsersResearchHotbed(
        user_iduser=second_user.iduser,
        researchHotbed_idresearchHotbed=test_data['research_hotbed'].idresearchHotbed,
        TypeUser_usersResearchHotbed="Profesor",
        status_usersResearchHotbed="Activo",
        dateEnter_usersResearchHotbed=date.today()
    )
    db.session.add(second_user_research)
    db.session.flush()
    db.session.commit()
    
    activity_data = {
        'title': 'Actividad Colaborativa',
        'date': '2025-06-15',
        'description': 'Actividad con múltiples participantes',
        'type': 'actividad',
        'duration': 3,
        'userResearchHotbedId': test_data['user_research'].idusersResearchHotbed,
        'authors_ids': [test_data['user_research'].idusersResearchHotbed],
        'co_authors_ids': [second_user_research.idusersResearchHotbed],
        'responsible': 'Juan Pérez'
    }
    
    # Ejecutar el controlador
    response, status_code = register_activity(activity_data)
    
    # Verificar respuesta exitosa
    assert status_code == 201
    
    # Verificar relaciones de autoría
    activity_id = response.json['activity_id']
    
    main_authors = ActivityAuthors.query.filter_by(
        activity_id=activity_id,
        is_main_author=True
    ).all()
    
    co_authors = ActivityAuthors.query.filter_by(
        activity_id=activity_id,
        is_main_author=False
    ).all()
    
    assert len(main_authors) == 1
    assert len(co_authors) == 1