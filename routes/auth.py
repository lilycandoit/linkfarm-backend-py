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

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Initiates password reset process by sending reset email.
    Expects JSON with 'email' field.
    Returns generic success message to prevent email enumeration.
    """
    data = request.get_json()

    if not data or 'email' not in data:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Email is required.'
        }), 400

    email = data.get('email', '').strip().lower()

    # Find user by email
    user = db.session.execute(
        db.select(User).where(User.email == email)
    ).scalar_one_or_none()

    # IMPORTANT: Always return success to prevent email enumeration
    # Don't reveal if email exists or not
    if user:
        # Generate reset token
        token = user.generate_reset_token()

        try:
            db.session.commit()

            # Send reset email
            from services.email_service import send_password_reset_email
            send_password_reset_email(user.email, user.username, token)

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Failed to process password reset: {str(e)}')
            # Still return success to user to prevent enumeration

    # Generic success message regardless of whether email exists
    return jsonify({
        'message': 'If an account exists with that email, a password reset link has been sent.'
    }), 200


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Completes password reset with token validation.
    Expects JSON with 'token' and 'new_password'.
    After successful reset, returns a new JWT for auto-login.
    """
    data = request.get_json()

    if not data or not all(key in data for key in ['token', 'new_password']):
        return jsonify({
            'error': 'Bad Request',
            'message': 'Token and new password are required.'
        }), 400

    token = data.get('token')
    new_password = data.get('new_password')

    # Validate password strength
    if len(new_password) < 8:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Password must be at least 8 characters long.'
        }), 400

    # Find user by reset token
    user = db.session.execute(
        db.select(User).where(User.reset_token == token)
    ).scalar_one_or_none()

    if not user:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Invalid or expired reset token.'
        }), 400

    # Verify token is valid and not expired
    if not user.verify_reset_token(token):
        return jsonify({
            'error': 'Bad Request',
            'message': 'Invalid or expired reset token.'
        }), 400

    try:
        # Update password
        user.set_password(new_password)

        # Clear reset token (one-time use)
        user.clear_reset_token()

        db.session.commit()

        # Create new JWT for auto-login (invalidates old sessions)
        # Note: In JWT, we can't truly "invalidate" old tokens server-side
        # unless we implement a token blacklist. However, by issuing a new token
        # and user changing their password, any compromised tokens become less useful
        # as the attacker no longer knows the new password.
        additional_claims = {"role": user.role, "username": user.username}
        new_token = create_access_token(identity=user.id, additional_claims=additional_claims)

        return jsonify({
            'message': 'Password reset successful.',
            'token': new_token  # Auto-login token
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Failed to reset password: {str(e)}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while resetting your password.'
        }), 500