import pytest
from app import app as flask_app
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
    flask_app.config.from_object('config.TestingConfig')

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
                                 farm_name="Test Farm",
                                 location="Test Location"
                             )),
                             content_type='application/json')

    farmer_data = farmer_res.get_json()['farmer']

    return {
        'headers': user_auth_headers,
        'farmer_id': farmer_data['id']
    }