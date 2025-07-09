from flask import Blueprint, jsonify, current_app
from sqlalchemy import text
from extensions import db

# Create a Blueprint for development-only routes
dev_bp = Blueprint('dev', __name__)

@dev_bp.route('/dev/reset-db', methods=['POST'])
def reset_db():
    """
    (Development only) Drops all tables and recreates them.
    This is a destructive operation and is protected to only run in debug mode.
    """
    if not current_app.config['DEBUG']:
        return jsonify({'error': 'This endpoint is only available in development mode.'}), 403

    try:
        # The db.drop_all() and db.create_all() methods are the standard
        # SQLAlchemy way to reset the database based on the current models.
        db.drop_all()
        db.create_all()
        return jsonify({'message': 'Database has been reset successfully.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to reset database.',
            'error_details': str(e)
        }), 500