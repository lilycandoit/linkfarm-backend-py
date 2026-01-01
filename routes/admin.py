"""
Admin Routes - Platform Management Endpoints

This module provides admin-only endpoints for viewing and managing
all resources across the platform.

All routes in this module require the 'admin' role.

Created: 2026-01-01
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from models.user import User
from models.farmer import Farmer
from models.product import Product
from models.inquiry import Inquiry
from utils.auth_decorators import admin_required

# Create a Blueprint for admin routes
admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def list_all_users():
    """
    Admin endpoint to list all registered users.

    Returns:
        List of all user accounts (without password hashes).

    Protected route - requires JWT token with 'admin' role.
    """
    users = db.session.execute(db.select(User)).scalars().all()
    return jsonify([u.to_dict() for u in users]), 200


@admin_bp.route('/farmers', methods=['GET'])
@jwt_required()
@admin_required
def list_all_farmers():
    """
    Admin endpoint to list all farmers with their products.

    Returns:
        List of all farmer profiles with nested product information.

    Protected route - requires JWT token with 'admin' role.
    """
    farmers = db.session.execute(db.select(Farmer)).scalars().all()
    return jsonify([f.to_dict(include_products=True) for f in farmers]), 200


@admin_bp.route('/products', methods=['GET'])
@jwt_required()
@admin_required
def list_all_products():
    """
    Admin endpoint to list all products with farmer information.

    Returns:
        List of all products with nested farmer information.

    Protected route - requires JWT token with 'admin' role.
    """
    products = db.session.execute(db.select(Product)).scalars().all()
    return jsonify([p.to_dict(include_farmer=True) for p in products]), 200


@admin_bp.route('/inquiries', methods=['GET'])
@jwt_required()
@admin_required
def list_all_inquiries():
    """
    Admin endpoint to list all inquiries across all farmers.

    Returns:
        List of all customer inquiries with product information.

    Protected route - requires JWT token with 'admin' role.
    """
    inquiries = db.session.execute(db.select(Inquiry)).scalars().all()
    return jsonify([i.to_dict(include_product=True) for i in inquiries]), 200
