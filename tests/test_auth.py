import json

def test_register_user(client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/register' endpoint is posted to (POST)
    THEN check that a new user is created and a 201 status code is returned
    """
    response = client.post('/api/register',
                           data=json.dumps(dict(
                               username='testuser',
                               email='test@example.com',
                               password='password123'
                           )),
                           content_type='application/json')

    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'User registered successfully!'
    assert data['user']['username'] == 'testuser'

def test_login_user_success(client, init_database):
    """
    GIVEN a registered user
    WHEN the '/api/login' endpoint is posted to with correct credentials
    THEN check that a JWT is returned and a 200 status code is returned
    """
    # First, register a user
    client.post('/api/register',
                data=json.dumps(dict(username='testuser', email='test@example.com', password='password123')),
                content_type='application/json')

    # Now, log in
    response = client.post('/api/login',
                           data=json.dumps(dict(
                               username='testuser',
                               password='password123'
                           )),
                           content_type='application/json')

    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Login successful!'
    assert 'token' in data

def test_login_user_failure(client, init_database):
    """
    GIVEN a registered user
    WHEN the '/api/login' endpoint is posted to with incorrect credentials
    THEN check that a 401 status code and an error message are returned
    """
    client.post('/api/register',
                data=json.dumps(dict(username='testuser', email='test@example.com', password='password123')),
                content_type='application/json')

    response = client.post('/api/login',
                           data=json.dumps(dict(username='testuser', password='wrongpassword')),
                           content_type='application/json')

    assert response.status_code == 401
    assert response.get_json()['message'] == 'Invalid credentials.'

def test_get_profile_success(client, user_auth_headers):
    """
    GIVEN a logged-in user
    WHEN the '/api/profile' endpoint is requested with a valid token
    THEN check that the user's profile is returned and the status code is 200
    """
    # Access protected route
    response = client.get('/api/profile', headers=user_auth_headers)

    assert response.status_code == 200
    data = response.get_json()
    assert data['username'] == 'testuser'
    assert data['email'] == 'test@example.com'

def test_get_profile_failure_no_token(client, init_database):
    """
    GIVEN a protected endpoint
    WHEN the endpoint is requested without a token
    THEN check that a 401 status code and an error message are returned
    """
    response = client.get('/api/profile')

    assert response.status_code == 401
    # Flask-JWT-Extended returns 'msg' key, not 'message'
    assert response.get_json()['msg'] == 'Missing Authorization Header'