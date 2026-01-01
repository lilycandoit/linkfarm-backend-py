import json
from unittest.mock import patch


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Basic Inquiry Tests - Core Functionality Only
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@patch('routes.inquiry.send_inquiry_notification')
def test_create_inquiry_success(mock_send_email, client, farmer_auth_data):
    """
    GIVEN a farmer exists
    WHEN a customer creates an inquiry
    THEN check that the inquiry is created successfully
    """
    mock_send_email.return_value = True
    farmer_id = farmer_auth_data['farmer_id']

    response = client.post('/api/inquiries',
                          data=json.dumps(dict(
                              farmer_id=farmer_id,
                              customer_name='John Customer',
                              customer_email='customer@example.com',
                              customer_phone='+1-555-0100',
                              message='I am interested in your organic tomatoes.'
                          )),
                          content_type='application/json')

    assert response.status_code == 201
    data = response.get_json()
    assert 'successfully' in data['message'].lower()

    # Verify email was sent to farmer
    mock_send_email.assert_called_once()


def test_create_inquiry_missing_fields(client, farmer_auth_data):
    """
    GIVEN a customer tries to create an inquiry
    WHEN required fields are missing
    THEN check that a 400 error is returned
    """
    response = client.post('/api/inquiries',
                          data=json.dumps(dict(
                              farmer_id=farmer_auth_data['farmer_id'],
                              customer_name='John Customer'
                              # Missing email, phone, message
                          )),
                          content_type='application/json')

    assert response.status_code == 400
    assert 'missing required fields' in response.get_json()['message'].lower()


def test_create_inquiry_nonexistent_farmer(client, init_database):
    """
    GIVEN an invalid farmer_id
    WHEN a customer creates an inquiry
    THEN check that a 404 error is returned
    """
    response = client.post('/api/inquiries',
                          data=json.dumps(dict(
                              farmer_id='nonexistent-farmer-id',
                              customer_name='John Customer',
                              customer_email='customer@example.com',
                              customer_phone='+1-555-0100',
                              message='Test message'
                          )),
                          content_type='application/json')

    assert response.status_code == 404
    assert 'farmer not found' in response.get_json()['message'].lower()


def test_create_inquiry_invalid_phone(client, farmer_auth_data):
    """
    GIVEN an invalid phone number format
    WHEN a customer creates an inquiry
    THEN check that a 400 error is returned
    """
    response = client.post('/api/inquiries',
                          data=json.dumps(dict(
                              farmer_id=farmer_auth_data['farmer_id'],
                              customer_name='John Customer',
                              customer_email='customer@example.com',
                              customer_phone='abc-def-ghij',  # Invalid format
                              message='Test message'
                          )),
                          content_type='application/json')

    assert response.status_code == 400
    assert 'invalid phone number' in response.get_json()['message'].lower()


@patch('routes.inquiry.send_inquiry_notification')
def test_list_inquiries_as_owner(mock_send_email, client, farmer_auth_data):
    """
    GIVEN a farmer with inquiries
    WHEN they request their inquiry list
    THEN check that their inquiries are returned
    """
    mock_send_email.return_value = True
    farmer_id = farmer_auth_data['farmer_id']
    headers = farmer_auth_data['headers']

    # Create an inquiry first
    client.post('/api/inquiries',
               data=json.dumps(dict(
                   farmer_id=farmer_id,
                   customer_name='John Customer',
                   customer_email='customer@example.com',
                   customer_phone='+1-555-0100',
                   message='Test inquiry'
               )),
               content_type='application/json')

    # List inquiries as the farmer
    response = client.get(f'/api/inquiries/farmers/{farmer_id}/inquiries',
                         headers=headers)

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]['customer_name'] == 'John Customer'


def test_list_inquiries_as_non_owner(client, farmer_auth_data, second_farmer_auth_data):
    """
    GIVEN two farmers
    WHEN farmer A tries to view farmer B's inquiries
    THEN check that a 403 forbidden error is returned
    """
    farmer_a_id = farmer_auth_data['farmer_id']
    farmer_b_headers = second_farmer_auth_data['headers']

    # Farmer B tries to access Farmer A's inquiries
    response = client.get(f'/api/inquiries/farmers/{farmer_a_id}/inquiries',
                         headers=farmer_b_headers)

    assert response.status_code == 403
    assert 'not authorized' in response.get_json()['message'].lower()


def test_list_inquiries_unauthenticated(client, farmer_auth_data):
    """
    GIVEN an unauthenticated request
    WHEN trying to list inquiries
    THEN check that a 401 error is returned
    """
    farmer_id = farmer_auth_data['farmer_id']

    response = client.get(f'/api/inquiries/farmers/{farmer_id}/inquiries')

    assert response.status_code == 401


@patch('routes.inquiry.send_inquiry_notification')
def test_update_inquiry_status(mock_send_email, client, farmer_auth_data):
    """
    GIVEN a farmer with an inquiry
    WHEN they update the inquiry status
    THEN check that the status is updated successfully
    """
    mock_send_email.return_value = True
    farmer_id = farmer_auth_data['farmer_id']
    headers = farmer_auth_data['headers']

    # Create an inquiry
    create_res = client.post('/api/inquiries',
                            data=json.dumps(dict(
                                farmer_id=farmer_id,
                                customer_name='John Customer',
                                customer_email='customer@example.com',
                                customer_phone='+1-555-0100',
                                message='Test inquiry'
                            )),
                            content_type='application/json')

    # Get the inquiry ID (we need to list inquiries to get the ID)
    list_res = client.get(f'/api/inquiries/farmers/{farmer_id}/inquiries',
                         headers=headers)
    inquiry_id = list_res.get_json()[0]['id']

    # Update status
    response = client.put(f'/api/inquiries/{inquiry_id}',
                         headers=headers,
                         data=json.dumps(dict(status='read')),
                         content_type='application/json')

    assert response.status_code == 200
    assert 'successfully' in response.get_json()['message'].lower()


@patch('routes.inquiry.send_inquiry_notification')
def test_delete_inquiry_as_owner(mock_send_email, client, farmer_auth_data):
    """
    GIVEN a farmer with an inquiry
    WHEN they delete the inquiry
    THEN check that the inquiry is deleted successfully
    """
    mock_send_email.return_value = True
    farmer_id = farmer_auth_data['farmer_id']
    headers = farmer_auth_data['headers']

    # Create an inquiry
    client.post('/api/inquiries',
               data=json.dumps(dict(
                   farmer_id=farmer_id,
                   customer_name='John Customer',
                   customer_email='customer@example.com',
                   customer_phone='+1-555-0100',
                   message='Test inquiry to delete'
               )),
               content_type='application/json')

    # Get the inquiry ID
    list_res = client.get(f'/api/inquiries/farmers/{farmer_id}/inquiries',
                         headers=headers)
    inquiry_id = list_res.get_json()[0]['id']

    # Delete the inquiry
    response = client.delete(f'/api/inquiries/{inquiry_id}',
                            headers=headers)

    assert response.status_code == 200
    assert 'successfully' in response.get_json()['message'].lower()

    # Verify it's actually deleted
    list_res_after = client.get(f'/api/inquiries/farmers/{farmer_id}/inquiries',
                                headers=headers)
    assert len(list_res_after.get_json()) == 0
