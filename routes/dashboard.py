from flask import Blueprint, jsonify, g
from utils.decorators import token_required, role_required

# Create a Blueprint for dashboard routes
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/farmer', methods=['GET'])
@token_required
@role_required(['farmer'])
def get_farmer_dashboard():
    """
    A private endpoint for a logged-in farmer to get all their data in one call.
    This is a key optimization for the frontend, especially on slow networks.
    """
    farmer = g.current_user.farmer

    # Serialize all necessary data into a single response object
    dashboard_data = {
        'profile': farmer.to_dict(),
        'products': [product.to_dict() for product in farmer.products],
        'inquiries': [{
            'id': inquiry.id,
            'customer_name': inquiry.customer_name,
            'message': inquiry.message,
            'status': inquiry.status
        } for inquiry in farmer.inquiries]
    }
    return jsonify(dashboard_data), 200