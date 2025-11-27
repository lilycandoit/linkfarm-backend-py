from extensions import db
from .base_model import BaseModel

class Product(BaseModel):
    """
    Represents a product offered by a farmer.
    """
    __tablename__ = 'products'

    farmer_id = db.Column(db.String(36), db.ForeignKey('farmers.id', ondelete='CASCADE'), nullable=False)

    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False) # DECIMAL(10,2)
    unit = db.Column(db.String(50), default='lb')
    category = db.Column(db.String(100))
    stock_quantity = db.Column(db.Integer, default=0)  # Track inventory
    image_url = db.Column(db.Text)
    is_available = db.Column(db.Boolean, default=True)

    # Relationship to Farmer model (one-to-many)
    farmer = db.relationship('Farmer', back_populates='products')

    # Relationship to Inquiries
    inquiries = db.relationship('Inquiry', back_populates='product', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        """
        Provides a developer-friendly representation of the Product object.
        """
        return f'<Product {self.name} (Farmer ID: {self.farmer_id})>'

    def to_dict(self, include_farmer=False, include_inquiries=False):
        """
        Serializes the Product object to a dictionary.
        - Optionally includes the related farmer's information.
        - Optionally includes the list of inquiries for this product.
        """
        data = {
            'id': self.id,
            'farmer_id': self.farmer_id,
            'name': self.name,
            'description': self.description,
            'price': str(self.price),  # Keep as string to avoid float precision issues
            'unit': self.unit,
            'category': self.category,
            'stock_quantity': self.stock_quantity,
            'image_url': self.image_url,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_farmer and self.farmer:
            # Exclude the farmer's own products to prevent circular recursion
            data['farmer'] = self.farmer.to_dict(include_products=False)
        if include_inquiries:
            # Assuming Inquiry model has a to_dict method
            data['inquiries'] = [inquiry.to_dict() for inquiry in self.inquiries]
        return data