from db.connection import db

class ProjectsResearchHotbed(db.Model):
    __tablename__ = 'projectsResearchHotbed'

    idprojectsResearchHotbed = db.Column(db.Integer, primary_key=True)
    name_projectsResearchHotbed = db.Column(db.String(125), nullable=False)
    referenceNumber_projectsResearchHotbed = db.Column(db.String(125), nullable=False)
    startDate_projectsResearchHotbed = db.Column(db.Date, nullable=False)
    endDate_projectsResearchHotbed = db.Column(db.Date, nullable=True)
    principalResearcher_projectsResearchHotbed = db.Column(db.String(125), nullable=False)
    coResearchers_projectsResearchHotbed = db.Column(db.String(125), nullable=True)
