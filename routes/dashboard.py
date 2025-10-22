from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from models.user import User

# Create a Blueprint for dashboard routes
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/farmer', methods=['GET'])
@jwt_required()
def get_farmer_dashboard():
    """
    A private endpoint for a logged-in farmer to get all their data in one call.
    This is a key optimization for the frontend, especially on slow networks.

    Protected route - requires JWT token with 'farmer' role.
    """
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({'error': 'Unauthorized', 'message': 'User not found.'}), 401

    # Check role - must be farmer
    jwt_claims = get_jwt()
    user_role = jwt_claims.get('role', 'user')

    if user_role != 'farmer':
        return jsonify({'error': 'Forbidden', 'message': 'This endpoint requires farmer role.'}), 403

    # Get farmer profile
    farmer = user.farmer_profile
    if not farmer:
        return jsonify({'error': 'Not Found', 'message': 'Farmer profile not found.'}), 404

    # Serialize all necessary data into a single response object
    # Using to_dict() methods ensures consistent serialization across the API
    dashboard_data = {
        'profile': farmer.to_dict(),
        'products': [product.to_dict() for product in farmer.products],
        'inquiries': [inquiry.to_dict(include_product=True) for inquiry in farmer.inquiries]
    }
    return jsonify(dashboard_data), 200