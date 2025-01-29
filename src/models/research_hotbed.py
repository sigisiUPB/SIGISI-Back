from db.connection import db

class ResearchHotbed(db.Model):
    __tablename__ = 'researchHotbed'

    idresearchHotbed = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name_researchHotbed = db.Column(db.String(125), nullable=False)
    universityBranch_researchHotbed = db.Column(db.String(125), nullable=False)
    acronym_researchHotbed = db.Column(db.String(45), nullable=False)
    faculty_researchHotbed = db.Column(db.String(125), nullable=False)
    status_researchHotbed = db.Column(db.String(45), nullable=False)
    dateCreation_researchHotbed = db.Column(db.String(45), nullable=False)
    deleteDescription_researchHotbed = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        return f"<ResearchHotbed {self.name_researchHotbed}>"