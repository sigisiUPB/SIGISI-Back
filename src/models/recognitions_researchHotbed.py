from db.connection import db

class RecognitionsResearchHotbed(db.Model):
    __tablename__ = 'recognitionsResearchHotbed'
    
    idrecognitionsResearchHotbed = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name_recognitionsResearchHotbed = db.Column(db.String(125), nullable=True)  # AGREGAR
    projectName_recognitionsResearchHotbed = db.Column(db.String(125), nullable=False)
    participantsNames_recognitionsResearchHotbed = db.Column(db.String(250), nullable=True)  # AGREGAR
    organizationName_recognitionsResearchHotbed = db.Column(db.String(125), nullable=False)
    
    def __repr__(self):
        return f'<RecognitionsResearchHotbed {self.idrecognitionsResearchHotbed}>'
