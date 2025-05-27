from db.connection import db

class ActivityAuthors(db.Model):
    __tablename__ = 'activity_authors'

    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activitiesResearchHotbed.idactivitiesResearchHotbed'), nullable=False)
    user_research_hotbed_id = db.Column(db.Integer, db.ForeignKey('usersResearchHotbed.idusersResearchHotbed'), nullable=False)
    is_main_author = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<ActivityAuthor {self.id}: Activity {self.activity_id}, User {self.user_research_hotbed_id}>'