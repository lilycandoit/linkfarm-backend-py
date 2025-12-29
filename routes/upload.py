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
    return handle_upload("product-images")

@upload_bp.route('/avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    return handle_upload("avatars")

def handle_upload(bucket_name):
    """
    Helper function to handle file uploads to a specific bucket or local directory.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'Bad Request', 'message': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Bad Request', 'message': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Bad Request', 'message': 'Invalid file type'}), 400

    current_user_id = get_jwt_identity()
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")

    try:
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{current_user_id}_{timestamp}_{uuid.uuid4().hex[:8]}.{file_ext}"
        safe_filename = secure_filename(unique_filename)

        if supabase_url and supabase_key:
            file_content = file.read()
            supabase = create_client(supabase_url, supabase_key)
            # Ensure bucket exists (optional, could just assume)
            res = supabase.storage.from_(bucket_name).upload(
                path=safe_filename,
                file=file_content,
                file_options={"content-type": file.mimetype}
            )

            if not (hasattr(res, 'status_code') and res.status_code in [200, 201]):
                # Fallback to creating bucket if it might not exist (minimal error handling)
                return jsonify({'error': 'Internal Server Error', 'message': 'Storage upload failed.'}), 500

            public_url_res = supabase.storage.from_(bucket_name).get_public_url(safe_filename)
            image_url = public_url_res
            if isinstance(public_url_res, dict) and 'publicUrl' in public_url_res:
                image_url = public_url_res['publicUrl']
            elif hasattr(public_url_res, 'public_url'):
                image_url = getattr(public_url_res, 'public_url')
        else:
            local_dir = os.path.join(current_app.root_path, 'uploads', bucket_name)
            os.makedirs(local_dir, exist_ok=True)
            file_path = os.path.join(local_dir, safe_filename)
            file.save(file_path)
            image_url = f"{request.host_url.rstrip('/')}/uploads/{bucket_name}/{safe_filename}"

        return jsonify({
            'message': 'Upload successful',
            'imageUrl': image_url,
            'filename': safe_filename
        }), 201

    except Exception as e:
        current_app.logger.error(f'Upload error: {str(e)}')
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500


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