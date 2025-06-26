from functools import wraps
from flask import request, jsonify, g, current_app
import jwt
from models.user import User

def token_required(f):
    """
    A decorator to ensure that a valid JWT is present in the request header.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check for token in the 'Authorization' header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            # The header should be in the format "Bearer <token>"
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Malformed token header. Expected "Bearer <token>".'}), 401

        if not token:
            return jsonify({'error': 'Unauthorized', 'message': 'Token is missing!'}), 401

        try:
            # Decode the token using the app's SECRET_KEY
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            # Find the user based on the 'sub' (subject) claim in the token
            current_user = User.query.get(data['sub'])
            if not current_user:
                 return jsonify({'error': 'Unauthorized', 'message': 'User not found.'}), 401
            # Store the user object in Flask's 'g' object for this request
            g.current_user = current_user
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Unauthorized', 'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Unauthorized', 'message': 'Token is invalid!'}), 401

        # The token is valid, and the user is loaded. Proceed to the route function.
        return f(*args, **kwargs)

    return decorated