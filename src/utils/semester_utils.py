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
    """
    try:
        parts = semester.split('-')
        if len(parts) != 3:
            return False
        
        _, sem_num, year = parts
        
        # Validar formato
        if not (sem_num in ['1', '2'] and year.isdigit()):
            return False
        
        # Validar rango de años (desde 2024 hasta año actual + 5)
        year_int = int(year)
        current_year = datetime.now().year
        
        return 2024 <= year_int <= current_year + 5
        
    except:
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