from flask import Blueprint, request, jsonify, g
from extensions import db
from models.inquiry import Inquiry
from models.farmer import Farmer
from utils.decorators import token_required, role_required

# Create a Blueprint for inquiry routes
inquiry_bp = Blueprint('inquiry', __name__)

@inquiry_bp.route('/inquiries', methods=['POST'])
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

@inquiry_bp.route('/farmers/<int:farmer_id>/inquiries', methods=['GET'])
@token_required
@role_required(['farmer', 'admin'])
def list_inquiries_for_farmer(farmer_id):
    """
    Retrieves all inquiries for a specific farmer.
    Only the farmer who owns the profile or an admin can access this.
    """
    # --- Crucial Ownership Check ---
    # The user must be an admin OR they must be the farmer whose inquiries are being requested.
    if not g.current_user.is_admin and g.current_user.farmer.id != farmer_id:
        return jsonify({'error': 'Forbidden', 'message': 'You are not authorized to view these inquiries.'}), 403

    # The farmer object is already available via the authenticated user
    farmer = g.current_user.farmer if not g.current_user.is_admin else db.session.get(Farmer, farmer_id)
    if not farmer:
        return jsonify({'error': 'Not Found', 'message': 'Farmer not found.'}), 404

    inquiries = farmer.inquiries
    inquiries_list = [{
        'id': inquiry.id,
        'product_id': inquiry.product_id,
        'customer_name': inquiry.customer_name,
        'customer_email': inquiry.customer_email,
        'message': inquiry.message,
        'status': inquiry.status,
        'created_at': inquiry.created_at.isoformat()
    } for inquiry in inquiries]

    return jsonify(inquiries_list), 200

@inquiry_bp.route('/inquiries/<int:inquiry_id>', methods=['PUT'])
@token_required
@role_required(['farmer', 'admin'])
def update_inquiry_status(inquiry_id):
    """
    Updates the status of an inquiry (e.g., from 'new' to 'read').
    Only the farmer who received the inquiry or an admin can do this.
    """
    inquiry = db.session.get(Inquiry, inquiry_id)
    if not inquiry:
        return jsonify({'error': 'Not Found', 'message': 'Inquiry not found.'}), 404

    # --- Ownership Check ---
    if not g.current_user.is_admin and g.current_user.farmer.id != inquiry.farmer_id:
        return jsonify({'error': 'Forbidden', 'message': 'You are not authorized to update this inquiry.'}), 403

    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({'error': 'Bad Request', 'message': 'Missing "status" field.'}), 400

    inquiry.status = data['status']
    db.session.commit()

    return jsonify({'message': 'Inquiry status updated successfully.'}), 200

@inquiry_bp.route('/inquiries/<int:inquiry_id>', methods=['DELETE'])
@token_required
@role_required(['farmer', 'admin'])
def delete_inquiry(inquiry_id):
    """
    Deletes an inquiry.
    Only the farmer who received the inquiry or an admin can do this.
    """
    inquiry = db.session.get(Inquiry, inquiry_id)
    if not inquiry:
        return jsonify({'error': 'Not Found', 'message': 'Inquiry not found.'}), 404

    # --- Ownership Check ---
    if not g.current_user.is_admin and g.current_user.farmer.id != inquiry.farmer_id:
        return jsonify({'error': 'Forbidden', 'message': 'You are not authorized to delete this inquiry.'}), 403

    db.session.delete(inquiry)
    db.session.commit()

    return jsonify({'message': 'Inquiry deleted successfully.'}), 200