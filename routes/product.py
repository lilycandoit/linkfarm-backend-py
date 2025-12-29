from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models.farmer import Farmer
from models.user import User
from models.product import Product
from schemas.product_schema import product_schema, products_schema

# Create a Blueprint for product routes
product_bp = Blueprint('product', __name__)

@product_bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    """
    Creates a new product for the authenticated farmer.
    The product is automatically associated with the logged-in farmer.
    """
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    # Ensure the user has a farmer profile before they can create a product.
    if not user or not user.farmer_profile:
        return jsonify({'error': 'Forbidden', 'message': 'You must have a farmer profile to create products.'}), 403

    data = request.get_json()
    try:
        # Use the schema to validate and create a Product instance
        new_product = product_schema.load(data)
        # Securely associate the product with the logged-in farmer
        new_product.farmer_id = user.farmer_profile.id

        db.session.add(new_product)
        db.session.commit()

        # Return the serialized new product data
        return jsonify({
            'message': 'Product created successfully!',
            'product': product_schema.dump(new_product)
        }), 201
    except ValidationError as err:
        return jsonify({'error': 'Validation Error', 'messages': err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

@product_bp.route('', methods=['GET'])
def list_all_products():
    """
    Public endpoint to retrieve a paginated list of products with advanced filtering.
    Supports: search, categories, locations, price range, and sorting.
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # Filtering parameters
    search_term = request.args.get('search', None, type=str)
    categories = request.args.getlist('category') # Supports multiple categories
    locations = request.args.getlist('location')   # Supports multiple locations
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)

    # Sorting parameter
    sort_by = request.args.get('sort_by', 'newest', type=str)

    # Base query
    select_query = db.select(Product).join(Farmer).filter(Product.is_available == True)

    # 1. Improved Search Filter
    if search_term:
        search_ilike = f"%{search_term}%"
        select_query = select_query.filter(db.or_(
            Product.name.ilike(search_ilike),
            Product.description.ilike(search_ilike),
            Farmer.farm_name.ilike(search_ilike)
        ))

    # 2. Multi-Category Filter
    if categories:
        select_query = select_query.filter(Product.category.in_(categories))

    # 3. Multi-Location Filter (Filtering by Farmer location)
    if locations:
        select_query = select_query.filter(Farmer.location.in_(locations))

    # 4. Price range filters
    if min_price is not None:
        select_query = select_query.filter(Product.price >= min_price)
    if max_price is not None:
        select_query = select_query.filter(Product.price <= max_price)

    # 5. Sorting Logic
    if sort_by == 'price-low':
        select_query = select_query.order_by(Product.price.asc())
    elif sort_by == 'price-high':
        select_query = select_query.order_by(Product.price.desc())
    elif sort_by == 'name':
        select_query = select_query.order_by(Product.name.asc())
    else:
        # Default: newest first
        select_query = select_query.order_by(Product.created_at.desc())

    # Execute paginated query
    pagination = db.paginate(select_query, page=page, per_page=per_page, error_out=False)
    products = pagination.items

    return jsonify({
        'products': products_schema.dump(products),
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    }), 200

@product_bp.route('/<string:product_id>', methods=['GET'])
def get_product(product_id):
    """
    Retrieves a specific product by ID. This is a public endpoint.
    """
    product = db.session.get(Product, product_id) # .get() is the most efficient way to query by primary key
    if not product:
        return jsonify({'error': 'Not Found', 'message': 'Product not found.'}), 404

    return jsonify(product_schema.dump(product)), 200

@product_bp.route('/<string:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """
    Updates an existing product.
    Only the farmer who owns the product or an admin can perform this action.
    """
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    product = db.session.get(Product, product_id)

    if not product:
        return jsonify({'error': 'Not Found', 'message': 'Product not found.'}), 404

    # --- Crucial Ownership Check ---
    is_owner = user.farmer_profile and user.farmer_profile.id == product.farmer_id
    is_admin = user.role == 'admin'

    if not is_owner and not is_admin:
        return jsonify({'error': 'Forbidden', 'message': 'You are not authorized to update this product.'}), 403

    data = request.get_json()
    try:
        # Use the schema to validate and load the data for update.
        # `partial=True` allows for updating only a subset of fields.
        # `instance=product` tells Marshmallow to update this existing object.
        updated_product = product_schema.load(data, instance=product, partial=True, session=db.session)
        db.session.commit()
        return jsonify(product_schema.dump(updated_product)), 200
    except ValidationError as err:
        return jsonify({'error': 'Validation Error', 'messages': err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

@product_bp.route('/<string:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """
    Deletes a product.
    Only the farmer who owns the product or an admin can perform this action.
    """
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    product = db.session.get(Product, product_id)

    if not product:
        return jsonify({'error': 'Not Found', 'message': 'Product not found.'}), 404

    # --- Crucial Ownership Check ---
    is_owner = user.farmer_profile and user.farmer_profile.id == product.farmer_id
    is_admin = user.role == 'admin'

    if not is_owner and not is_admin:
        return jsonify({'error': 'Forbidden', 'message': 'You are not authorized to delete this product.'}), 403

    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500