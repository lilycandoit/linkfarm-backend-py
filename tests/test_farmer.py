import json
from models.user import User
from models.farmer import Farmer
from extensions import db

# --- Test Create Farmer Profile (POST /farmers) ---

def test_create_farmer_profile_success(client, user_auth_headers):
    """
    GIVEN a standard authenticated user
    WHEN the '/api/farmers' endpoint is posted to with valid data
    THEN check that a new farmer profile is created, the user's role is promoted, and a 201 status code is returned
    """
    response = client.post('/api/farmers',
                           headers=user_auth_headers,
                           data=json.dumps(dict(
                               name="John Doe",
                               farm_name="Sunny Meadow Farm",
                               location="Green Valley",
                               phone="555-1234",
                               bio="A sunny farm in the valley"
                           )),
                           content_type='application/json')

    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Farmer profile created successfully!'
    assert data['farmer']['farm_name'] == "Sunny Meadow Farm"

    # Verify the user's role was promoted in the database
    user = db.session.execute(db.select(User).filter_by(username='testuser')).scalar_one()
    assert user.role == 'farmer'

def test_create_farmer_profile_conflict(client, farmer_auth_data):
    """
    GIVEN a user who already has a farmer profile
    WHEN the '/api/farmers' endpoint is posted to again
    THEN check that a 409 conflict error is returned
    """
    response = client.post('/api/farmers',
                           headers=farmer_auth_data['headers'],
                           data=json.dumps(dict(farm_name="Another Farm")),
                           content_type='application/json')

    assert response.status_code == 409
    assert response.get_json()['message'] == 'User already has a farmer profile.'

# --- Test Read Farmer Profile (GET /farmers/<id>) ---

def test_get_farmer_profile(client, user_auth_headers, farmer_auth_data):
    """
    GIVEN an authenticated user and an existing farmer profile
    WHEN the '/api/farmers/<id>' endpoint is requested
    THEN check that the farmer's profile data is returned with a 200 status code
    """
    farmer_id = farmer_auth_data['farmer_id']
    response = client.get(f'/api/farmers/{farmer_id}', headers=user_auth_headers)

    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == farmer_id
    assert data['farm_name'] == "Test Farm"

def test_get_nonexistent_farmer_profile(client, user_auth_headers):
    """
    GIVEN an authenticated user
    WHEN a non-existent farmer profile is requested
    THEN check that a 404 not found error is returned
    """
    response = client.get('/api/farmers/9999', headers=user_auth_headers)
    assert response.status_code == 404

# --- Test Update Farmer Profile (PUT /farmers/<id>) ---

def test_update_farmer_profile_as_owner(client, farmer_auth_data):
    """
    GIVEN a farmer
    WHEN they update their own profile via the '/api/farmers/<id>' endpoint
    THEN check that the profile is updated and a 200 status code is returned
    """
    farmer_id = farmer_auth_data['farmer_id']
    headers = farmer_auth_data['headers']

    response = client.put(f'/api/farmers/{farmer_id}',
                          headers=headers,
                          data=json.dumps(dict(bio="Updated bio")),
                          content_type='application/json')

    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Farmer profile updated successfully!'
    # Verify the change in the database
    farmer = db.session.get(Farmer, farmer_id)
    assert farmer.bio == "Updated bio"

def test_update_farmer_profile_as_admin(client, admin_auth_headers, farmer_auth_data):
    """
    GIVEN an admin user and a farmer profile
    WHEN the admin updates the farmer's profile
    THEN check that the profile is updated and a 200 status code is returned
    """
    farmer_id = farmer_auth_data['farmer_id']

    response = client.put(f'/api/farmers/{farmer_id}',
                          headers=admin_auth_headers,
                          data=json.dumps(dict(farm_name="Admin Updated Farm Name")),
                          content_type='application/json')

    assert response.status_code == 200
    farmer = db.session.get(Farmer, farmer_id)
    assert farmer.farm_name == "Admin Updated Farm Name"

def test_update_farmer_profile_unauthorized(client, user_auth_headers, farmer_auth_data):
    """
    GIVEN a standard user (not the owner)
    WHEN they attempt to update a farmer's profile
    THEN check that a 403 forbidden error is returned because their role is 'user', not 'farmer'
    """
    farmer_id = farmer_auth_data['farmer_id']

    # This test uses a different user ('testuser') than the one who owns the farmer profile ('testfarmer')
    # We need to create a separate user for this test.
    client.post('/api/register', data=json.dumps(dict(username='anotheruser', email='another@user.com', password='password')), content_type='application/json')
    login_res = client.post('/api/login', data=json.dumps(dict(username='anotheruser', password='password')), content_type='application/json')
    another_user_headers = {'Authorization': f'Bearer {login_res.get_json()["token"]}'}

    response = client.put(f'/api/farmers/{farmer_id}',
                          headers=another_user_headers,
                          data=json.dumps(dict(farm_name="Unauthorized Update")),
                          content_type='application/json')

    assert response.status_code == 403
    assert response.get_json()['message'] == 'You do not have the necessary permissions to access this resource.'