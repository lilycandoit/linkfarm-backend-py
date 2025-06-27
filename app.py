# Import Flask framework and necessary modules
from flask import Flask, jsonify, Response, request
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import text
import os
from datetime import datetime

# Import our configuration
from config import config

# Import extensions
from extensions import db

# Load environment variables from .env file
load_dotenv()

# Create Flask application instance
app = Flask(__name__)

# Load configuration based on environment
# Gets FLASK_ENV from environment, defaults to 'development'
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize extensions with our Flask app
db.init_app(app)

# Import models so SQLAlchemy knows about them
# This must be done AFTER db is initialized, but before blueprints are registered
from models.user import User

# Configure CORS (Cross-Origin Resource Sharing)
# Uses the CORS_ORIGINS from our config
CORS(app, origins=app.config['CORS_ORIGINS'])

# Import and register Blueprints
from routes.auth import auth_bp
app.register_blueprint(auth_bp, url_prefix='/api') # All routes in auth_bp will be prefixed with /api
from routes.farmer import farmer_bp
app.register_blueprint(farmer_bp, url_prefix='/api') # All routes in farmer_bp will be prefixed with /api
from routes.product import product_bp
app.register_blueprint(product_bp, url_prefix='/api') # All routes in product_bp will be prefixed with /api
from routes.dashboard import dashboard_bp
app.register_blueprint(dashboard_bp, url_prefix='/api') # All routes in dashboard_bp will be prefixed with /api
from routes.inquiry import inquiry_bp
app.register_blueprint(inquiry_bp, url_prefix='/api') # All routes in inquiry_bp will be prefixed with /api

# ============ ROUTES (API ENDPOINTS) ============

# Health check endpoint - test if server is running
@app.route('/api/health', methods=['GET'])
def health_check() -> Response:
    """
    Health check endpoint with database status
    Returns JSON with server status and database connection
    """
    db_ok = False
    try:
        # A quick check to see if we can connect to the DB
        with app.app_context():
            with db.engine.connect() as connection:
                connection.execute(text('SELECT 1'))
            db_ok = True
    except Exception:
        pass  # We don't need to log the error here, /api/test-db is for that

    return jsonify({
        'status': 'OK',
        'message': 'LinkFarm Python API is running! 🐍',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'database_status': "Connected" if db_ok else "Disconnected",
        'environment': os.getenv('FLASK_ENV', 'production')
    })

# Database connection test endpoint
@app.route('/api/test-db', methods=['GET'])
def test_db_endpoint() -> Response:
    """
    Detailed database connection test
    Shows database URL and connection status
    """
    try:
        # Use a connection from the engine to execute a query
        with db.engine.connect() as connection:
            result = connection.execute(text('SELECT version()'))
            version = result.scalar_one()

        return jsonify({
            'status': 'success',
            'message': 'Database connection successful! 🗄️',
            'database_url_preview': f"{app.config['SQLALCHEMY_DATABASE_URI'][:50]}...",
            'postgres_version': version,
            'sqlalchemy_echo': app.config['SQLALCHEMY_ECHO']
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Database connection failed.',
            'error_type': type(e).__name__,
            'error_details': str(e),
            'database_url_preview': f"{app.config['SQLALCHEMY_DATABASE_URI'][:50]}..."
        }), 500

# Root endpoint - shows available endpoints
@app.route('/', methods=['GET'])
def root() -> Response:
    """
    Root endpoint - shows API information and available endpoints
    """
    return jsonify({
        'message': 'Welcome to LinkFarm API! 🌱',
        'version': '1.0.0',
        'environment': app.config['ENV'],
        # Updated to reflect the current state of the API
        'endpoints': {
            'public_routes': {
                'health_check': '/api/health',
                'list_farmers': '/api/farmers',
                'get_farmer_profile': '/api/farmers/<farmer_id>',
                'list_products_by_farmer': '/api/farmers/<farmer_id>/products',
                'get_product': '/api/products/<product_id>',
                'submit_inquiry': '/api/inquiries'
            },
            'auth_routes': {
                'register': '/api/register',
                'login': '/api/login'
            }
        }
    })

# ============ DEVELOPMENT-ONLY ROUTES ============

# WARNING: This route is for development only and will delete all data.
@app.route('/api/dev/reset-db', methods=['POST'])
def reset_db():
    """
    (Development only) Drops all tables and recreates them.
    This is useful for applying schema changes.
    """
    if app.config['DEBUG'] is False:
        return jsonify({'error': 'This endpoint is only available in development mode.'}), 403

    try:
        with app.app_context():
            # Explicitly drop the 'users' table with CASCADE.
            # This handles cases where other tables (like 'farmers')
            # might exist in the DB and have foreign keys to 'users',
            # even if those tables are not defined in our current models.
            # We commit this to ensure the table is dropped before proceeding.
            db.session.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
            db.session.commit() # Commit the raw SQL drop

            # Explicitly drop the 'products' table with CASCADE.
            db.session.execute(text("DROP TABLE IF EXISTS products CASCADE;"))
            db.session.commit() # Commit the raw SQL drop

            # Explicitly drop the 'inquiries' table with CASCADE.
            db.session.execute(text("DROP TABLE IF EXISTS inquiries CASCADE;"))
            db.session.commit() # Commit the raw SQL drop

            # Explicitly drop the 'farmers' table with CASCADE for similar reasons.
            db.session.execute(text("DROP TABLE IF EXISTS farmers CASCADE;"))
            db.session.commit() # Commit the raw SQL drop

            db.drop_all()
            db.create_all()
        return jsonify({'message': 'Database has been reset successfully.'}), 200
    except Exception as e:
        db.session.rollback() # Rollback in case of error during raw SQL or db.drop_all()
        return jsonify({
            'status': 'error',
            'message': 'Failed to reset database.',
            'error_type': type(e).__name__,
            'error_details': str(e)
        }), 500

# ============ ERROR HANDLERS ============

# Handle 404 errors (route not found)
@app.errorhandler(404)
def not_found(_error: Exception) -> tuple[Response, int]:
    """
    Custom 404 handler - returns JSON instead of HTML.
    """
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested URL was not found on this server',
        'status_code': 404
    }), 404

# Handle 500 errors (internal server errors)
@app.errorhandler(500)
def internal_error(_error: Exception) -> tuple[Response, int]:
    """
    Custom 500 handler - returns JSON error response.
    """
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong on our end',
        'status_code': 500
    }), 500

# ============ APPLICATION STARTUP ============

if __name__ == '__main__':
    # Print startup information
    port = int(os.getenv('PORT', 5000))
    print("🚀 Starting LinkFarm API...")
    print(f"🌍 Environment: {os.getenv('FLASK_ENV', 'production')}")
    print(f"🔧 Debug mode: {app.config['DEBUG']}")
    print(f"🔗 API running at: http://localhost:{port}/")

    # Test database connection on startup
    # The 'with app.app_context()' is crucial here.
    # It ensures that the application context is available,
    # which SQLAlchemy needs to access the engine.
    with app.app_context():
        try:
            # Create database tables if they don't exist.
            # This will create a 'users' table based on the User model.
            db.create_all()
            print("✅ Database tables checked/created.")
            db.engine.connect().close()
            print("✅ Database connection successful.")
        except Exception as e:
            print("❌ Database connection failed. Please check your DATABASE_URL and ensure the database server is running.")
            print(f"   Error: {e}")

    # Start the Flask development server
    app.run(
        debug=app.config['DEBUG'],
        host='0.0.0.0',
        port=port
    )