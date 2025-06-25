from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables from .env file
# This must be called before accessing os.environ
load_dotenv()

app = Flask(__name__)

# Configure CORS (Cross-Origin Resource Sharing)
CORS(app, origins=[os.getenv('FRONTEND_URL', 'http://localhost:3000')])

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

### ===ROUTES===
# Health check endpoint - test if server is running
@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Simple health check endpoint
    Returns JSON with server status and timestamp
    """
    from datetime import datetime

    return jsonify({
        'status': 'OK',
        'message': 'LinkFarm Python API is running! 🐍',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# Test endpoint to verify database connection later
@app.route('/api/test-db', methods=['GET'])
def test_database():
    """
    Test database connection
    We'll implement this after setting up SQLAlchemy
    """
    return jsonify({
        'message': 'Database connection test - coming soon!',
        'database_url': os.getenv('DATABASE_URL', 'Not configured')
    })

# Root endpoint - helpful for debugging
@app.route('/', methods=['GET'])
def root():
    """
    Root endpoint - shows available endpoints
    """
    return jsonify({
        'message': 'Welcome to LinkFarm API! 🌱',
        'endpoints': {
            'health': '/api/health',
            'test_db': '/api/test-db',
            'farmers': '/api/farmers (coming soon)',
            'products': '/api/products (coming soon)'
        }
    })

# ============ ERROR HANDLERS ============

# Handle 404 errors (route not found)
@app.errorhandler(404)
def not_found(error):
    """
    Custom 404 handler
    Returns JSON instead of HTML error page
    """
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested URL was not found on this server',
        'status_code': 404
    }), 404

# Handle 500 errors (internal server errors)
@app.errorhandler(500)
def internal_error(error):
    """
    Custom 500 handler
    Returns JSON error response
    """
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong on our end',
        'status_code': 500
    }), 500

# ============ RUN APPLICATION ============

# This block only runs when you execute this file directly
# (not when imported as a module)
if __name__ == '__main__':
    # Get configuration from environment variables
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    port = int(os.getenv('PORT', 5000))

    # Print startup information
    print("🚀 Starting LinkFarm API...")
    print(f"📍 Health check: http://localhost:{port}/api/health")
    print(f"🌍 Environment: {os.getenv('FLASK_ENV', 'production')}")
    print(f"🗄️  Database: {os.getenv('DATABASE_URL', 'Not configured')}")

    # Start the Flask development server
    # debug=True enables auto-reload when you save files
    # host='0.0.0.0' allows external connections (needed for some deployments)
    app.run(
        debug=debug_mode,
        host='0.0.0.0',
        port=port
    )
