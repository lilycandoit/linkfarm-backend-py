from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models.farmer import Farmer
from models.user import User
from schemas.farmer_schema import FarmerSchema

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

    # Use modern SQLAlchemy 2.0 syntax for consistency and clarity.
    # db.paginate is the modern equivalent of the older .query.paginate()
    select_query = db.select(Farmer).order_by(Farmer.created_at.desc())
    pagination = db.paginate(select_query, page=page, per_page=per_page, error_out=False)
    farmers = pagination.items

    return jsonify({
        'farmers': farmers_schema.dump(farmers),
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    }), 200

@farmer_bp.route('', methods=['POST'])
@jwt_required()
def create_farmer_profile():
    """
    Creates a new farmer profile for the authenticated user.
    A user can only have one farmer profile.
    """
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({'error': 'Not Found', 'message': 'Authenticated user not found.'}), 404

    if user.farmer_profile:
        return jsonify({'error': 'Conflict', 'message': 'User already has a farmer profile.'}), 409

    data = request.get_fjson()
    try:
        # Validate and deserialize the incoming data directly into a Farmer object
        # because `load_instance=True` is set in the schema.
        new_farmer = farmer_schema.load(data, session=db.session)

        # Associate the new profile with the logged-in user
        new_farmer.user_id = user.id

        # Add the new instance to the session
        db.session.add(new_farmer)

        # Promote the user's role to 'farmer' if they are currently a 'user'
        if user.role == 'user':
            user.role = 'farmer'

        db.session.commit()
        return jsonify(farmer_schema.dump(new_farmer)), 201
    except ValidationError as err:
        return jsonify({'error': 'Validation Error', 'messages': err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

@farmer_bp.route('/<string:farmer_id>', methods=['GET'])
def get_farmer_by_id(farmer_id):
    """
    Publicly retrieves a specific farmer profile by ID, including their products.
    The route parameter must be a string to accommodate UUIDs.
    """
    farmer = db.session.get(Farmer, farmer_id) # .get() is the most efficient way to query by primary key
    if not farmer:
        return jsonify({'error': 'Not Found', 'message': 'Farmer profile not found.'}), 404
    # The schema controls which nested fields are included.
    return jsonify(farmer_schema.dump(farmer)), 200

@farmer_bp.route('/me', methods=['GET'])
@jwt_required()
def get_my_farmer_profile():
    """
    Retrieves the profile for the currently authenticated user.
    This is the endpoint your dashboard calls.
    """
    user_id = get_jwt_identity()
    farmer = db.session.execute(db.select(Farmer).filter_by(user_id=user_id)).scalar_one_or_none()
    if not farmer:
        return jsonify({'error': 'Not Found', 'message': 'Farmer profile not found for this user.'}), 404
    return jsonify(farmer_schema.dump(farmer)), 200

@farmer_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_my_farmer_profile():
    """Updates the profile for the currently authenticated user."""
    user_id = get_jwt_identity()
    farmer = db.session.execute(db.select(Farmer).filter_by(user_id=user_id)).scalar_one_or_none()
    if not farmer:
        return jsonify({'error': 'Not Found', 'message': 'Farmer profile not found.'}), 404

    data = request.get_json()
    try:
        # Use the schema to validate and load the data for update.
        # `partial=True` allows for updating only a subset of fields.
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