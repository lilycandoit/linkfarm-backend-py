from flask import Blueprint, request, jsonify, g
from extensions import db
from models.product import Product
from utils.decorators import token_required, role_required

# Create a Blueprint for product routes
product_bp = Blueprint('product', __name__)

@product_bp.route('/products', methods=['POST'])
@token_required
@role_required(['farmer']) # Only users with the 'farmer' role can create products
def create_product():
    """
    Creates a new product for the authenticated farmer.
    The product is automatically associated with the logged-in farmer.
    """
    data = request.get_json()

    if not data or not all(key in data for key in ['name', 'price']):
        return jsonify({'error': 'Bad Request', 'message': 'Missing required fields: name, price.'}), 400

    try:
        new_product = Product(
            # Crucial: The farmer_id is taken from the authenticated user, not the request body.
            # This ensures a farmer can only create products for themselves.
            farmer_id=g.current_user.farmer.id,
            name=data['name'],
            price=data['price'],
            description=data.get('description'),
            unit=data.get('unit', 'lb'),
            category=data.get('category'),
            image_url=data.get('image_url'),
            is_available=data.get('is_available', True)
        )
        db.session.add(new_product)
        db.session.commit()

        return jsonify({
            'message': 'Product created successfully!',
            'product': {
                'id': new_product.id,
                'name': new_product.name,
                'price': str(new_product.price) # Convert Decimal to string for JSON
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

@product_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """
    Retrieves a specific product by ID. This is a public endpoint.
    """
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'error': 'Not Found', 'message': 'Product not found.'}), 404

    return jsonify({
        'id': product.id,
        'farmer_id': product.farmer_id,
        'name': product.name,
        'description': product.description,
        'price': str(product.price),
        'unit': product.unit,
        'category': product.category,
        'image_url': product.image_url,
        'is_available': product.is_available
    }), 200

### Update a product
@product_bp.route('/products/<int:product_id>', methods=['PUT'])
@token_required
@role_required(['farmer', 'admin']) # Only farmers or admins can attempt to update
def update_product(product_id):
    """
    Updates an existing product.
    Only the farmer who owns the product or an admin can perform this action.
    """
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'error': 'Not Found', 'message': 'Product not found.'}), 404

    # --- Crucial Ownership Check ---
    # The user must be an admin OR they must be a farmer who owns this specific product.
    if not g.current_user.is_admin and g.current_user.farmer.id != product.farmer_id:
        return jsonify({'error': 'Forbidden', 'message': 'You are not authorized to update this product.'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Bad Request', 'message': 'No data provided for update.'}), 400

    try:
        for key, value in data.items():
            if hasattr(product, key) and key not in ['id', 'farmer_id', 'created_at', 'updated_at']:
                setattr(product, key, value)

        db.session.commit()
        return jsonify({'message': 'Product updated successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

@product_bp.route('/products/<int:product_id>', methods=['DELETE'])
@token_required
@role_required(['farmer', 'admin']) # Only farmers or admins can attempt to delete
def delete_product(product_id):
    """
    Deletes a product.
    Only the farmer who owns the product or an admin can perform this action.
    """
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'error': 'Not Found', 'message': 'Product not found.'}), 404

    # --- Crucial Ownership Check ---
    if not g.current_user.is_admin and g.current_user.farmer.id != product.farmer_id:
        return jsonify({'error': 'Forbidden', 'message': 'You are not authorized to delete this product.'}), 403

    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500