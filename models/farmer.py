from extensions import db
from datetime import datetime

class Farmer(db.Model):
    """
    Represents a farmer's profile in the database, linked to a User.
    """
    __tablename__ = 'farmers'

    id = db.Column(db.Integer, primary_key=True)
    # One-to-one relationship with User: each user can have one farmer profile.
    # unique=True ensures this one-to-one constraint.
    # ondelete='CASCADE' means if the associated user is deleted, this farmer profile is also deleted.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)

    farm_name = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    location = db.Column(db.Text)
    phone = db.Column(db.String(20))
    description = db.Column(db.Text)
    profile_image_url = db.Column(db.Text)

    # Timestamps for creation and last update
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # onupdate=datetime.utcnow ensures this field is updated every time the record is modified
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships to Products and Inquiries (one-to-many)
    products = db.relationship('Product', backref='farmer', lazy=True, cascade='all, delete-orphan')
    inquiries = db.relationship('Inquiry', backref='farmer', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        """
        Provides a developer-friendly representation of the Farmer object.
        """
        return f'<Farmer {self.farm_name} (User ID: {self.user_id})>'