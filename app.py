import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from config import config
from extensions import db, ma, jwt, migrate

# Load environment variables from .env file
# It's good practice to call this at the top of your entry file.
load_dotenv()

def create_app(config_name=None):
    """
    Application Factory: Creates and configures the Flask application.
    This pattern makes the application more modular and easier to test.
    """
    app = Flask(__name__)

    # --- 1. Load Configuration ---
    # If no config_name is provided, default to the FLASK_ENV variable,
    # or 'development' if that's not set.
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])

    # --- 2. Initialize Extensions ---
    # Bind the extensions to the Flask app instance.
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)  # Initialize Flask-Migrate with app and db

    # Import models so Flask-Migrate can detect them for migrations
    # This must be done after db.init_app() to avoid circular imports
    from models import User, Farmer, Product, Inquiry

    # --- 3. Configure CORS ---
    # This allows your frontend (running on a different port) to make
    # requests to the backend API.
    CORS(
        app,
        origins=app.config['CORS_ORIGINS'],
        supports_credentials=True,
        allow_headers=['Content-Type', 'Authorization'],
        expose_headers=['Content-Type', 'Authorization'],
        methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
    )

    # --- 4. Register Blueprints ---
    # Blueprints are used to organize routes into separate modules.
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.farmer import farmer_bp
    from routes.product import product_bp
    from routes.inquiry import inquiry_bp
    from routes.upload import upload_bp
    from routes.dashboard import dashboard_bp
    from routes.ai import ai_bp
    from routes.analytics import analytics_bp

    # All blueprints are registered under the /api prefix
    app.register_blueprint(main_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(farmer_bp, url_prefix='/api/farmers')
    app.register_blueprint(product_bp, url_prefix='/api/products')
    app.register_blueprint(inquiry_bp, url_prefix='/api/inquiries')
    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    app.register_blueprint(dashboard_bp, url_prefix='/api')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')

    # Conditionally register the development blueprint
    if app.config['DEBUG']:
        from routes.dev import dev_bp
        app.register_blueprint(dev_bp, url_prefix='/api')

    # --- 5. Root-level Health Check for AWS Elastic Beanstalk ---
    # EB health checks hit "/" by default, so we provide a simple endpoint here
    @app.route('/')
    def root_health_check():
        """
        Simple health check endpoint for AWS Elastic Beanstalk.
        Returns 200 OK if the application is running.
        """
        return jsonify({
            'status': 'healthy',
            'message': 'LinkFarm API is running',
            'api_docs': '/api'
        }), 200

    # --- 6. Serve Uploaded Files as Static Content ---
    # This route allows the frontend to access uploaded images
    # Example: http://localhost:5000/uploads/product-images/image.jpg
    @app.route('/uploads/<path:subpath>/<filename>')
    def serve_upload(subpath, filename):
        """
        Serve uploaded files (e.g., product images).

        Security Note: In production, it's better to serve static files
        through a proper web server (Nginx, Apache) or CDN for better performance.
        This is acceptable for development and small deployments.
        """
        uploads_dir = os.path.join(app.root_path, 'uploads', subpath)
        return send_from_directory(uploads_dir, filename)

    # --- 7. Register Error Handlers ---
    # This provides consistent JSON error responses instead of default HTML pages.
    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({
            'error': 'Endpoint not found',
            'message': 'The requested URL was not found on this server.'
        }), 404

    @app.errorhandler(500)
    def internal_error(_error):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred on the server.'
        }), 500

    return app

if __name__ == '__main__':
    # This block is the entry point for running the application directly.
    # We wrap the startup in a try...except block to catch any configuration
    # or initialization errors and provide a clear error message.
    try:
        app = create_app()
        port = int(os.getenv('PORT', 5000))
        print("🚀 Starting LinkFarm API...")
        print(f"🌍 Environment: {app.config['ENV']}")
        print(f"🔧 Debug mode: {app.config['DEBUG']}")
        print(f"🔗 API running at: http://localhost:{port}/")
        app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
    except Exception as e:
        # This will catch any error during app creation and print it.
        print("❌ An error occurred during application startup:")
        print(f"   Error Type: {type(e).__name__}")
        print(f"   Error Details: {e}")
        import traceback
        traceback.print_exc()