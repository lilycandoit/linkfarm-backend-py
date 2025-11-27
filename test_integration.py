#!/usr/bin/env python3
"""
Full Stack Integration Test for LinkFarm
Tests the complete API flow: auth, farmers, products, and inquiries
"""

from datetime import datetime
import requests

# Configuration
BASE_URL = "http://localhost:5000/api"
FRONTEND_URL = "http://localhost:5173"

# Test colors
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_test(name):
    print(f"\n{BLUE}🧪 Testing: {name}{RESET}")

def print_success(message):
    print(f"{GREEN}✓ {message}{RESET}")

def print_error(message):
    print(f"{RED}✗ {message}{RESET}")

def print_info(message):
    print(f"{YELLOW}ℹ {message}{RESET}")

# Test data
test_user = {
    "username": f"testuser_{datetime.now().strftime('%H%M%S')}",
    "email": f"test_{datetime.now().strftime('%H%M%S')}@example.com",
    "password": "TestPassword123",
    "role": "farmer"
}

def test_api_health():
    """Test API is responding"""
    print_test("API Health Check")
    try:
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        print_success(f"API is healthy - {data['message']}")
        print_info(f"Version: {data['version']}, Environment: {data['environment']}")
        return True
    except Exception as e:
        print_error(f"API health check failed: {e}")
        return False

def test_user_registration():
    """Test user registration"""
    print_test("User Registration")
    try:
        response = requests.post(
            f"{BASE_URL}/register",
            json=test_user
        )
        assert response.status_code == 201
        data = response.json()
        print_success(f"User registered: {data['user']['username']} (ID: {data['user']['id'][:8]}...)")
        return data['user']['id']
    except Exception as e:
        print_error(f"Registration failed: {e}")
        if hasattr(e, 'response'):
            print_error(f"Response: {e.response.text}")
        return None

