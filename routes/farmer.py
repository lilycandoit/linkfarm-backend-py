from flask import Blueprint, request, jsonify
from extensions import db
from models.farmer import Farmer
from models.user import User
from schemas.farmer_schema import FarmerSchema
from marshmallow import ValidationError
from decorators import jwt_required

# Create a Blueprint for farmer routes
farmer_bp = Blueprint('farmer', __name__)
farmer_schema = FarmerSchema()
farmers_schema = FarmerSchema(many=True)

@farmer_bp.route('', methods=['GET'])
def list_farmers():
    """
    Public endpoint to retrieve a paginated list of all farmers.
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = Farmer.query.paginate(page=page, per_page=per_page, error_out=False)
    farmers = pagination.items

    return jsonify({
        'farmers': farmers_schema.dump(farmers),
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@farmer_bp.route('', methods=['POST'])
@jwt_required
def create_farmer_profile(current_user):
    """
    Creates a new farmer profile for the authenticated user.
    A user can only have one farmer profile.
    """
    if current_user.farmer_profile:
        return jsonify({'error': 'Conflict', 'message': 'User already has a farmer profile.'}), 409

    data = request.get_json()
    try:
        # Validate incoming data using the schema
        loaded_data = farmer_schema.load(data)
        new_farmer = Farmer(user_id=current_user.id, **loaded_data)
        db.session.add(new_farmer)

        # Promote the user's role to 'farmer' if they are currently a 'user'
        if current_user.role == 'user':
            current_user.role = 'farmer'

        db.session.commit()
        return jsonify(farmer_schema.dump(new_farmer)), 201
    except ValidationError as err:
        return jsonify({'error': 'Validation Error', 'messages': err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

@farmer_bp.route('/<int:farmer_id>', methods=['GET'])
def get_farmer_by_id(farmer_id):
    """
    Publicly retrieves a specific farmer profile by ID, including their products.
    """
    farmer = db.session.get(Farmer, farmer_id)
    if not farmer:
        return jsonify({'error': 'Not Found', 'message': 'Farmer profile not found.'}), 404
    return jsonify(farmer_schema.dump(farmer, include_products=True)), 200

@farmer_bp.route('/me', methods=['GET'])
@jwt_required
def get_my_farmer_profile(current_user):
    """
    Retrieves the profile for the currently authenticated user.
    This is the endpoint your dashboard calls.
    """
    farmer = db.session.execute(db.select(Farmer).filter_by(user_id=current_user.id)).scalar_one_or_none()
    if not farmer:
        return jsonify({'error': 'Not Found', 'message': 'Farmer profile not found for this user.'}), 404
    return jsonify(farmer_schema.dump(farmer)), 200

@farmer_bp.route('/me', methods=['PUT'])
@jwt_required
def update_my_farmer_profile(current_user):
    """Updates the profile for the currently authenticated user."""
    farmer = db.session.execute(db.select(Farmer).filter_by(user_id=current_user.id)).scalar_one_or_none()
    if not farmer:
        return jsonify({'error': 'Not Found', 'message': 'Farmer profile not found.'}), 404

    data = request.get_json()
    try:
        # Use the schema to validate and load the data for update
        loaded_data = farmer_schema.load(data, partial=True)
        for key, value in loaded_data.items():
            setattr(farmer, key, value)
        db.session.commit()
        return jsonify(farmer_schema.dump(farmer)), 200
    except ValidationError as err:
        return jsonify({'error': 'Validation Error', 'messages': err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500