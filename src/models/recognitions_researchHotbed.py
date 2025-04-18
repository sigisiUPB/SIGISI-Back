from db.connection import db

class RecognitionsResearchHotbed(db.Model):
    __tablename__ = 'recognitionsResearchHotbed'

    idrecognitionsResearchHotbed = db.Column(db.Integer, primary_key=True)
    name_recognitionsResearchHotbed = db.Column(db.String(125), nullable=False)
    projectName_recognitionsResearchHotbed = db.Column(db.String(125), nullable=False)
    participantsNames_recognitionsResearchHotbed = db.Column(db.String(250), nullable=False)
    organizationName_recognitionsResearchHotbed = db.Column(db.String(125), nullable=False)
