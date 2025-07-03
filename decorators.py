from functools import wraps
from flask import request, jsonify, current_app
import jwt
from models.user import User
from extensions import db

def jwt_required(f):
    """
    A decorator to protect routes with JWT authentication.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # This is the key fix: Allow OPTIONS requests to pass through
        # without any token checks. The browser sends this "preflight"
        # request to check CORS permissions before the actual request.
        if request.method == 'OPTIONS':
            return jsonify({'message': 'CORS preflight request successful'}), 200

        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'error': 'Unauthorized', 'message': 'Authorization token is missing'}), 401

        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = db.session.get(User, payload['sub'])
            if not current_user:
                 return jsonify({'error': 'Unauthorized', 'message': 'User not found for token'}), 401
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return jsonify({'error': 'Unauthorized', 'message': 'Token is invalid or expired'}), 401

        return f(current_user=current_user, *args, **kwargs)
    return decorated_function