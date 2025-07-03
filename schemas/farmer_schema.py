from extensions import ma
from models.farmer import Farmer

class FarmerSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for serializing and validating Farmer data.
    It automatically generates fields from the Farmer model, ensuring consistency.
    """
    # Use marshmallow's nested fields to include related data when requested.
    # By using a string "ProductSchema", we allow Marshmallow to find the class
    # later, avoiding the circular import error at startup.
    products = ma.Nested("ProductSchema", many=True, dump_only=True)

    class Meta:
        model = Farmer
        load_instance = True
        # Exclude fields that are managed by the backend and not provided by the user.
        exclude = ('user_id', 'created_at', 'updated_at')

farmer_schema = FarmerSchema()
farmers_schema = FarmerSchema(many=True)