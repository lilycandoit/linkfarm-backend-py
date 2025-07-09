from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager

"""
This file centralizes the creation of Flask extension instances.
By creating them here without an app, we can import them into our
blueprints and models without causing circular import errors.
"""
db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()