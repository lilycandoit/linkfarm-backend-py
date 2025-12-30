"""
Vercel-compatible entry point WITHOUT WebSockets
Use this for serverless deployment on Vercel
"""
import os
os.environ['DISABLE_WEBSOCKETS'] = '1'

from flask import Flask
from flask_cors import CORS
from extensions import db, jwt, migrate, ma
from config import config_by_name

def create_app():
    """Application factory for Vercel deployment"""
    app = Flask(__name__)

    # Load configuration
    env = os.getenv('FLASK_ENV', 'production')
    app.config.from_object(config_by_name[env])

    # Initialize extensions (NO SocketIO)
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # CORS configuration
    CORS(
        app,
        origins=app.config['CORS_ORIGINS'],
        supports_credentials=True,
        allow_headers=['Content-Type', 'Authorization'],
        expose_headers=['Content-Type', 'Authorization'],
        methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
    )

    # Register blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.farmer import farmer_bp
    from routes.product import product_bp
    from routes.inquiry import inquiry_bp
    from routes.upload import upload_bp
    from routes.dashboard import dashboard_bp
    from routes.ai import ai_bp
    from routes.analytics import analytics_bp

    app.register_blueprint(main_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(farmer_bp, url_prefix='/api/farmers')
    app.register_blueprint(product_bp, url_prefix='/api/products')
    app.register_blueprint(inquiry_bp, url_prefix='/api/inquiries')
    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    app.register_blueprint(dashboard_bp, url_prefix='/api')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')

    # NOTE: WebSocket routes are NOT registered for Vercel

    return app

app = create_app()

# Vercel expects 'app' to be exported
if __name__ == '__main__':
    app.run()
