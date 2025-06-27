from extensions import db
from datetime import datetime

class Product(db.Model):
    """
    Represents a product offered by a farmer.
    """
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    # Foreign key to the farmers table, if a farmer is deleted, their products are also deleted.
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