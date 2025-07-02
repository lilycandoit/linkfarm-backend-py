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