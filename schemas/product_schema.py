from extensions import ma
from models.product import Product

class ProductSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for serializing and validating Product data.
    """
    # When dumping a product, we want the farmer's info,
    # but we must exclude the farmer's own product list to prevent an infinite loop.
    farmer = ma.Nested("FarmerSchema", dump_only=True, exclude=("products",))

    class Meta:
        model = Product
        load_instance = True
        # Exclude fields managed by the backend or defined in the relationship.
        exclude = ('farmer_id', 'created_at', 'updated_at')

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)