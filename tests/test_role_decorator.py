"""
Tests for role-based authorization decorators.

Tests the @role_required, @admin_required, and @farmer_or_admin_required
decorators to ensure proper role-based access control.

Created: 2026-01-01
"""

import pytest
from flask import Flask, jsonify
from flask_jwt_extended import create_access_token, JWTManager, jwt_required


@pytest.fixture
def app_with_decorators():
    """Create a test Flask app with JWT and our decorators."""
    from utils.auth_decorators import role_required, admin_required, farmer_or_admin_required

    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    app.config['TESTING'] = True

    jwt = JWTManager(app)

    # Test routes using our decorators
    @app.route('/farmer-only')
    @jwt_required()
    @role_required(['farmer'])
    def farmer_only():
        return jsonify({'message': 'Farmer access granted'}), 200

    @app.route('/admin-only')
    @jwt_required()
    @admin_required
    def admin_only():
        return jsonify({'message': 'Admin access granted'}), 200

    @app.route('/farmer-or-admin')
    @jwt_required()
    @farmer_or_admin_required
    def farmer_or_admin():
        return jsonify({'message': 'Farmer or admin access granted'}), 200

    return app


def test_role_required_allows_correct_role(app_with_decorators):
    """Test that @role_required(['farmer']) allows farmers."""
    client = app_with_decorators.test_client()

    # Create a farmer token
    with app_with_decorators.app_context():
        token = create_access_token(
            identity='user123',
            additional_claims={'role': 'farmer', 'username': 'testfarmer'}
        )

    # Access farmer-only route
    response = client.get(
        '/farmer-only',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Farmer access granted'


def test_role_required_blocks_wrong_role(app_with_decorators):
    """Test that @role_required(['farmer']) blocks users."""
    client = app_with_decorators.test_client()

    # Create a user token (not farmer)
    with app_with_decorators.app_context():
        token = create_access_token(
            identity='user123',
            additional_claims={'role': 'user', 'username': 'testuser'}
        )

    # Try to access farmer-only route
    response = client.get(
        '/farmer-only',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 403
    data = response.get_json()
    assert data['error'] == 'Forbidden'
    assert 'farmer' in data['message']


def test_admin_required_allows_admin(app_with_decorators):
    """Test that @admin_required allows admins."""
    client = app_with_decorators.test_client()

    # Create an admin token
    with app_with_decorators.app_context():
        token = create_access_token(
            identity='admin123',
            additional_claims={'role': 'admin', 'username': 'testadmin'}
        )

    # Access admin-only route
    response = client.get(
        '/admin-only',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Admin access granted'


def test_admin_required_blocks_farmer(app_with_decorators):
    """Test that @admin_required blocks farmers."""
    client = app_with_decorators.test_client()

    # Create a farmer token
    with app_with_decorators.app_context():
        token = create_access_token(
            identity='user123',
            additional_claims={'role': 'farmer', 'username': 'testfarmer'}
        )

    # Try to access admin-only route
    response = client.get(
        '/admin-only',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 403
    data = response.get_json()
    assert data['error'] == 'Forbidden'


def test_farmer_or_admin_required_allows_farmer(app_with_decorators):
    """Test that @farmer_or_admin_required allows farmers."""
    client = app_with_decorators.test_client()

    # Create a farmer token
    with app_with_decorators.app_context():
        token = create_access_token(
            identity='user123',
            additional_claims={'role': 'farmer', 'username': 'testfarmer'}
        )

    # Access route
    response = client.get(
        '/farmer-or-admin',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Farmer or admin access granted'


def test_farmer_or_admin_required_allows_admin(app_with_decorators):
    """Test that @farmer_or_admin_required allows admins."""
    client = app_with_decorators.test_client()

    # Create an admin token
    with app_with_decorators.app_context():
        token = create_access_token(
            identity='admin123',
            additional_claims={'role': 'admin', 'username': 'testadmin'}
        )

    # Access route
    response = client.get(
        '/farmer-or-admin',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Farmer or admin access granted'


def test_farmer_or_admin_required_blocks_user(app_with_decorators):
    """Test that @farmer_or_admin_required blocks regular users."""
    client = app_with_decorators.test_client()

    # Create a user token
    with app_with_decorators.app_context():
        token = create_access_token(
            identity='user123',
            additional_claims={'role': 'user', 'username': 'testuser'}
        )

    # Try to access route
    response = client.get(
        '/farmer-or-admin',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 403
    data = response.get_json()
    assert data['error'] == 'Forbidden'
