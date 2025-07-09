from extensions import db
from datetime import datetime, timezone
from .base_model import BaseModel

class Farmer(BaseModel):
    """
    Represents a farmer's profile in the database, linked to a User.
    """
    __tablename__ = 'farmers'

    # One-to-one relationship with User: each user can have one farmer profile.
    # unique=True ensures this one-to-one constraint.
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)

    name = db.Column(db.String(150), nullable=False)
    farm_name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.Text)
    phone = db.Column(db.String(20))
    bio = db.Column(db.Text)
    profile_image_url = db.Column(db.Text)

    # Relationship to User model (one-to-one)
    user = db.relationship('User', back_populates='farmer_profile', uselist=False)

    # Relationships to Products and Inquiries (one-to-many)
    products = db.relationship('Product', back_populates='farmer', lazy=True, cascade='all, delete-orphan')

    inquiries = db.relationship('Inquiry', back_populates='farmer', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        """
        Provides a developer-friendly representation of the Farmer object.
        """
        return f'<Farmer {self.farm_name} (User ID: {self.user_id})>'

    def to_dict(self, include_products=False):
        """
        Serializes the Farmer object to a dictionary.
        This single method combines all fields and optionally includes products.
        """
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'farm_name': self.farm_name,
            'location': self.location,
            'phone': self.phone,
            'bio': self.bio,
            'profile_image_url': self.profile_image_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_products:
            data['products'] = [product.to_dict() for product in self.products]
        return data