from datetime import datetime

def get_current_semester():
    """
    Obtiene el semestre actual basado en la fecha.
    Semestre 1: Enero - Junio
    Semestre 2: Julio - Diciembre
    """
    now = datetime.now()
    year = now.year
    month = now.month
    
    semester = 1 if month <= 6 else 2
    return f"semestre-{semester}-{year}"

def get_available_semesters(start_year=2024, future_years=2):
    """
    Genera una lista de semestres disponibles desde start_year
    hasta future_years años en el futuro.
    """
    current_year = datetime.now().year
    end_year = current_year + future_years
    
    semesters = []
    
    for year in range(start_year, end_year + 1):
        semesters.extend([
            f"semestre-1-{year}",
            f"semestre-2-{year}"
        ])
    
    return semesters

def is_valid_semester(semester):
    """
    Valida si un semestre tiene el formato correcto y está en el rango válido.
    Acepta semestres desde el inicio del sistema (2024) hasta años futuros razonables.
    """
    try:
        parts = semester.split('-')
        if len(parts) != 3:
            return False
        
        prefix, sem_num, year = parts
        
        # Validar formato exacto
        if prefix != "semestre":
            return False
            
        if not (sem_num in ['1', '2'] and year.isdigit()):
            return False
        
        # Validar rango de años - más escalable
        year_int = int(year)
        current_year = datetime.now().year
        
        # Desde el año de inicio del sistema hasta +20 años en el futuro
        # Esto permite planificación a muy largo plazo
        min_year = 2024  # Año de inicio del sistema
        max_year = current_year + 20  # Suficiente para planificación universitaria
        
        return min_year <= year_int <= max_year
        
    except (ValueError, IndexError):
        return False

def format_semester_label(semester):
    """
    Convierte el formato de semestre a una etiqueta legible.
    """
    try:
        parts = semester.split('-')
        if len(parts) == 3:
            _, sem_num, year = parts
            return f"Semestre {sem_num} - {year}"
    except:
        pass
    
    return semester

def format_semester_label_detailed(semester):
    """
    Convierte formato 'semestre-1-2025' a 'Primer Semestre 2025'
    Para uso en el PDF con formato más descriptivo
    """
    try:
        parts = semester.split('-')
        if len(parts) != 3:
            return semester
            
        semester_num = int(parts[1])
        year = parts[2]
        
        semester_name = "Primer" if semester_num == 1 else "Segundo"
        return f"{semester_name} Semestre {year}"
    except:
        return semester

def is_semester_in_past(semester):
    """
    Función adicional para verificar si un semestre ya pasó.
    Útil para validaciones específicas de negocio.
    """
    try:
        current_semester = get_current_semester()
        current_parts = current_semester.split('-')
        semester_parts = semester.split('-')
        
        if len(current_parts) != 3 or len(semester_parts) != 3:
            return False
            
        current_year = int(current_parts[2])
        current_sem = int(current_parts[1])
        
        check_year = int(semester_parts[2])
        check_sem = int(semester_parts[1])
        
        if check_year < current_year:
            return True
        elif check_year == current_year and check_sem < current_sem:
            return True
        else:
            return False
            
    except (ValueError, IndexError):
        return False

def is_semester_current_or_future(semester):
    """
    Función adicional para verificar si un semestre es actual o futuro.
    Útil para validar que se puedan crear actividades solo en semestres actuales/futuros.
    """
    return is_valid_semester(semester) and not is_semester_in_past(semester)