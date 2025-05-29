from db.connection import db

class ProjectsResearchHotbed(db.Model):
    __tablename__ = 'projectsResearchHotbed'
    
    idprojectsResearchHotbed = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Corregir nombres de columnas según la base de datos
    referenceNumber_projectsResearchHotbed = db.Column(db.String(125), nullable=False)
    startDate_projectsResearchHotbed = db.Column(db.Date, nullable=False)
    endDate_projectsResearchHotbed = db.Column(db.Date, nullable=True)
    principalResearcher_projectsResearchHotbed = db.Column(db.String(125), nullable=False)
    # Nota: coResearchers no existe en la tabla actual
    
    def __repr__(self):
        return f'<ProjectsResearchHotbed {self.idprojectsResearchHotbed}>'
