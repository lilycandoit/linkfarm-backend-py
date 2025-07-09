import os
from dotenv import load_dotenv

# Load environment variables from the .env file.
# This makes it easy to manage configuration for different environments.
load_dotenv()

class Config:
    """
    Base configuration class. Contains default settings and settings
    loaded from environment variables that are common to all environments.
    """
    # --- Critical Application Secrets ---
    # These are loaded from the .env file. The application will not start
    # if these are not set, which is a crucial security measure.
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('SECRET_KEY') # flask-jwt-extended uses this

    # --- Database Configuration ---
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- CORS Configuration ---
    CORS_ORIGINS = os.getenv('FRONTEND_URL')

    def __init__(self):
        """
        Validates that essential environment variables are loaded.
        The application will refuse to start if they are missing.
        """
        if not self.SECRET_KEY or not self.SQLALCHEMY_DATABASE_URI or not self.CORS_ORIGINS:
            raise ValueError("One or more required environment variables (SECRET_KEY, DATABASE_URL, FRONTEND_URL) are not set in your .env file.")

class DevelopmentConfig(Config):
    """
    Configuration for the development environment.
    Enables debug mode and other development-friendly features.
    """
    ENV = 'development'
    DEBUG = True
    # Print all executed SQL queries to the console for easy debugging.
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    """
    Configuration for running automated tests.
    """
    ENV = 'testing'
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Use in-memory DB for tests
    SECRET_KEY = 'test-secret-key' # Use a separate key for testing
    JWT_SECRET_KEY = 'test-secret-key'

class ProductionConfig(Config):
    """Configuration for the live production environment."""
    ENV = 'production'
    DEBUG = False
    SQLALCHEMY_ECHO = False

# A dictionary to easily switch between configurations in the app factory.
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}