from extensions import db
from datetime import datetime
from .base_model import BaseModel

class Inquiry(BaseModel):
    """
    Represents a customer inquiry about a product or farmer.
    """
    __tablename__ = 'inquiries'

    # Foreign key to the farmers table. If a farmer is deleted, their inquiries are also deleted.
    farmer_id = db.Column(db.String(36), db.ForeignKey('farmers.id', ondelete='CASCADE'), nullable=False)
    # Foreign key to the products table. If a product is deleted, this field is set to NULL.
    product_id = db.Column(db.String(36), db.ForeignKey('products.id', ondelete='SET NULL'), nullable=True)

    customer_name = db.Column(db.String(255), nullable=False)
    customer_email = db.Column(db.String(255), nullable=False)
    customer_phone = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='new') # e.g., 'new', 'read', 'responded', 'archived'

    # relationship with other models
    farmer = db.relationship('Farmer', back_populates='inquiries')

    product = db.relationship('Product', back_populates='inquiries')


    def __repr__(self):
        """
        Provides a developer-friendly representation of the Inquiry object.
        """
        return f'<Inquiry {self.id} (Farmer ID: {self.farmer_id}, Product ID: {self.product_id})>'