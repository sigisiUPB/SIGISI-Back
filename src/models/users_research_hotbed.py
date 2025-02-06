from db.connection import db
from datetime import datetime

class UsersResearchHotbed(db.Model):
    __tablename__ = "usersResearchHotbed"

    idusersResearchHotbed = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status_usersResearchHotbed = db.Column(db.String(45), nullable=False)
    TypeUser_usersResearchHotbed = db.Column(db.String(45), nullable=False)
    observation_usersResearchHotbed = db.Column(db.String(500), nullable=True)
    dateEnter_usersResearchHotbed = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    dateExit_usersResearchHotbed = db.Column(db.Date, nullable=True)
    
    # Relaciones con User y ResearchHotbed
    researchHotbed_idresearchHotbed = db.Column(db.Integer, db.ForeignKey("researchHotbed.idresearchHotbed"), nullable=False)
    user_iduser = db.Column(db.Integer, db.ForeignKey("user.iduser"), nullable=False)

    researchHotbed = db.relationship("ResearchHotbed", backref="users_research_hotbed")
    user = db.relationship("User", backref="research_hotbeds")

    def __repr__(self):
        return f"<UsersResearchHotbed {self.idusersResearchHotbed} - User {self.user_iduser} - ResearchHotbed {self.researchHotbed_idresearchHotbed}>"
