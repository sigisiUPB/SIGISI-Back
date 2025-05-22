from db.connection import db

class RecognitionsResearchHotbed(db.Model):
    __tablename__ = "recognitionsResearchHotbed"

    idrecognitionsResearchHotbed = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name_recognitionsResearchHotbed = db.Column(db.String(200), nullable=False)
    projectName_recognitionsResearchHotbed = db.Column(db.String(200), nullable=True)
    participantsNames_recognitionsResearchHotbed = db.Column(db.Text, nullable=True)
    organizationName_recognitionsResearchHotbed = db.Column(db.String(200), nullable=False)
