from flask import Blueprint, request, jsonify, current_app
from extensions import db, ma
from sqlalchemy import or_
from models.user import User
from schemas.user_schema import UserRegisterSchema
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
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
    role = validated_data.get('role', 'farmer')  # Default to 'farmer' if not provided

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
    new_user = User(username=username, email=email, role=role)
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

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Returns the authenticated user's profile information.
    Includes farmer profile details if applicable.
    """
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({'error': 'Not Found', 'message': 'User not found.'}), 404

    profile_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'created_at': user.created_at.isoformat()
    }

    if user.farmer_profile:
        profile_data['farmer_id'] = user.farmer_profile.id
        profile_data['farm_name'] = user.farmer_profile.farm_name
        profile_data['profile_image_url'] = user.farmer_profile.profile_image_url

    return jsonify(profile_data), 200

@auth_bp.route('/settings', methods=['PUT'])
@jwt_required()
def update_settings():
    """
    Updates user account settings: email and password.
    Requires current password for validation.
    """
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({'error': 'Not Found', 'message': 'User not found.'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Bad Request', 'message': 'No data provided.'}), 400

    current_password = data.get('current_password')
    if not current_password:
        return jsonify({'error': 'Bad Request', 'message': 'Current password is required.'}), 400

    if not user.check_password(current_password):
        return jsonify({'error': 'Unauthorized', 'message': 'Incorrect current password.'}), 401

    # Update email if provided
    new_email = data.get('email')
    if new_email and new_email != user.email:
        existing_email = db.session.execute(
            db.select(User).where(User.email == new_email)
        ).scalar_one_or_none()
        if existing_email:
            return jsonify({'error': 'Conflict', 'message': 'Email is already in use.'}), 409
        user.email = new_email

    # Update password if provided
    new_password = data.get('new_password')
    if new_password:
        if len(new_password) < 8:
            return jsonify({'error': 'Bad Request', 'message': 'New password too short.'}), 400
        user.set_password(new_password)

    try:
        db.session.commit()
        return jsonify({'message': 'Settings updated successfully.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500