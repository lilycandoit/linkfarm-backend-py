# config.py - Database configuration and settings
import os
from dotenv import load_dotenv

# Load environment variables from .env file
# This must be called before accessing os.getenv()
load_dotenv()

class Config:
    """
    Base configuration class
    Contains all the settings for our Flask application
    """

    # Database connection string
    # Gets the DATABASE_URL from environment variables
    # Format: postgresql://username:password@host:port/database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

    # Disable SQLAlchemy event system (saves memory)
    # Flask-SQLAlchemy recommendation for better performance
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secret key for session security (from environment variables)
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')

    # Enable/disable debug mode based on environment
    DEBUG = os.getenv('FLASK_ENV') == 'development'

    # CORS settings - Get the allowed origin from the environment variable.
    # This makes the configuration cleaner and avoids hardcoded values.
    CORS_ORIGINS = [os.getenv('FRONTEND_URL', 'http://localhost:5173')]

class DevelopmentConfig(Config):
    """
    Development environment configuration
    Inherits from base Config class
    """
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Print all SQL queries (helpful for learning!)

class TestingConfig(Config):
    """
    Testing environment configuration
    """
    TESTING = True
    DEBUG = True
    # Use an in-memory SQLite database for tests for speed and isolation
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ECHO = False # Keep test output clean

class ProductionConfig(Config):
    """
    Production environment configuration
    More secure settings for deployment
    """
    DEBUG = False
    SQLALCHEMY_ECHO = False  # Don't print SQL queries in production

# Dictionary to easily switch between configurations
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}