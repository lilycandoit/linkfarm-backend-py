from extensions import db
from datetime import datetime

class Inquiry(db.Model):
    """
    Represents a customer inquiry about a product or farmer.
    """
    __tablename__ = 'inquiries'

    id = db.Column(db.Integer, primary_key=True)
    # Foreign key to the farmers table. If a farmer is deleted, their inquiries are also deleted.
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id', ondelete='CASCADE'), nullable=False)
    # Foreign key to the products table. If a product is deleted, this field is set to NULL.
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='SET NULL'), nullable=True)

    customer_name = db.Column(db.String(255), nullable=False)
    customer_email = db.Column(db.String(255), nullable=False)
    customer_phone = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='new') # e.g., 'new', 'read', 'responded', 'archived'

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        """
        Provides a developer-friendly representation of the Inquiry object.
        """
        return f'<Inquiry {self.id} (Farmer ID: {self.farmer_id}, Product ID: {self.product_id})>'