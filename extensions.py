from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_socketio import SocketIO

"""
This file centralizes the creation of Flask extension instances.
By creating them here without an app, we can import them into our
blueprints and models without causing circular import errors.
"""
db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()
migrate = Migrate()  # Database migration manager using Alembic
socketio = SocketIO(cors_allowed_origins="*") # Manage real-time WebSocket connections
