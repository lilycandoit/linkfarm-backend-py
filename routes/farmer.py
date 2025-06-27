from flask import Blueprint, request, jsonify, g
from extensions import db
from models.farmer import Farmer
from models.user import User # Needed for relationship access
from utils.decorators import token_required, role_required

# Create a Blueprint for farmer routes
farmer_bp = Blueprint('farmer', __name__)

@farmer_bp.route('/farmers', methods=['POST'])
@token_required
@role_required(['user', 'admin']) # A regular user can create their farmer profile, admin can create for others
def create_farmer_profile():
    """
    Creates a new farmer profile for the authenticated user.
    A user can only have one farmer profile.
    """
    data = request.get_json()

    if not data or not data.get('farm_name'):
        return jsonify({'error': 'Bad Request', 'message': 'Farm name is required.'}), 400

    # Check if the current user already has a farmer profile
    if g.current_user.farmer:
        return jsonify({'error': 'Conflict', 'message': 'User already has a farmer profile.'}), 409

    try:
        new_farmer = Farmer(
            user_id=g.current_user.id,
            farm_name=data['farm_name'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            location=data.get('location'),
            phone=data.get('phone'),
            description=data.get('description'),
            profile_image_url=data.get('profile_image_url')
        )
        # Add the new farmer profile to the session
        db.session.add(new_farmer)

        # --- Crucial Logic Fix ---
        # Promote the user's role to 'farmer' upon successful profile creation.
        g.current_user.role = 'farmer'
        db.session.commit()

        return jsonify({
            'message': 'Farmer profile created successfully!',
            'farmer': {
                'id': new_farmer.id,
                'user_id': new_farmer.user_id,
                'farm_name': new_farmer.farm_name,
                'location': new_farmer.location,
                'created_at': new_farmer.created_at.isoformat()
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

@farmer_bp.route('/farmers/<int:farmer_id>', methods=['GET'])
@token_required # Anyone with a valid token can view a farmer profile
def get_farmer_profile(farmer_id):
    """
    Retrieves a specific farmer profile by ID.
    """
    farmer = db.session.get(Farmer, farmer_id)
    if not farmer:
        return jsonify({'error': 'Not Found', 'message': 'Farmer profile not found.'}), 404

    return jsonify({
        'id': farmer.id,
        'user_id': farmer.user_id,
        'farm_name': farmer.farm_name,
        'first_name': farmer.first_name,
        'last_name': farmer.last_name,
        'location': farmer.location,
        'phone': farmer.phone,
        'description': farmer.description,
        'profile_image_url': farmer.profile_image_url,
        'created_at': farmer.created_at.isoformat(),
        'updated_at': farmer.updated_at.isoformat()
    }), 200

@farmer_bp.route('/farmers/<int:farmer_id>', methods=['PUT'])
@token_required
@role_required(['farmer', 'admin']) # Only the farmer themselves or an admin can update
def update_farmer_profile(farmer_id):
    """
    Updates an existing farmer profile.
    Only the associated user (if they are a farmer) or an admin can update.
    """
    farmer = db.session.get(Farmer, farmer_id)
    if not farmer:
        return jsonify({'error': 'Not Found', 'message': 'Farmer profile not found.'}), 404

    # Authorization check: User must own the profile OR be an admin
    if g.current_user.id != farmer.user_id and not g.current_user.is_admin:
        return jsonify({'error': 'Forbidden', 'message': 'You are not authorized to update this profile.'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Bad Request', 'message': 'No data provided for update.'}), 400

    try:
        for key, value in data.items():
            if hasattr(farmer, key) and key not in ['id', 'user_id', 'created_at', 'updated_at']:
                setattr(farmer, key, value)

        db.session.commit()

        return jsonify({
            'message': 'Farmer profile updated successfully!',
            'farmer': {
                'id': farmer.id,
                'farm_name': farmer.farm_name,
                'location': farmer.location,
                'updated_at': farmer.updated_at.isoformat()
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

@farmer_bp.route('/farmers/<int:farmer_id>', methods=['DELETE'])
@token_required
@role_required(['farmer', 'admin']) # Only the farmer themselves or an admin can delete
def delete_farmer_profile(farmer_id):
    """
    Deletes a farmer profile.
    Only the associated user (if they are a farmer) or an admin can delete.
    """
    farmer = db.session.get(Farmer, farmer_id)
    if not farmer:
        return jsonify({'error': 'Not Found', 'message': 'Farmer profile not found.'}), 404

    # Authorization check: User must own the profile OR be an admin
    if g.current_user.id != farmer.user_id and not g.current_user.is_admin:
        return jsonify({'error': 'Forbidden', 'message': 'You are not authorized to delete this profile.'}), 403

    try:
        db.session.delete(farmer)
        db.session.commit()
        return jsonify({'message': 'Farmer profile deleted successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500