from extensions import db
from flask_login import UserMixin

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    completed = db.Column(db.Boolean, default=False)

    # Define the relationship here in Task
    user = db.relationship("User", backref="tasks", lazy=True)

    def __repr__(self):
        return f"<Task {self.title}>"

class User(db.Model, UserMixin):  # UserMixin provides default implementations for these methods
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"
