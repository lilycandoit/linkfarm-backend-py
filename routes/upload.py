import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, url_for
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity

"""
This module handles file uploads for the LinkFarm application.

Key Concepts:
1. secure_filename(): Sanitizes filenames to prevent directory traversal attacks
2. JWT protection: Only authenticated farmers can upload images
3. File validation: Check file type and size before accepting
4. Unique filenames: Prevent overwrites by using UUIDs
"""

upload_bp = Blueprint('upload', __name__)

# Configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes

def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.

    Example: 'photo.jpg' -> True, 'script.py' -> False
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file_storage):
    """
    Check if file size is within allowed limits.

    Explanation:
    - file_storage.seek(0, 2) moves to end of file
    - file_storage.tell() gets current position (= file size)
    - file_storage.seek(0) resets to beginning for later reading
    """
    file_storage.seek(0, 2)  # Move to end of file
    size = file_storage.tell()  # Get file size
    file_storage.seek(0)  # Reset to beginning

    return size <= MAX_FILE_SIZE

@upload_bp.route('/product-image', methods=['POST'])
@jwt_required()  # This decorator ensures user is logged in
def upload_product_image():
    """
    Upload a product image and return the URL.

    Protected endpoint - requires JWT token in Authorization header.
    Expected: Authorization: Bearer <token>
    """
    # Get the current user's ID from the JWT token
    current_user_id = get_jwt_identity()

    # Check if the request contains a file
    if 'file' not in request.files:
        return jsonify({
            'error': 'Bad Request',
            'message': 'No file part in the request'
        }), 400

    file = request.files['file']

    # Check if user actually selected a file
    if file.filename == '':
        return jsonify({
            'error': 'Bad Request',
            'message': 'No file selected'
        }), 400

    # Validate file type
    if not allowed_file(file.filename):
        return jsonify({
            'error': 'Bad Request',
            'message': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400

    # Validate file size
    if not validate_file_size(file):
        return jsonify({
            'error': 'Bad Request',
            'message': f'File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024)}MB'
        }), 400

    try:
        # Get the file extension
        file_ext = file.filename.rsplit('.', 1)[1].lower()

        # Generate a unique filename using UUID to prevent overwrites
        # Format: <user_id>_<timestamp>_<uuid>.<extension>
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{current_user_id}_{timestamp}_{uuid.uuid4().hex[:8]}.{file_ext}"

        # Secure the filename (removes potentially dangerous characters)
        safe_filename = secure_filename(unique_filename)

        # Construct the full file path
        upload_folder = os.path.join(current_app.root_path, 'uploads', 'product-images')

        # Ensure the upload directory exists
        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(upload_folder, safe_filename)

        # Save the file to disk
        file.save(file_path)

        # Generate the URL that will be used to access this image
        # In development: http://localhost:5000/uploads/product-images/filename.jpg
        # In production: https://yourdomain.com/uploads/product-images/filename.jpg
        image_url = f"{request.host_url}uploads/product-images/{safe_filename}"

        return jsonify({
            'message': 'Image uploaded successfully',
            'imageUrl': image_url,
            'filename': safe_filename
        }), 201

    except Exception as e:
        # Log the error for debugging
        current_app.logger.error(f'Error uploading file: {str(e)}')

        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Failed to upload image. Please try again.'
        }), 500

@upload_bp.route('/delete-image', methods=['DELETE'])
@jwt_required()
def delete_image():
    """
    Delete an uploaded image (optional feature for cleanup).

    Expects JSON: {"filename": "image_name.jpg"}
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data or 'filename' not in data:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Filename is required'
        }), 400

    filename = secure_filename(data['filename'])

    # Security check: Ensure the filename belongs to the current user
    # Format: <user_id>_<timestamp>_<uuid>.<extension>
    if not filename.startswith(current_user_id):
        return jsonify({
            'error': 'Forbidden',
            'message': 'You can only delete your own images'
        }), 403

    try:
        file_path = os.path.join(
            current_app.root_path,
            'uploads',
            'product-images',
            filename
        )

        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({
                'message': 'Image deleted successfully'
            }), 200
        else:
            return jsonify({
                'error': 'Not Found',
                'message': 'Image not found'
            }), 404

    except Exception as e:
        current_app.logger.error(f'Error deleting file: {str(e)}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Failed to delete image'
        }), 500
