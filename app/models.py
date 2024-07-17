from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    username = db.Column(db.String(64), unique=True, nullable=False)  # Unique username
    password_hash = db.Column(db.String(256), nullable=False)  # Password hash

    # Method to set the user's password, storing the hash
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Method to check the user's password against the stored hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Define the BlogPost model
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    title = db.Column(db.String(128), nullable=False)  # Title of the blog post
    body = db.Column(db.Text, nullable=False)  # Body of the blog post
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)  # Timestamp of when the post was created
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)  # Foreign key referencing the user

    # Establish a relationship between BlogPost and User models
    user = db.relationship('User', backref=db.backref('posts', lazy='dynamic'))
