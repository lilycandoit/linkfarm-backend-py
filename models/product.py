from extensions import db
from datetime import datetime

class Product(db.Model):
    """
    Represents a product offered by a farmer.
    """
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id', ondelete='CASCADE'), nullable=False)

    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False) # DECIMAL(10,2)
    unit = db.Column(db.String(50), default='lb')
    category = db.Column(db.String(100))
    image_url = db.Column(db.Text)
    is_available = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to Inquiries (one-to-many)
    inquiries = db.relationship('Inquiry', backref='product', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        """
        Provides a developer-friendly representation of the Product object.
        """
        return f'<Product {self.name} (Farmer ID: {self.farmer_id})>'

    def to_dict(self, include_farmer=False):
        """
        Serializes the Product object to a dictionary.
        Optionally includes the related farmer's information.
        """
        data = {
            'id': self.id,
            'farmer_id': self.farmer_id,
            'name': self.name,
            'description': self.description,
            'price': str(self.price), # Keep as string to avoid float precision issues
            'unit': self.unit,
            'category': self.category,
            'image_url': self.image_url,
            'is_available': self.is_available
        }
        if include_farmer and self.farmer:
            # Exclude the farmer's own products to prevent circular recursion
            data['farmer'] = self.farmer.to_dict(include_products=False)
        return data

    def to_dict(self):
        """Serializes the Product object to a dictionary."""
        return {
            'id': self.id,
            'farmer_id': self.farmer_id,
            'name': self.name,
            'description': self.description,
            'price': str(self.price), # Keep as string to avoid float precision issues
            'unit': self.unit,
            'category': self.category,
            'image_url': self.image_url,
            'is_available': self.is_available
        }

    def to_dict(self):
        """Serializes the Product object to a dictionary."""
        return {
            'id': self.id,
            'farmer_id': self.farmer_id,
            'name': self.name,
            'description': self.description,
            'price': str(self.price), # Keep as string to avoid float precision issues
            'unit': self.unit,
            'category': self.category,
            'image_url': self.image_url,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }