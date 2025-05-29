from db.connection import db

class ActivitiesResearchHotbed(db.Model):
    __tablename__ = 'activitiesResearchHotbed'

    idactivitiesResearchHotbed = db.Column(db.Integer, primary_key=True)
    title_activitiesResearchHotbed = db.Column(db.String(125), nullable=False)
    responsible_activitiesResearchHotbed = db.Column(db.String(125), nullable=True)
    date_activitiesResearchHotbed = db.Column(db.Date, nullable=False)
    description_activitiesResearchHotbed = db.Column(db.Text, nullable=False)
    type_activitiesResearchHotbed = db.Column(db.String(45), nullable=False)
    category = db.Column(db.String(50), nullable=False, default='general')
    reference_number = db.Column(db.String(125), nullable=True)
    publication_date = db.Column(db.Date, nullable=True)
    organization_name = db.Column(db.String(125), nullable=True)
    startTime_activitiesResearchHotbed = db.Column(db.Time, nullable=True)
    endTime_activitiesResearchHotbed = db.Column(db.Time, nullable=True)
    duration_activitiesResearchHotbed = db.Column(db.Float, nullable=True)
    approvedFreeHours_activitiesResearchHotbed = db.Column(db.Float, nullable=True)
    semester = db.Column(db.String(20), nullable=False, default='semestre-1-2025')

    usersResearchHotbed_idusersResearchHotbed = db.Column(
        db.Integer, 
        db.ForeignKey('usersResearchHotbed.idusersResearchHotbed'),
        nullable=False
    )

    projectsResearchHotbed_idprojectsResearchHotbed = db.Column(
        db.Integer, 
        db.ForeignKey('projectsResearchHotbed.idprojectsResearchHotbed'),
        nullable=True
    )

    productsResearchHotbed_idproductsResearchHotbed = db.Column(
        db.Integer, 
        db.ForeignKey('productsResearchHotbed.idproductsResearchHotbed'),
        nullable=True
    )

    recognitionsResearchHotbed_idrecognitionsResearchHotbed = db.Column(
        db.Integer, 
        db.ForeignKey('recognitionsResearchHotbed.idrecognitionsResearchHotbed'),
        nullable=True
    )

    def __repr__(self):
        return f'<ActivitiesResearchHotbed {self.idactivitiesResearchHotbed}>'
