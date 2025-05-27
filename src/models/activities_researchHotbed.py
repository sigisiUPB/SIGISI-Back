from db.connection import db

class ActivitiesResearchHotbed(db.Model):
    __tablename__ = 'activitiesResearchHotbed'

    idactivitiesResearchHotbed = db.Column(db.Integer, primary_key=True)
    title_activitiesResearchHotbed = db.Column(db.String(125), nullable=False)
    responsible_activitiesResearchHotbed = db.Column(db.String(125), nullable=False)
    date_activitiesResearchHotbed = db.Column(db.Date, nullable=False)
    description_activitiesResearchHotbed = db.Column(db.Text, nullable=False)  # Cambiado a TEXT
    type_activitiesResearchHotbed = db.Column(db.String(45), nullable=False)
    startTime_activitiesResearchHotbed = db.Column(db.Time, nullable=True)
    endTime_activitiesResearchHotbed = db.Column(db.Time, nullable=True)
    duration_activitiesResearchHotbed = db.Column(db.Float, nullable=True)
    approvedFreeHours_activitiesResearchHotbed = db.Column(db.Boolean, nullable=True)
    semester = db.Column(db.String(20), nullable=False, default='semestre-1-2025')  # Nuevo campo

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
