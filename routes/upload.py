import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity
from supabase import create_client, Client

# --- Supabase Integration ---
# Initialize Supabase client. These environment variables must be set on Koyeb.
# SUPABASE_URL and SUPABASE_KEY are found in your Supabase project's API settings.
# The service_role key is used for backend operations, bypassing RLS policies.

def get_supabase_client():
    """Lazy initialization of Supabase client"""
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables are required")
    return create_client(url, key)

BUCKET_NAME = "product-images"

upload_bp = Blueprint('upload', __name__)

# Configuration (can be kept for initial client-side validation if needed)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes

def allowed_file(filename):
    """Checks if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/product-image', methods=['POST'])
@jwt_required()
def upload_product_image():
    """
    Uploads a product image to Supabase Storage and returns the public URL.
    This is a protected endpoint requiring a JWT token.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'Bad Request', 'message': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Bad Request', 'message': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Bad Request', 'message': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400

    # Note: File size validation is still good practice but less critical
    # as Supabase has its own limits.

    current_user_id = get_jwt_identity()

    # Try Supabase first, fallback to local if keys are missing
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")

    try:
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{current_user_id}_{timestamp}_{uuid.uuid4().hex[:8]}.{file_ext}"
        safe_filename = secure_filename(unique_filename)

        if supabase_url and supabase_key:
            # --- Supabase Upload Path ---
            # Read file content into memory to upload
            file_content = file.read()
            supabase = create_client(supabase_url, supabase_key)

            res = supabase.storage.from_(BUCKET_NAME).upload(
                path=safe_filename,
                file=file_content,
                file_options={"content-type": file.mimetype}
            )

            if not (hasattr(res, 'status_code') and res.status_code in [200, 201]):
                error_msg = res.text if hasattr(res, 'text') else "Unknown storage error"
                current_app.logger.error(f"Supabase upload failed: {error_msg}")
                return jsonify({'error': 'Internal Server Error', 'message': 'Failed to upload image to storage.'}), 500

            public_url_res = supabase.storage.from_(BUCKET_NAME).get_public_url(safe_filename)

            # Support various SDK versions for get_public_url return types
            image_url = public_url_res
            if isinstance(public_url_res, dict) and 'publicUrl' in public_url_res:
                image_url = public_url_res['publicUrl']
            elif hasattr(public_url_res, 'public_url'):
                image_url = getattr(public_url_res, 'public_url')
        else:
            # --- Local Fallback Path ---
            # Create local directory if it doesn't exist
            local_dir = os.path.join(current_app.root_path, 'uploads', 'product-images')
            os.makedirs(local_dir, exist_ok=True)

            file_path = os.path.join(local_dir, safe_filename)
            file.save(file_path)

            # Construct local URL
            image_url = f"{request.host_url.rstrip('/')}/uploads/product-images/{safe_filename}"
            current_app.logger.info(f"Local upload success: {image_url}")

        return jsonify({
            'message': 'Image uploaded successfully',
            'imageUrl': image_url,
            'filename': safe_filename,
            'storage': 'supabase' if (supabase_url and supabase_key) else 'local'
        }), 201

    except Exception as e:
        current_app.logger.error(f'Error uploading file: {str(e)}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': f'Upload failed: {str(e)}'
        }), 500


@upload_bp.route('/delete-image', methods=['DELETE'])
@jwt_required()
def delete_image():
    """
    Deletes an uploaded image from Supabase Storage.
    Expects JSON: {"filename": "image_name.jpg"}
    """
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({'error': 'Bad Request', 'message': 'Filename is required'}), 400

    filename = secure_filename(data['filename'])
    current_user_id = get_jwt_identity()

    # Security check: Ensure the filename appears to belong to the current user
    if not str(filename).startswith(str(current_user_id)):
        return jsonify({'error': 'Forbidden', 'message': 'You can only delete your own images'}), 403

    try:
        # Get Supabase client
        supabase = get_supabase_client()

        # Remove the file from Supabase Storage
        res = supabase.storage.from_(BUCKET_NAME).remove([filename])

        if res.status_code != 200:
            # Log the error but still return a success-like message if file might be gone
            current_app.logger.warning(f"Supabase delete returned non-200 status: {res.text}")

        return jsonify({'message': 'Image deletion request processed'}), 200

    except Exception as e:
        current_app.logger.error(f'Error deleting file from Supabase: {str(e)}')
        return jsonify({'error': 'Internal Server Error', 'message': 'Failed to delete image'}), 500