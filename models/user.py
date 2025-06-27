from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    """
    Represents a user in the database.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Increased length for future-proofing with different hashing algorithms
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    role = db.Column(db.String(20), nullable=False, default='user') # Roles: user, farmer, admin

    # One-to-one relationship with Farmer
    # uselist=False indicates a one-to-one relationship
    farmer = db.relationship('Farmer', backref='user', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        """
        Provides a developer-friendly representation of the User object.
        """
        return f'<User {self.username}>'

    def set_password(self, password):
        """Hashes and sets the user's password."""
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        """Returns True if the user is an admin."""
        return self.role == 'admin'

    @property
    def is_farmer(self):
        """Returns True if the user is a farmer."""
        return self.role == 'farmer'