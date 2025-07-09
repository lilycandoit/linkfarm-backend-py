from flask import Blueprint, request, jsonify, current_app
from extensions import db, ma
from sqlalchemy import or_
from models.user import User
from schemas.user_schema import UserRegisterSchema
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError

# Create a Blueprint for authentication routes
# The name 'auth' is used internally by Flask for routing and URL generation.
# __name__ is the standard Python way to refer to the current module.
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login_user():
    """
    Authenticates a user and returns a JWT.
    Expects a JSON payload with 'username' and 'password'.
    """
    data = request.get_json()

    if not data or not all(key in data for key in ['username', 'password']):
        return jsonify({
            'error': 'Bad Request',
            'message': 'Missing username or password.'
        }), 400

    login_identifier = data.get('username')
    password = data.get('password')

    # Use modern SQLAlchemy 2.0 syntax to find the user by either username or email.
    user = db.session.execute(
        db.select(User).where(
            or_(User.username == login_identifier, User.email == login_identifier)
        )
    ).scalar_one_or_none()

    # Use a generic error message to avoid leaking information about whether a username exists
    if not user or not user.check_password(password):
        return jsonify({'error': 'Unauthorized', 'message': 'Invalid credentials.'}), 401

    # --- Create JWT using flask-jwt-extended ---
    # The `identity` is stored in the 'sub' claim of the token.
    # We can add custom data to the token using the `additional_claims` parameter.
    # The library handles expiration ('exp') and issued at ('iat') automatically.
    additional_claims = {"role": user.role, "username": user.username}
    token = create_access_token(identity=user.id, additional_claims=additional_claims)

    return jsonify({
        'message': 'Login successful!',
        'token': token
    }), 200

# User Registration endpoint
@auth_bp.route('/register', methods=['POST'])
def register_user():
    """
    Registers a new user.
    Expects a JSON payload with 'username', 'email', and 'password'.
    This route will be accessible at /api/register due to the Blueprint's url_prefix.
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Bad Request", "message": "No input data provided"}), 400

    schema = UserRegisterSchema()

    # --- Validation ---
    try:
        # Validate the incoming data against the rules in our schema.
        validated_data = schema.load(data)
    except ValidationError as err:
        # If validation fails, return a 400 error with detailed messages.
        return jsonify({'error': 'Validation Error', 'messages': err.messages}), 400

    username = validated_data['username']
    email = validated_data['email']
    password = validated_data['password']

    # Check if username or email already exists in a single, efficient query.
    existing_user = db.session.execute(
        db.select(User).where(or_(User.username == username, User.email == email))
    ).scalar_one_or_none()

    if existing_user:
        if existing_user.username == username:
            return jsonify({'error': 'Conflict', 'message': 'Username already exists.'}), 409
        # Since we know the user exists, if the username doesn't match, the email must.
        return jsonify({'error': 'Conflict', 'message': 'Email already registered.'}), 409

    # --- Create and save new user ---
    new_user = User(username=username, email=email)
    new_user.set_password(password) # Securely hash the password

    db.session.add(new_user)
    db.session.commit()

    # --- Return success response (omitting password hash for security) ---
    return jsonify({
        'message': 'User registered successfully!',
        'user': {
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email
        }
    }), 201