import json
from models.product import Product
from extensions import db

# --- Test Create Product (POST /products) ---

def test_create_product_success(client, farmer_auth_data):
    """
    GIVEN a logged-in farmer
    WHEN the '/api/products' endpoint is posted to with valid data
    THEN check that a new product is created and a 201 status code is returned
    """
    response = client.post('/api/products',
                           headers=farmer_auth_data['headers'],
                           data=json.dumps(dict(
                               name="Organic Carrots",
                               price=2.99,
                               unit="bunch"
                           )),
                           content_type='application/json')

    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Product created successfully!'
    assert data['product']['name'] == 'Organic Carrots'

def test_create_product_by_non_farmer(client, user_auth_headers):
    """
    GIVEN a standard user (not a farmer)
    WHEN they attempt to post to the '/api/products' endpoint
    THEN check that a 403 Forbidden error is returned
    """
    response = client.post('/api/products',
                           headers=user_auth_headers,
                           data=json.dumps(dict(name="Illegal Carrots", price=1.00)),
                           content_type='application/json')

    assert response.status_code == 403

# --- Test Read Product (GET /products/<id> and GET /farmers/<id>/products) ---

def test_get_public_product(client, farmer_auth_data):
    """
    GIVEN a product exists
    WHEN the '/api/products/<id>' endpoint is requested without authentication
    THEN check that the product data is returned with a 200 status code
    """
    # First, create a product to fetch
    create_res = client.post('/api/products', headers=farmer_auth_data['headers'], data=json.dumps(dict(name="Public Apples", price=4.50)), content_type='application/json')
    product_id = create_res.get_json()['product']['id']

    # Now, fetch it publicly
    response = client.get(f'/api/products/{product_id}')
    assert response.status_code == 200
    assert response.get_json()['name'] == 'Public Apples'

def test_list_products_by_farmer(client, farmer_auth_data):
    """
    GIVEN a farmer with several products
    WHEN the '/api/farmers/<farmer_id>/products' endpoint is requested
    THEN check that a list of that farmer's products is returned
    """
    headers = farmer_auth_data['headers']
    farmer_id = farmer_auth_data['farmer_id']

    # Create a couple of products for this farmer
    client.post('/api/products', headers=headers, data=json.dumps(dict(name="Product A", price=1)), content_type='application/json')
    client.post('/api/products', headers=headers, data=json.dumps(dict(name="Product B", price=2)), content_type='application/json')

    response = client.get(f'/api/farmers/{farmer_id}/products')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]['name'] == 'Product A'

# --- Test Update/Delete and Ownership ---

def test_update_product_as_owner(client, farmer_auth_data):
    """
    GIVEN a farmer who owns a product
    WHEN they send a PUT request to their product's endpoint
    THEN check that the product is updated successfully
    """
    headers = farmer_auth_data['headers']
    create_res = client.post('/api/products', headers=headers, data=json.dumps(dict(name="Original Name", price=10)), content_type='application/json')
    product_id = create_res.get_json()['product']['id']

    response = client.put(f'/api/products/{product_id}',
                          headers=headers,
                          data=json.dumps(dict(name="Updated Name")),
                          content_type='application/json')

    assert response.status_code == 200
    product = db.session.get(Product, product_id)
    assert product.name == "Updated Name"

def test_update_product_as_another_farmer_fails(client, farmer_auth_data, second_farmer_auth_data):
    """
    GIVEN two farmers, A and B, where farmer A owns a product
    WHEN farmer B attempts to update farmer A's product
    THEN check that a 403 Forbidden error is returned
    """
    # Farmer A creates a product
    create_res = client.post('/api/products', headers=farmer_auth_data['headers'], data=json.dumps(dict(name="Farmer A's Product", price=10)), content_type='application/json')
    product_id = create_res.get_json()['product']['id']

    # Farmer B tries to update it
    response = client.put(f'/api/products/{product_id}',
                          headers=second_farmer_auth_data['headers'],
                          data=json.dumps(dict(name="Illegal Update")),
                          content_type='application/json')

    assert response.status_code == 403
    assert response.get_json()['message'] == 'You are not authorized to update this product.'

def test_delete_product_as_admin_succeeds(client, admin_auth_headers, farmer_auth_data):
    """
    GIVEN a product owned by a farmer and a logged-in admin
    WHEN the admin sends a DELETE request to the product's endpoint
    THEN check that the product is deleted successfully
    """
    # Farmer creates a product
    create_res = client.post('/api/products', headers=farmer_auth_data['headers'], data=json.dumps(dict(name="Product to be deleted", price=10)), content_type='application/json')
    product_id = create_res.get_json()['product']['id']

    # Admin deletes it
    response = client.delete(f'/api/products/{product_id}', headers=admin_auth_headers)

    assert response.status_code == 200
    product = db.session.get(Product, product_id)
    assert product is None