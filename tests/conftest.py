import pytest
from app import create_app
from extensions import db
import json
from models.user import User
from models.farmer import Farmer

@pytest.fixture(scope='module')
def app():
    """
    Creates a test Flask application instance for the entire test module.
    """
    # Use the 'testing' configuration
    flask_app = create_app('testing')

    with flask_app.app_context():
        yield flask_app

@pytest.fixture(scope='module')
def client(app):
    """
    Creates a test client for making requests to the application.
    """
    return app.test_client()

@pytest.fixture(scope='function')
def init_database(app):
    """
    Initializes the database for each test function.
    This ensures each test starts with a clean slate.
    """
    with app.app_context():
        db.create_all()

        yield db  # this is where the testing happens

        # Teardown: drop all tables after the test is done
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def user_auth_headers(client, init_database):
    """
    Fixture to register and log in a standard user with the 'user' role, returning auth headers.
    """
    # Register a user
    client.post('/api/register',
                data=json.dumps(dict(
                    username='testuser',
                    email='test@example.com',
                    password='password123'
                )),
                content_type='application/json')

    # Log in to get a token
    login_res = client.post('/api/login',
                            data=json.dumps(dict(
                                username='testuser',
                                password='password123'
                            )),
                            content_type='application/json')

    token = login_res.get_json()['token']
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture(scope='function')
def admin_auth_headers(client, init_database):
    """
    Fixture to create an admin user and return their auth headers.
    """
    # Create an admin user directly in the database for testing purposes
    admin_user = User(username='adminuser', email='admin@example.com', role='admin')
    admin_user.set_password('adminpassword')
    db.session.add(admin_user)
    db.session.commit()

    # Log in to get a token
    login_res = client.post('/api/login',
                            data=json.dumps(dict(
                                username='adminuser',
                                password='adminpassword'
                            )),
                            content_type='application/json')

    token = login_res.get_json()['token']
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture(scope='function')
def farmer_auth_data(client, user_auth_headers):
    """
    Fixture to create a user with a farmer profile and return their auth data.
    This reuses the user_auth_headers fixture to create the initial user.
    Returns a dict with {'headers': ..., 'farmer_id': ...}
    """
    # Create a farmer profile for the user created by user_auth_headers
    farmer_res = client.post('/api/farmers',
                             headers=user_auth_headers,
                             data=json.dumps(dict(
                                 name="Test Farmer",
                                 farm_name="Test Farm",
                                 location="Test Location",
                                 phone="555-0100",
                                 bio="Test farmer bio"
                             )),
                             content_type='application/json')

    farmer_data = farmer_res.get_json()['farmer']

    return {
        'headers': user_auth_headers,
        'farmer_id': farmer_data['id']
    }

@pytest.fixture(scope='function')
def second_farmer_auth_data(client, init_database):
    """
    Fixture to create a second, distinct user with a farmer profile.
    This is useful for testing ownership and authorization rules.
    """
    # Register a new user
    user_data = {
        'username': 'farmer_two',
        'email': 'farmer_two@example.com',
        'password': 'password123'
    }
    client.post('/api/register', data=json.dumps(user_data), content_type='application/json')

    # Log in to get a token
    login_res = client.post('/api/login',
                            data=json.dumps({k: v for k, v in user_data.items() if k != 'email'}),
                            content_type='application/json')

    headers = {'Authorization': f'Bearer {login_res.get_json()["token"]}'}

    # Create a farmer profile for this second user
    farmer_res = client.post('/api/farmers',
                             headers=headers,
                             data=json.dumps(dict(
                                 name="Second Farmer",
                                 farm_name="Second Test Farm",
                                 location="Second Location",
                                 phone="555-0200",
                                 bio="Second test farmer bio"
                             )),
                             content_type='application/json')
    farmer_data = farmer_res.get_json()['farmer']

    return {'headers': headers, 'farmer_id': farmer_data['id']}