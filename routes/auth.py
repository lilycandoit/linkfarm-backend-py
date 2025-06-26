from flask import Blueprint, request, jsonify
from extensions import db
from models.user import User

# Create a Blueprint for authentication routes
# The name 'auth' is used internally by Flask for routing and URL generation.
# __name__ is the standard Python way to refer to the current module.
auth_bp = Blueprint('auth', __name__)

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
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Conflict', 'message': 'Username already exists.'}), 409

    if User.query.filter_by(email=email).first():
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