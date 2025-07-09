from flask import Blueprint, jsonify, current_app
from sqlalchemy import text
from datetime import datetime

from extensions import db

# Create a Blueprint for the main, non-model-specific routes
main_bp = Blueprint('main', __name__)

@main_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify that the API and database are responsive.
    """
    db_ok = False
    try:
        # Use a connection from the engine to execute a simple query
        with db.engine.connect() as connection:
            connection.execute(text('SELECT 1'))
        db_ok = True
    except Exception:
        # If the query fails, db_ok remains False.
        pass

    return jsonify({
        'status': 'OK',
        'message': 'LinkFarm Python API is running! 🐍',
        'timestamp': datetime.now().isoformat(),
        'database_status': "Connected" if db_ok else "Disconnected",
        'environment': current_app.config['ENV']
    })

@main_bp.route('/', methods=['GET'])
def root():
    """
    Root endpoint that provides basic API information and a list of available endpoints.
    """
    return jsonify({
        'message': 'Welcome to LinkFarm API! 🌱',
        'version': '1.0.0',
        'environment': current_app.config['ENV'],
        'endpoints': {
            'public_routes': {
                'health_check': '/api/health',
                'list_farmers': '/api/farmers',
                'get_product': '/api/products/<product_id>',
            },
            'auth_routes': {
                'register': '/api/register',
                'login': '/api/login'
            }
        }
    })