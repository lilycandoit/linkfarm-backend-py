from extensions import ma
from models.farmer import Farmer

class FarmerSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for serializing and validating Farmer data.
    It automatically generates fields from the Farmer model, ensuring consistency.
    """
    # Use marshmallow's nested fields to include related data when requested.
    # When dumping a farmer, we want their products, but we must exclude the
    # back-reference to the farmer from each product to prevent an infinite loop.
    products = ma.Nested("ProductSchema", many=True, dump_only=True, exclude=("farmer",))

    class Meta:
        model = Farmer
        load_instance = True
        # Exclude fields that are managed by the backend and not provided by the user.
        exclude = ('user_id', 'created_at', 'updated_at')

farmer_schema = FarmerSchema()
farmers_schema = FarmerSchema(many=True)