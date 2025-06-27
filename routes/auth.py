from flask import Blueprint, request, jsonify, current_app, g
from extensions import db
from models.user import User
import jwt
from datetime import datetime, timedelta, timezone
from utils.decorators import token_required

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

    username = data.get('username')
    password = data.get('password')

    # Use modern SQLAlchemy 2.0 syntax for querying
    user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()

    # Use a generic error message to avoid leaking information about whether a username exists
    if not user or not user.check_password(password):
        return jsonify({'error': 'Unauthorized', 'message': 'Invalid credentials.'}), 401

    # --- Create JWT ---
    # The token payload contains the user's ID and expiration information.
    payload = {
        'sub': user.id,  # 'sub' (subject) is a standard claim for user ID
        'iat': datetime.now(timezone.utc),  # 'iat' (issued at) timestamp
        'exp': datetime.now(timezone.utc) + timedelta(hours=24)  # 'exp' (expiration) timestamp
    }

    token = jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )

    return jsonify({
        'message': 'Login successful!',
        'token': token
    }), 200

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """
    A protected route that returns the current user's profile.
    The user is identified by the JWT provided in the Authorization header.
    """
    # The `token_required` decorator has already verified the token
    # and placed the user object in g.current_user.
    current_user = g.current_user

    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'role': current_user.role
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

    # --- Validation ---
    if not data or not all(key in data for key in ['username', 'email', 'password']):
        return jsonify({
            'error': 'Bad Request',
            'message': 'Missing data. Required fields are: username, email, password.'
        }), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Check if user already exists
    # Use modern SQLAlchemy 2.0 syntax for querying
    if db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none():
        return jsonify({'error': 'Conflict', 'message': 'Username already exists.'}), 409

    # Use modern SQLAlchemy 2.0 syntax for querying
    if db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none():
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