"""
Tests for admin-only endpoints.

Tests the admin routes (/api/admin/*) and admin dashboard endpoint
to ensure proper access control and functionality.

Created: 2026-01-01
"""

import pytest


def test_admin_dashboard_as_admin(client, admin_auth_headers):
    """Test that admin can access admin dashboard."""
    response = client.get(
        '/api/dashboard/admin',
        headers=admin_auth_headers
    )

    assert response.status_code == 200
    data = response.get_json()

    # Check that all expected stats are present
    assert 'total_users' in data
    assert 'total_farmers' in data
    assert 'total_products' in data
    assert 'total_inquiries' in data
    assert 'recent_registrations' in data

    # Stats should be integers
    assert isinstance(data['total_users'], int)
    assert isinstance(data['total_farmers'], int)


def test_admin_dashboard_as_farmer(client, farmer_auth_data):
    """Test that farmer cannot access admin dashboard."""
    response = client.get(
        '/api/dashboard/admin',
        headers=farmer_auth_data['headers']
    )

    assert response.status_code == 403
    data = response.get_json()
    assert data['error'] == 'Forbidden'


def test_admin_dashboard_as_user(client, user_auth_headers):
    """Test that regular user cannot access admin dashboard."""
    response = client.get(
        '/api/dashboard/admin',
        headers=user_auth_headers
    )

    assert response.status_code == 403


def test_list_all_farmers_as_admin(client, admin_auth_headers, farmer_auth_data):
    """Test that admin can list all farmers."""
    response = client.get(
        '/api/admin/farmers',
        headers=admin_auth_headers
    )

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    # Should have at least the farmer from fixture
    assert len(data) >= 1


def test_list_all_farmers_as_farmer(client, farmer_auth_data):
    """Test that farmer cannot access admin farmers list."""
    response = client.get(
        '/api/admin/farmers',
        headers=farmer_auth_data['headers']
    )

    assert response.status_code == 403


def test_list_all_products_as_admin(client, admin_auth_headers):
    """Test that admin can list all products."""
    response = client.get(
        '/api/admin/products',
        headers=admin_auth_headers
    )

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_list_all_products_as_farmer(client, farmer_auth_data):
    """Test that farmer cannot access admin products list."""
    response = client.get(
        '/api/admin/products',
        headers=farmer_auth_data['headers']
    )

    assert response.status_code == 403


def test_list_all_inquiries_as_admin(client, admin_auth_headers):
    """Test that admin can list all inquiries."""
    response = client.get(
        '/api/admin/inquiries',
        headers=admin_auth_headers
    )

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_list_all_inquiries_as_farmer(client, farmer_auth_data):
    """Test that farmer cannot access admin inquiries list."""
    response = client.get(
        '/api/admin/inquiries',
        headers=farmer_auth_data['headers']
    )

    assert response.status_code == 403


def test_admin_can_update_any_farmer_profile(client, admin_auth_headers, farmer_auth_data):
    """Test that admin can update any farmer profile."""
    farmer_id = farmer_auth_data['farmer_id']

    # Admin updates farmer profile (should work)
    response = client.put(
        f'/api/farmers/{farmer_id}',
        json={'farm_name': 'Admin Updated Farm'},
        headers=admin_auth_headers
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['farmer']['farm_name'] == 'Admin Updated Farm'


def test_admin_can_delete_any_product(client, admin_auth_headers, farmer_auth_data):
    """Test that admin can delete any product."""
    import json

    # Create a product owned by farmer
    create_response = client.post(
        '/api/products',
        headers=farmer_auth_data['headers'],
        data=json.dumps({
            'name': 'Test Product',
            'price': '10.00',
            'unit': 'kg',
            'category': 'Vegetables'
        }),
        content_type='application/json'
    )

    assert create_response.status_code == 201
    product_id = create_response.get_json()['product']['id']

    # Admin deletes farmer's product (should work)
    response = client.delete(
        f'/api/products/{product_id}',
        headers=admin_auth_headers
    )

    assert response.status_code == 200


def test_farmer_cannot_delete_other_farmers_product(client, farmer_auth_data, second_farmer_auth_data):
    """Test that farmer cannot delete another farmer's product."""
    import json

    # Create a product owned by farmer2
    create_response = client.post(
        '/api/products',
        headers=second_farmer_auth_data['headers'],
        data=json.dumps({
            'name': 'Farmer2 Product',
            'price': '15.00',
            'unit': 'kg',
            'category': 'Fruits'
        }),
        content_type='application/json'
    )

    assert create_response.status_code == 201
    product_id = create_response.get_json()['product']['id']

    # Farmer1 tries to delete farmer2's product (should fail)
    response = client.delete(
        f'/api/products/{product_id}',
        headers=farmer_auth_data['headers']
    )

    assert response.status_code == 403
    data = response.get_json()
    assert data['error'] == 'Forbidden'
