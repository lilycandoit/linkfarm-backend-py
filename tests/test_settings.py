import json
from models.user import User
from extensions import db


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Integration Tests: /api/settings Endpoint
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_update_email_success(client, user_auth_headers, init_database):
    """
    GIVEN an authenticated user
    WHEN the '/api/settings' endpoint is updated with a new email
    THEN check that the email is updated successfully
    """
    response = client.put('/api/settings',
                         headers=user_auth_headers,
                         data=json.dumps(dict(
                             current_password='password123',
                             email='newemail@example.com'
                         )),
                         content_type='application/json')

    assert response.status_code == 200
    data = response.get_json()
    assert 'successfully' in data['message'].lower()

    # Verify email was updated in database
    user = db.session.execute(
        db.select(User).where(User.username == 'testuser')
    ).scalar_one()
    assert user.email == 'newemail@example.com'


def test_update_password_success(client, user_auth_headers, init_database):
    """
    GIVEN an authenticated user
    WHEN the '/api/settings' endpoint is updated with a new password
    THEN check that the password is updated successfully
    """
    response = client.put('/api/settings',
                         headers=user_auth_headers,
                         data=json.dumps(dict(
                             current_password='password123',
                             new_password='newpassword456'
                         )),
                         content_type='application/json')

    assert response.status_code == 200

    # Verify password was updated by trying to login with new password
    login_response = client.post('/api/login',
                                data=json.dumps(dict(
                                    username='testuser',
                                    password='newpassword456'
                                )),
                                content_type='application/json')
    assert login_response.status_code == 200

    # Verify old password no longer works
    old_login = client.post('/api/login',
                           data=json.dumps(dict(
                               username='testuser',
                               password='password123'
                           )),
                           content_type='application/json')
    assert old_login.status_code == 401


def test_update_both_email_and_password(client, user_auth_headers, init_database):
    """
    GIVEN an authenticated user
    WHEN the '/api/settings' endpoint is updated with both email and password
    THEN check that both are updated successfully
    """
    response = client.put('/api/settings',
                         headers=user_auth_headers,
                         data=json.dumps(dict(
                             current_password='password123',
                             email='updated@example.com',
                             new_password='updatedpassword789'
                         )),
                         content_type='application/json')

    assert response.status_code == 200

    # Verify both were updated
    user = db.session.execute(
        db.select(User).where(User.username == 'testuser')
    ).scalar_one()
    assert user.email == 'updated@example.com'
    assert user.check_password('updatedpassword789')


def test_update_settings_wrong_current_password(client, user_auth_headers, init_database):
    """
    GIVEN an authenticated user
    WHEN the '/api/settings' endpoint is posted with an incorrect current password
    THEN check that a 401 error is returned
    """
    response = client.put('/api/settings',
                         headers=user_auth_headers,
                         data=json.dumps(dict(
                             current_password='wrongpassword',
                             email='hacker@example.com'
                         )),
                         content_type='application/json')

    assert response.status_code == 401
    data = response.get_json()
    assert 'incorrect current password' in data['message'].lower()

    # Verify email was NOT changed
    user = db.session.execute(
        db.select(User).where(User.username == 'testuser')
    ).scalar_one()
    assert user.email == 'test@example.com'


def test_update_settings_missing_current_password(client, user_auth_headers, init_database):
    """
    GIVEN an authenticated user
    WHEN the '/api/settings' endpoint is posted without current password
    THEN check that a 400 error is returned
    """
    response = client.put('/api/settings',
                         headers=user_auth_headers,
                         data=json.dumps(dict(
                             email='newemail@example.com'
                         )),
                         content_type='application/json')

    assert response.status_code == 400
    data = response.get_json()
    assert 'current password is required' in data['message'].lower()


def test_update_email_already_in_use(client, user_auth_headers, init_database):
    """
    GIVEN two users in the database
    WHEN one user tries to change their email to another user's email
    THEN check that a 409 conflict error is returned
    """
    # Create a second user
    user2 = User(username='otheruser', email='other@example.com')
    user2.set_password('password456')
    db.session.add(user2)
    db.session.commit()

    # Try to update first user's email to second user's email
    response = client.put('/api/settings',
                         headers=user_auth_headers,
                         data=json.dumps(dict(
                             current_password='password123',
                             email='other@example.com'
                         )),
                         content_type='application/json')

    assert response.status_code == 409
    data = response.get_json()
    assert 'already in use' in data['message'].lower()


def test_update_password_too_short(client, user_auth_headers, init_database):
    """
    GIVEN an authenticated user
    WHEN the '/api/settings' endpoint is posted with a password less than 8 characters
    THEN check that a 400 error is returned
    """
    response = client.put('/api/settings',
                         headers=user_auth_headers,
                         data=json.dumps(dict(
                             current_password='password123',
                             new_password='short'
                         )),
                         content_type='application/json')

    assert response.status_code == 400
    data = response.get_json()
    assert 'too short' in data['message'].lower()


def test_update_settings_no_data(client, user_auth_headers, init_database):
    """
    GIVEN an authenticated user
    WHEN the '/api/settings' endpoint is posted with no data
    THEN check that a 400 error is returned
    """
    response = client.put('/api/settings',
                         headers=user_auth_headers,
                         data=json.dumps(None),
                         content_type='application/json')

    assert response.status_code == 400


def test_update_settings_unauthenticated(client, init_database):
    """
    GIVEN an unauthenticated request
    WHEN the '/api/settings' endpoint is accessed
    THEN check that a 401 error is returned
    """
    response = client.put('/api/settings',
                         data=json.dumps(dict(
                             current_password='password123',
                             email='hacker@example.com'
                         )),
                         content_type='application/json')

    assert response.status_code == 401


def test_update_email_to_same_value(client, user_auth_headers, init_database):
    """
    GIVEN an authenticated user
    WHEN the '/api/settings' endpoint is updated with the same email
    THEN check that the request succeeds (no-op)
    """
    response = client.put('/api/settings',
                         headers=user_auth_headers,
                         data=json.dumps(dict(
                             current_password='password123',
                             email='test@example.com'  # Same as current
                         )),
                         content_type='application/json')

    assert response.status_code == 200
