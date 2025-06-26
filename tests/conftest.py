import pytest
from app import app as flask_app
from extensions import db
import json
from models.user import User

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
def auth_headers(client, init_database):
    """
    Fixture to register and log in a user, returning auth headers.
    This makes testing protected endpoints much cleaner.
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