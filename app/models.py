from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Relationship to Location (Defines the relationship between the User and the location tables.)
    locations = db.relationship('Location', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(30), nullable=False)
    #Foriegn Key allows this table to access the other table.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationship back to User (Just defines the user).
    user = db.relationship('User', back_populates='locations')

    def __repr__(self):
        return f'<Location {self.location_name}>'
