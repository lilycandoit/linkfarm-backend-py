from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from models.inquiry import Inquiry
from models.farmer import Farmer
from models.user import User

# Create a Blueprint for inquiry routes
inquiry_bp = Blueprint('inquiry', __name__)

@inquiry_bp.route('', methods=['POST'])
def create_inquiry():
    """
    Creates a new customer inquiry. This is a public endpoint.
    """
    data = request.get_json()
    required_fields = ['farmer_id', 'customer_name', 'customer_email', 'message']
    if not data or not all(key in data for key in required_fields):
        return jsonify({'error': 'Bad Request', 'message': 'Missing required fields.'}), 400

    # Verify that the farmer exists before creating an inquiry for them
    if not db.session.get(Farmer, data['farmer_id']):
        return jsonify({'error': 'Not Found', 'message': 'Farmer not found.'}), 404

    try:
        new_inquiry = Inquiry(
            farmer_id=data['farmer_id'],
            product_id=data.get('product_id'), # Optional
            customer_name=data['customer_name'],
            customer_email=data['customer_email'],
            customer_phone=data.get('customer_phone'),
            message=data['message']
        )
        db.session.add(new_inquiry)
        db.session.commit()

        return jsonify({'message': 'Inquiry submitted successfully!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

@inquiry_bp.route('/farmers/<string:farmer_id>/inquiries', methods=['GET'])
@jwt_required()
def list_inquiries_for_farmer(farmer_id):
    """
    Retrieves all inquiries for a specific farmer.
    Only the farmer who owns the profile or an admin can access this.

    Protected route - requires JWT token with 'farmer' or 'admin' role.
    """
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({'error': 'Unauthorized', 'message': 'User not found.'}), 401

    # Check role - must be farmer or admin
    jwt_claims = get_jwt()
    user_role = jwt_claims.get('role', 'user')

    if user_role not in ['farmer', 'admin']:
        return jsonify({'error': 'Forbidden', 'message': 'This endpoint requires farmer or admin role.'}), 403

    # Get the farmer
    farmer = db.session.get(Farmer, farmer_id)
    if not farmer:
        return jsonify({'error': 'Not Found', 'message': 'Farmer not found.'}), 404

    # --- Crucial Ownership Check ---
    # The user must be an admin OR they must be the farmer whose inquiries are being requested
    is_admin = user_role == 'admin'
    is_owner = user.farmer_profile and user.farmer_profile.id == farmer_id

    if not is_admin and not is_owner:
        return jsonify({'error': 'Forbidden', 'message': 'You are not authorized to view these inquiries.'}), 403

    inquiries = farmer.inquiries
    # Use to_dict() method for consistent serialization
    inquiries_list = [inquiry.to_dict(include_product=True) for inquiry in inquiries]

    return jsonify(inquiries_list), 200

@inquiry_bp.route('/<string:inquiry_id>', methods=['PUT'])
@jwt_required()
def update_inquiry_status(inquiry_id):
    """
    Updates the status of an inquiry (e.g., from 'new' to 'read').
    Only the farmer who received the inquiry or an admin can do this.

    Protected route - requires JWT token with 'farmer' or 'admin' role.
    """
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({'error': 'Unauthorized', 'message': 'User not found.'}), 401

    # Check role - must be farmer or admin
    jwt_claims = get_jwt()
    user_role = jwt_claims.get('role', 'user')

    if user_role not in ['farmer', 'admin']:
        return jsonify({'error': 'Forbidden', 'message': 'This endpoint requires farmer or admin role.'}), 403

    inquiry = db.session.get(Inquiry, inquiry_id)
    if not inquiry:
        return jsonify({'error': 'Not Found', 'message': 'Inquiry not found.'}), 404

    # --- Ownership Check ---
    is_admin = user_role == 'admin'
    is_owner = user.farmer_profile and user.farmer_profile.id == inquiry.farmer_id

    if not is_admin and not is_owner:
        return jsonify({'error': 'Forbidden', 'message': 'You are not authorized to update this inquiry.'}), 403

    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({'error': 'Bad Request', 'message': 'Missing "status" field.'}), 400

    inquiry.status = data['status']
    db.session.commit()

    return jsonify({'message': 'Inquiry status updated successfully.'}), 200

@inquiry_bp.route('/<string:inquiry_id>', methods=['DELETE'])
@jwt_required()
def delete_inquiry(inquiry_id):
    """
    Deletes an inquiry.
    Only the farmer who received the inquiry or an admin can do this.

    Protected route - requires JWT token with 'farmer' or 'admin' role.
    """
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({'error': 'Unauthorized', 'message': 'User not found.'}), 401

    # Check role - must be farmer or admin
    jwt_claims = get_jwt()
    user_role = jwt_claims.get('role', 'user')

    if user_role not in ['farmer', 'admin']:
        return jsonify({'error': 'Forbidden', 'message': 'This endpoint requires farmer or admin role.'}), 403

    inquiry = db.session.get(Inquiry, inquiry_id)
    if not inquiry:
        return jsonify({'error': 'Not Found', 'message': 'Inquiry not found.'}), 404

    # --- Ownership Check ---
    is_admin = user_role == 'admin'
    is_owner = user.farmer_profile and user.farmer_profile.id == inquiry.farmer_id

    if not is_admin and not is_owner:
        return jsonify({'error': 'Forbidden', 'message': 'You are not authorized to delete this inquiry.'}), 403

    db.session.delete(inquiry)
    db.session.commit()

    return jsonify({'message': 'Inquiry deleted successfully.'}), 200