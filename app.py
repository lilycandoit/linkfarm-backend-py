import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from config import config
from extensions import db, ma, jwt

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
    print(f"--- [1/7] Loading config: {config_name} ---")
    app.config.from_object(config[config_name])
    print("--- [2/7] Config loaded successfully ---")

    # --- 2. Initialize Extensions ---
    # Bind the extensions to the Flask app instance.
    print("--- [3/7] Initializing extensions... ---")
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    print("--- [4/7] Extensions initialized successfully ---")

    # --- 3. Configure CORS ---
    # This allows your frontend (running on a different port) to make
    # requests to the backend API.
    print("--- [5/7] Configuring CORS... ---")
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    print("--- [6/7] CORS configured successfully ---")

    # --- 4. Register Blueprints ---
    # Blueprints are used to organize routes into separate modules.
    print("--- [7/7] Registering blueprints... ---")
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.farmer import farmer_bp
    from routes.product import product_bp
    from routes.inquiry import inquiry_bp

    # All blueprints are registered under the /api prefix
    app.register_blueprint(main_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(farmer_bp, url_prefix='/api/farmers')
    app.register_blueprint(product_bp, url_prefix='/api/products')
    app.register_blueprint(inquiry_bp, url_prefix='/api/inquiries')

    # Conditionally register the development blueprint
    if app.config['DEBUG']:
        from routes.dev import dev_bp
        app.register_blueprint(dev_bp, url_prefix='/api')
    print("--- Blueprints registered successfully ---")

    # --- 5. Register Error Handlers ---
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

    print("--- App creation complete. Returning app instance. ---")
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
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        # This will catch any error during app creation and print it.
        print("❌ An error occurred during application startup:")
        print(f"   Error Type: {type(e).__name__}")
        print(f"   Error Details: {e}")
        import traceback
        traceback.print_exc()