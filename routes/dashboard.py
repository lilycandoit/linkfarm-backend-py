from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from models.user import User
from models.farmer import Farmer
from models.product import Product
from models.inquiry import Inquiry
from utils.auth_decorators import role_required, admin_required
from datetime import datetime, timedelta

# Create a Blueprint for dashboard routes
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/farmer', methods=['GET'])
@jwt_required()
@role_required(['farmer'])
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


@dashboard_bp.route('/dashboard/admin', methods=['GET'])
@jwt_required()
@admin_required
def get_admin_dashboard():
    """
    Admin dashboard with system-wide statistics.

    Protected route - requires JWT token with 'admin' role.

    Returns:
        - total_users: Total number of users in the system
        - total_farmers: Total number of farmer profiles
        - total_products: Total number of products listed
        - total_inquiries: Total number of customer inquiries
        - recent_registrations: Number of new users in last 7 days
    """
    # Get counts for all entities
    total_users = db.session.query(User).count()
    total_farmers = db.session.query(Farmer).count()
    total_products = db.session.query(Product).count()
    total_inquiries = db.session.query(Inquiry).count()

    # Get recent activity (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_users = db.session.query(User).filter(
        User.created_at >= seven_days_ago
    ).count()

    return jsonify({
        'total_users': total_users,
        'total_farmers': total_farmers,
        'total_products': total_products,
        'total_inquiries': total_inquiries,
        'recent_registrations': recent_users
    }), 200