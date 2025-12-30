"""
Analytics Routes - Farmer Dashboard Analytics

This module provides analytics endpoints for farmers to track:
- Inquiry volume over time
- Product view statistics
- Conversion metrics (views → inquiries)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User
from models.inquiry import Inquiry
from models.product import Product
from sqlalchemy import func
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/farmers/<string:farmer_id>/stats', methods=['GET'])
@jwt_required()
def get_farmer_analytics(farmer_id):
    """
    Get analytics data for a specific farmer.
    Returns inquiry volume, product views, and conversion metrics.
    """
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({'error': 'Unauthorized', 'message': 'User not found.'}), 401

    # Verify ownership
    is_owner = user.farmer_profile and user.farmer_profile.id == farmer_id
    is_admin = user.role == 'admin'

    if not is_owner and not is_admin:
        return jsonify({'error': 'Forbidden', 'message': 'You are not authorized to view these analytics.'}), 403

    # Get date range from query params (default: last 30 days)
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)

    # 1. Inquiry Volume Over Time (grouped by date)
    inquiry_stats = db.session.query(
        func.date(Inquiry.created_at).label('date'),
        func.count(Inquiry.id).label('count')
    ).filter(
        Inquiry.farmer_id == farmer_id,
        Inquiry.created_at >= start_date
    ).group_by(func.date(Inquiry.created_at)).order_by('date').all()

    # 2. Product View Statistics
    product_views = db.session.query(
        Product.id,
        Product.name,
        Product.view_count,
        Product.category
    ).filter(
        Product.farmer_id == farmer_id
    ).order_by(Product.view_count.desc()).limit(10).all()

    # 3. Total Statistics
    total_inquiries = db.session.query(func.count(Inquiry.id)).filter(
        Inquiry.farmer_id == farmer_id
    ).scalar()

    total_views = db.session.query(func.sum(Product.view_count)).filter(
        Product.farmer_id == farmer_id
    ).scalar() or 0

    total_products = db.session.query(func.count(Product.id)).filter(
        Product.farmer_id == farmer_id
    ).scalar()

    # 4. Conversion Rate (inquiries / views)
    conversion_rate = (total_inquiries / total_views * 100) if total_views > 0 else 0

    return jsonify({
        'inquiry_timeline': [
            {'date': str(stat.date), 'count': stat.count}
            for stat in inquiry_stats
        ],
        'top_products': [
            {
                'id': p.id,
                'name': p.name,
                'views': p.view_count,
                'category': p.category
            }
            for p in product_views
        ],
        'summary': {
            'total_inquiries': total_inquiries,
            'total_views': int(total_views),
            'total_products': total_products,
            'conversion_rate': round(conversion_rate, 2),
            'period_days': days
        }
    }), 200