def test_user_login():
    """Test user login"""
    print_test("User Login")
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json={
                "username": test_user["username"],
                "password": test_user["password"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        token = data['token']
        print_success(f"Login successful - Token received (length: {len(token)})")
        print_info(f"Message: {data['message']}")
        return token
    except Exception as e:
        print_error(f"Login failed: {e}")
        return None

def test_create_farmer_profile(token, user_id):
    """Test creating a farmer profile"""
    print_test("Create Farmer Profile")
    # Note: user_id is NOT sent in the request body
    # It's extracted from the JWT token by the backend for security
    farmer_data = {
        "name": "Integration Test Farmer",
        "farm_name": "Test Farm",
        "location": "Test Location, CA",
        "phone": "555-1234",
        "bio": "This is a test farmer profile for integration testing"
    }
    try:
        response = requests.post(
            f"{BASE_URL}/farmers",
            json=farmer_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        print_info(f"Response status: {response.status_code}")
        print_info(f"Response body: {response.text[:200]}")

        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        data = response.json()
        print_success(f"Farmer profile created: {data['farm_name']} (ID: {data['id'][:8]}...)")
        return data['id']
    except AssertionError as e:
        print_error(f"Assertion failed: {e}")
        print_error(f"Full response: {response.text}")
        return None
    except Exception as e:
        print_error(f"Farmer profile creation failed: {type(e).__name__}: {e}")
        if 'response' in locals():
            print_error(f"Status code: {response.status_code}")
            print_error(f"Response: {response.text}")
        return None

def test_list_products():
    """Test listing products"""
    print_test("List Products (Public)")
    try:
        response = requests.get(f"{BASE_URL}/products")
        assert response.status_code == 200
        data = response.json()
        print_success(f"Products retrieved: {data['total']} total, showing page {data['current_page']} of {data['pages']}")
        if data['products']:
            print_info(f"Sample product: {data['products'][0]['name']} - ${data['products'][0]['price']}")
        return True
    except Exception as e:
        print_error(f"List products failed: {e}")
        return False

def test_create_product(token, farmer_id):
    """Test creating a product"""
    print_test("Create Product")
    # Note: farmer_id is NOT sent in the request body
    # It's automatically set from the user's farmer profile for security
    product_data = {
        "name": "Test Organic Tomatoes",
        "description": "Fresh organic tomatoes for integration testing",
        "price": "4.99",
        "unit": "lb",
        "category": "Vegetables",
        "is_available": True
    }
    try:
        response = requests.post(
            f"{BASE_URL}/products",
            json=product_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        print_info(f"Response status: {response.status_code}")
        print_info(f"Response body: {response.text[:300]}")

        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        data = response.json()
        print_success(f"Product created: {data['name']} - ${data['price']}/{data['unit']}")
        return data['id']
    except AssertionError as e:
        print_error(f"Assertion failed: {e}")
        print_error(f"Full response: {response.text}")
        return None
    except Exception as e:
        print_error(f"Product creation failed: {type(e).__name__}: {e}")
        if 'response' in locals():
            print_error(f"Status: {response.status_code}, Body: {response.text}")
        return None

def test_get_product(product_id):
    """Test getting a specific product"""
    print_test("Get Product Details")
    try:
        response = requests.get(f"{BASE_URL}/products/{product_id}")
        assert response.status_code == 200
        data = response.json()
        print_success(f"Product retrieved: {data['name']} from {data['farmer']['farm_name']}")
        return True
    except Exception as e:
        print_error(f"Get product failed: {e}")
        return False

def test_update_product(token, product_id):
    """Test updating a product"""
    print_test("Update Product")
    try:
        update_data = {
            "price": "5.99",
            "description": "Updated: Fresh organic tomatoes at new price!"
        }
        response = requests.put(
            f"{BASE_URL}/products/{product_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        print_success(f"Product updated: new price ${data['price']}")
        return True
    except Exception as e:
        print_error(f"Update product failed: {e}")
        return False

def test_list_farmers():
    """Test listing farmers"""
    print_test("List Farmers")
    try:
        response = requests.get(f"{BASE_URL}/farmers")
        assert response.status_code == 200
        data = response.json()
        print_success(f"Farmers retrieved: {len(data['farmers'])} farmers")
        if data['farmers']:
            print_info(f"Sample farmer: {data['farmers'][0]['farm_name']} - {data['farmers'][0]['location']}")
        return True
    except Exception as e:
        print_error(f"List farmers failed: {e}")
        return False

def test_create_inquiry(token, product_id, farmer_id):
    """Test creating an inquiry"""
    print_test("Create Inquiry")
    inquiry_data = {
        "farmer_id": farmer_id,
        "product_id": product_id,
        "customer_name": "Test Customer",
        "customer_email": "customer@test.com",
        "customer_phone": "555-9999",
        "message": "I'm interested in your tomatoes. What's the minimum order?"
    }
    try:
        response = requests.post(
            f"{BASE_URL}/inquiries",
            json=inquiry_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        print_info(f"Response status: {response.status_code}")
        print_info(f"Response body: {response.text[:300]}")

        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        data = response.json()
        print_success(f"Inquiry created: {data['message']}")
        return True  # Inquiry endpoint only returns a message, not the inquiry object
    except AssertionError as e:
        print_error(f"Assertion failed: {e}")
        print_error(f"Full response: {response.text}")
        return None
    except Exception as e:
        print_error(f"Create inquiry failed: {type(e).__name__}: {e}")
        if 'response' in locals():
            print_error(f"Status: {response.status_code}, Body: {response.text}")
        return None

def test_frontend_accessible():
    """Test if frontend is accessible"""
    print_test("Frontend Accessibility")
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        assert response.status_code == 200
        print_success(f"Frontend is accessible at {FRONTEND_URL}")
        return True
    except Exception as e:
        print_error(f"Frontend not accessible: {e}")
        return False

def main():
    """Run all integration tests"""
    print(f"\n{'='*60}")
    print(f"{BLUE}🚀 LinkFarm Full Stack Integration Test{RESET}")
    print(f"{'='*60}")

    results = {
        'passed': 0,
        'failed': 0,
        'total': 0
    }

    # Test 1: API Health
    results['total'] += 1
    if test_api_health():
        results['passed'] += 1
    else:
        results['failed'] += 1
        print_error("Cannot continue without healthy API")
        return

    # Test 2: User Registration
    results['total'] += 1
    user_id = test_user_registration()
    if user_id:
        results['passed'] += 1
    else:
        results['failed'] += 1
        print_error("Cannot continue without user registration")
        return

    # Test 3: User Login
    results['total'] += 1
    token = test_user_login()
    if token:
        results['passed'] += 1
    else:
        results['failed'] += 1
        print_error("Cannot continue without authentication")
        return

    # Test 4: Create Farmer Profile
    results['total'] += 1
    farmer_id = test_create_farmer_profile(token, user_id)
    if farmer_id:
        results['passed'] += 1
    else:
        results['failed'] += 1

    # Test 5: List Farmers
    results['total'] += 1
    if test_list_farmers():
        results['passed'] += 1
    else:
        results['failed'] += 1

    # Test 6: List Products
    results['total'] += 1
    if test_list_products():
        results['passed'] += 1
    else:
        results['failed'] += 1

    # Test 7: Create Product (only if we have farmer_id)
    product_id = None
    if farmer_id:
        results['total'] += 1
        product_id = test_create_product(token, farmer_id)
        if product_id:
            results['passed'] += 1
        else:
            results['failed'] += 1

    # Test 8: Get Product Details
    if product_id:
        results['total'] += 1
        if test_get_product(product_id):
            results['passed'] += 1
        else:
            results['failed'] += 1

    # Test 9: Update Product
    if product_id:
        results['total'] += 1
        if test_update_product(token, product_id):
            results['passed'] += 1
        else:
            results['failed'] += 1

    # Test 10: Create Inquiry
    if product_id and farmer_id:
        results['total'] += 1
        inquiry_id = test_create_inquiry(token, product_id, farmer_id)
        if inquiry_id:
            results['passed'] += 1
        else:
            results['failed'] += 1

    # Test 11: Frontend Accessibility
    results['total'] += 1
    if test_frontend_accessible():
        results['passed'] += 1
    else:
        results['failed'] += 1

    # Summary
    print(f"\n{'='*60}")
    print(f"{BLUE}📊 Test Results{RESET}")
    print(f"{'='*60}")
    print(f"Total Tests: {results['total']}")
    print(f"{GREEN}Passed: {results['passed']}{RESET}")
    print(f"{RED}Failed: {results['failed']}{RESET}")

    if results['failed'] == 0:
        print(f"\n{GREEN}🎉 All tests passed! Full stack integration is working!{RESET}")
    else:
        print(f"\n{YELLOW}⚠️  Some tests failed. Check the output above for details.{RESET}")

    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
