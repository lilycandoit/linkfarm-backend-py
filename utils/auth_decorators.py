"""
Role-based authorization decorators for flask-jwt-extended.

These decorators work with the modern flask-jwt-extended library to provide
reusable role-based access control across all routes.

Usage:
    @jwt_required()
    @role_required(['farmer', 'admin'])
    def farmer_only_route():
        ...

    @jwt_required()
    @admin_required
    def admin_only_route():
        ...

Created: 2026-01-01
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def role_required(allowed_roles):
    """
    Decorator to require specific roles for accessing a route.

    This decorator must be used AFTER @jwt_required() to ensure the JWT
    is verified before checking roles.

    Args:
        allowed_roles (list): List of role strings that are allowed access.
                             Valid roles: 'user', 'farmer', 'admin'

    Returns:
        Decorated function that checks user role before executing.
        Returns 403 Forbidden if user role is not in allowed_roles.

    Example:
        @app.route('/farmers/<id>/products')
        @jwt_required()
        @role_required(['farmer', 'admin'])
        def get_farmer_products(id):
            return jsonify({'products': [...]})
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Verify JWT is present (should already be done by @jwt_required)
            verify_jwt_in_request()

            # Get JWT claims
            claims = get_jwt()
            user_role = claims.get('role', 'user')

            # Check if user's role is in allowed roles
            if user_role not in allowed_roles:
                return jsonify({
                    'error': 'Forbidden',
                    'message': f'This endpoint requires one of the following roles: {", ".join(allowed_roles)}'
                }), 403

            # Role is valid, proceed to route handler
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(fn):
    """
    Shortcut decorator for admin-only routes.

    Equivalent to @role_required(['admin']) but more concise.
    Must be used AFTER @jwt_required().

    Example:
        @app.route('/admin/dashboard')
        @jwt_required()
        @admin_required
        def admin_dashboard():
            return jsonify({'stats': {...}})
    """
    return role_required(['admin'])(fn)


def farmer_or_admin_required(fn):
    """
    Shortcut decorator for routes accessible by farmers and admins.

    Equivalent to @role_required(['farmer', 'admin']) but more concise.
    Must be used AFTER @jwt_required().

    Example:
        @app.route('/farmers/<id>/inquiries')
        @jwt_required()
        @farmer_or_admin_required
        def list_inquiries(id):
            return jsonify({'inquiries': [...]})
    """
    return role_required(['farmer', 'admin'])(fn)
