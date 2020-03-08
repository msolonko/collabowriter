from project import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    #general / login
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(20), nullable=False)
    lname = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    #relationships
    freewrites = db.relationship('Freewrite', backref='user', lazy=True)
    feedbacks = db.relationship('Feedback', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.fname}', '{self.lname}', '{self.email}')"


class Freewrite(db.Model):
    __tablename__ = 'freewrite'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    question = db.Column(db.Text, nullable=False)
    complete = db.Column(db.Boolean, nullable=False, default=False)
    
    received_feedback = db.Column(db.Boolean, nullable=False, default=False)
    searching_feedback = db.Column(db.Boolean, nullable=False, default=True)
    
    prompt_id = db.Column(db.Integer, db.ForeignKey('prompt.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    feedback = db.relationship('Feedback', backref='freewrite', lazy=True)

    def __repr__(self):
        return f"Freewrite('{self.id}')"
    
    
class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    general = db.Column(db.Text, nullable=False)
    specific = db.Column(db.Text, nullable=False)
    complete = db.Column(db.Boolean, nullable=False, default=False)
        
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # person who writes the FEEDBACK
    freewrite_id = db.Column(db.Integer, db.ForeignKey('freewrite.id'), nullable=False) # id of the freewrite of the person receiving feedback

    def __repr__(self):
        return f"Feedback('{self.id}')"
    
class Prompt(db.Model):
    __tablename__ = 'prompt'
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Text, nullable=False)
        
    def __repr__(self):
        return f"Prompt('{self.id}')"
