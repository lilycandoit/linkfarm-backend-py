from extensions import ma
from models.product import Product

class ProductSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for serializing and validating Product data.
    """
    # Use a string "FarmerSchema" to avoid circular import issues at startup.
    farmer = ma.Nested("FarmerSchema", dump_only=True)

    class Meta:
        model = Product
        load_instance = True
        # Exclude fields managed by the backend or defined in the relationship.
        exclude = ('farmer_id', 'created_at', 'updated_at')

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)