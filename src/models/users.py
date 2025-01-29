from db.connection import db

class User(db.Model):
    __tablename__ = 'user'
    iduser = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email_user = db.Column(db.String(125), unique=True, nullable=False)
    password_user = db.Column(db.String(255), nullable=False)
    idSigaa_user = db.Column(db.String(125), unique=True, nullable=False)
    name_user = db.Column(db.String(50), nullable=False)
    status_user = db.Column(db.String(45), nullable=False)
    type_user = db.Column(db.String(45), nullable=False)
    academicProgram_user = db.Column(db.String(125), nullable=False)
    termsAccepted_user = db.Column(db.Boolean, nullable=False)
    termsAcceptedAt_user = db.Column(db.DateTime, nullable=False)
    termsVersion_user = db.Column(db.String(45), nullable=False)
    lastDayLogin_user = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<User {self.name_user}>'
