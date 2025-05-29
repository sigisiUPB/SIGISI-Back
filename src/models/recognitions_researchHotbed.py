from db.connection import db

class RecognitionsResearchHotbed(db.Model):
    __tablename__ = 'recognitionsResearchHotbed'
    
    idrecognitionsResearchHotbed = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Corregir nombres de columnas según la base de datos
    projectName_recognitionsResearchHotbed = db.Column(db.String(125), nullable=False)
    organizationName_recognitionsResearchHotbed = db.Column(db.String(125), nullable=False)
    
    def __repr__(self):
        return f'<RecognitionsResearchHotbed {self.idrecognitionsResearchHotbed}>'
