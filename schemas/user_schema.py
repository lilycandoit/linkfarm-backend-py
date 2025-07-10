from extensions import ma
from models.user import User
from marshmallow import fields, validate

class UserRegisterSchema(ma.Schema):
    """
    Schema for validating user registration data.
    This is where we define the rules for our data.
    """
    # Use Marshmallow's built-in email validator.
    email = fields.Email(required=True)

    # This is the crucial fix: Add a password length validator.
    # It ensures the password is at least 8 characters long.
    password = fields.Str(required=True, validate=validate.Length(min=8, error="Password must be at least 8 characters long."))

    # Also add a validator for the username.
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))

    class Meta:
        # This tells Marshmallow to ignore any extra fields sent in the request.
        unknown = "EXCLUDE"

class UserSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for serializing User data for display.
    It automatically generates fields from the User model.
    """
    # Use a string to prevent circular import errors at startup.
    # `dump_only=True` is correct as you wouldn't update a user by providing a profile.
    farmer_profile = ma.Nested("FarmerSchema", dump_only=True)

    class Meta:
        model = User
        # Exclude the password hash for security. Never send this to the frontend.
        exclude = ("password_hash",)

user_schema = UserSchema()
users_schema = UserSchema(many=True)