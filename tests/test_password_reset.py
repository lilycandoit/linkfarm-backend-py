import json
import pytest
from datetime import datetime, timedelta
from models.user import User
from extensions import db
from unittest.mock import patch


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Unit Tests: User Model Password Reset Methods
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_generate_reset_token_creates_valid_token(client, init_database):
    """
    GIVEN a user in the database
    WHEN generate_reset_token() is called
    THEN check that a secure token is created with 15-minute expiry
    """
    # Create a user
    user = User(username='resetuser', email='reset@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    # Generate reset token
    token = user.generate_reset_token()

    assert token is not None
    assert len(token) > 20  # Secure tokens should be long
    assert user.reset_token == token
    assert user.reset_token_expiry is not None

    # Check expiry is ~15 minutes in the future
    time_diff = user.reset_token_expiry - datetime.utcnow()
    assert 890 <= time_diff.total_seconds() <= 910  # Allow 10s variance


def test_verify_reset_token_success(client, init_database):
    """
    GIVEN a user with a valid reset token
    WHEN verify_reset_token() is called with the correct token
    THEN check that it returns True
    """
    user = User(username='resetuser', email='reset@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    token = user.generate_reset_token()
    db.session.commit()

    assert user.verify_reset_token(token) is True


def test_verify_reset_token_expired(client, init_database):
    """
    GIVEN a user with an expired reset token
    WHEN verify_reset_token() is called
    THEN check that it returns False
    """
    user = User(username='resetuser', email='reset@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    # Generate token and manually set expiry to the past
    token = user.generate_reset_token()
    user.reset_token_expiry = datetime.utcnow() - timedelta(minutes=1)
    db.session.commit()

    assert user.verify_reset_token(token) is False


def test_verify_reset_token_invalid(client, init_database):
    """
    GIVEN a user with a reset token
    WHEN verify_reset_token() is called with a wrong token
    THEN check that it returns False
    """
    user = User(username='resetuser', email='reset@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    user.generate_reset_token()
    db.session.commit()

    assert user.verify_reset_token('wrong_token_here') is False


def test_verify_reset_token_no_token_set(client, init_database):
    """
    GIVEN a user without a reset token
    WHEN verify_reset_token() is called
    THEN check that it returns False
    """
    user = User(username='resetuser', email='reset@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    assert user.verify_reset_token('any_token') is False


def test_clear_reset_token(client, init_database):
    """
    GIVEN a user with a reset token
    WHEN clear_reset_token() is called
    THEN check that the token and expiry are cleared
    """
    user = User(username='resetuser', email='reset@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    user.generate_reset_token()
    db.session.commit()

    # Verify token exists
    assert user.reset_token is not None
    assert user.reset_token_expiry is not None

    # Clear token
    user.clear_reset_token()
    db.session.commit()

    # Verify token is cleared
    assert user.reset_token is None
    assert user.reset_token_expiry is None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Integration Tests: /api/forgot-password Endpoint
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@patch('services.email_service.send_password_reset_email')
def test_forgot_password_success(mock_send_email, client, init_database):
    """
    GIVEN a registered user
    WHEN the '/api/forgot-password' endpoint is posted to with their email
    THEN check that a reset token is generated, email is sent, and 200 is returned
    """
    # Register a user
    client.post('/api/register',
                data=json.dumps(dict(
                    username='testuser',
                    email='test@example.com',
                    password='password123'
                )),
                content_type='application/json')

    mock_send_email.return_value = True

    response = client.post('/api/forgot-password',
                          data=json.dumps(dict(email='test@example.com')),
                          content_type='application/json')

    assert response.status_code == 200
    data = response.get_json()
    assert 'password reset link has been sent' in data['message'].lower()

    # Verify email was sent
    mock_send_email.assert_called_once()

    # Verify token was generated in database
    user = db.session.execute(
        db.select(User).where(User.email == 'test@example.com')
    ).scalar_one()
    assert user.reset_token is not None
    assert user.reset_token_expiry is not None


@patch('services.email_service.send_password_reset_email')
def test_forgot_password_nonexistent_email(mock_send_email, client, init_database):
    """
    GIVEN a non-existent email address
    WHEN the '/api/forgot-password' endpoint is posted to
    THEN check that a 200 is returned (to prevent email enumeration)
    """
    mock_send_email.return_value = True

    response = client.post('/api/forgot-password',
                          data=json.dumps(dict(email='nonexistent@example.com')),
                          content_type='application/json')

    # IMPORTANT: Should return 200 to prevent email enumeration attacks
    assert response.status_code == 200
    data = response.get_json()
    assert 'password reset link has been sent' in data['message'].lower()

    # Verify email was NOT sent
    mock_send_email.assert_not_called()


def test_forgot_password_missing_email(client, init_database):
    """
    GIVEN a request without an email
    WHEN the '/api/forgot-password' endpoint is posted to
    THEN check that a 400 error is returned
    """
    response = client.post('/api/forgot-password',
                          data=json.dumps(dict()),
                          content_type='application/json')

    assert response.status_code == 400
    data = response.get_json()
    assert 'email is required' in data['message'].lower()


def test_forgot_password_empty_payload(client, init_database):
    """
    GIVEN an empty request payload
    WHEN the '/api/forgot-password' endpoint is posted to
    THEN check that a 400 error is returned
    """
    response = client.post('/api/forgot-password',
                          data=json.dumps(None),
                          content_type='application/json')

    assert response.status_code == 400


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Integration Tests: /api/reset-password Endpoint
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_reset_password_success(client, init_database):
    """
    GIVEN a user with a valid reset token
    WHEN the '/api/reset-password' endpoint is posted to with token and new password
    THEN check that password is updated, token is cleared, and JWT is returned
    """
    # Create user and generate token
    user = User(username='resetuser', email='reset@example.com')
    user.set_password('oldpassword123')
    db.session.add(user)
    db.session.commit()

    token = user.generate_reset_token()
    db.session.commit()

    # Reset password
    response = client.post('/api/reset-password',
                          data=json.dumps(dict(
                              token=token,
                              new_password='newpassword123'
                          )),
                          content_type='application/json')

    assert response.status_code == 200
    data = response.get_json()
    assert 'password reset successful' in data['message'].lower()
    assert 'token' in data  # Auto-login JWT

    # Verify password was changed
    user = db.session.get(User, user.id)
    assert user.check_password('newpassword123')
    assert not user.check_password('oldpassword123')

    # Verify reset token was cleared
    assert user.reset_token is None
    assert user.reset_token_expiry is None


def test_reset_password_expired_token(client, init_database):
    """
    GIVEN a user with an expired reset token
    WHEN the '/api/reset-password' endpoint is posted to
    THEN check that a 400 error is returned
    """
    user = User(username='resetuser', email='reset@example.com')
    user.set_password('oldpassword123')
    db.session.add(user)
    db.session.commit()

    # Generate token and set expiry to past
    token = user.generate_reset_token()
    user.reset_token_expiry = datetime.utcnow() - timedelta(minutes=1)
    db.session.commit()

    response = client.post('/api/reset-password',
                          data=json.dumps(dict(
                              token=token,
                              new_password='newpassword123'
                          )),
                          content_type='application/json')

    assert response.status_code == 400
    data = response.get_json()
    assert 'invalid or expired' in data['message'].lower()

    # Verify password was NOT changed
    user = db.session.get(User, user.id)
    assert user.check_password('oldpassword123')


def test_reset_password_invalid_token(client, init_database):
    """
    GIVEN a user
    WHEN the '/api/reset-password' endpoint is posted to with an invalid token
    THEN check that a 400 error is returned
    """
    user = User(username='resetuser', email='reset@example.com')
    user.set_password('oldpassword123')
    db.session.add(user)
    db.session.commit()

    response = client.post('/api/reset-password',
                          data=json.dumps(dict(
                              token='invalid_token_xyz',
                              new_password='newpassword123'
                          )),
                          content_type='application/json')

    assert response.status_code == 400
    data = response.get_json()
    assert 'invalid or expired' in data['message'].lower()


def test_reset_password_too_short(client, init_database):
    """
    GIVEN a user with a valid reset token
    WHEN the '/api/reset-password' endpoint is posted to with a short password
    THEN check that a 400 error is returned
    """
    user = User(username='resetuser', email='reset@example.com')
    user.set_password('oldpassword123')
    db.session.add(user)
    db.session.commit()

    token = user.generate_reset_token()
    db.session.commit()

    response = client.post('/api/reset-password',
                          data=json.dumps(dict(
                              token=token,
                              new_password='short'  # Less than 8 characters
                          )),
                          content_type='application/json')

    assert response.status_code == 400
    data = response.get_json()
    assert '8 characters' in data['message'].lower()


def test_reset_password_missing_fields(client, init_database):
    """
    GIVEN a request missing required fields
    WHEN the '/api/reset-password' endpoint is posted to
    THEN check that a 400 error is returned
    """
    # Missing token
    response = client.post('/api/reset-password',
                          data=json.dumps(dict(new_password='newpassword123')),
                          content_type='application/json')
    assert response.status_code == 400

    # Missing password
    response = client.post('/api/reset-password',
                          data=json.dumps(dict(token='sometoken')),
                          content_type='application/json')
    assert response.status_code == 400


def test_reset_password_token_reuse_prevention(client, init_database):
    """
    GIVEN a user who has successfully reset their password
    WHEN they try to use the same token again
    THEN check that the token is rejected (one-time use)
    """
    user = User(username='resetuser', email='reset@example.com')
    user.set_password('oldpassword123')
    db.session.add(user)
    db.session.commit()

    token = user.generate_reset_token()
    db.session.commit()

    # First reset - should succeed
    response1 = client.post('/api/reset-password',
                           data=json.dumps(dict(
                               token=token,
                               new_password='newpassword123'
                           )),
                           content_type='application/json')
    assert response1.status_code == 200

    # Second reset with same token - should fail
    response2 = client.post('/api/reset-password',
                           data=json.dumps(dict(
                               token=token,
                               new_password='anotherpassword'
                           )),
                           content_type='application/json')
    assert response2.status_code == 400
    assert 'invalid or expired' in response2.get_json()['message'].lower()

    # Verify password is still 'newpassword123', not 'anotherpassword'
    user = db.session.get(User, user.id)
    assert user.check_password('newpassword123')


def test_reset_password_auto_login(client, init_database):
    """
    GIVEN a successful password reset
    WHEN the response is returned
    THEN check that a valid JWT is included for auto-login
    """
    user = User(username='resetuser', email='reset@example.com')
    user.set_password('oldpassword123')
    db.session.add(user)
    db.session.commit()

    token = user.generate_reset_token()
    db.session.commit()

    response = client.post('/api/reset-password',
                          data=json.dumps(dict(
                              token=token,
                              new_password='newpassword123'
                          )),
                          content_type='application/json')

    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data

    # Verify the JWT works by accessing a protected endpoint
    jwt = data['token']
    profile_response = client.get('/api/profile',
                                  headers={'Authorization': f'Bearer {jwt}'})
    assert profile_response.status_code == 200
    assert profile_response.get_json()['username'] == 'resetuser'
