"""
Configuration Module for LinkFarm API

Defines configuration classes for different environments:
- DevelopmentConfig: Local development with debug enabled
- TestingConfig: Automated testing with in-memory database
- ProductionConfig: Live production environment with security hardened

All configs require environment variables to be set in .env file.
See README.md for required environment variables.
"""

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
    # Ensure compatibility with modern SQLAlchemy which prefers 'postgresql://'
    db_url = os.getenv('DATABASE_URL', '')
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Serverless Database Connection Pooling ---
    # Critical for Vercel serverless functions to avoid "too many connections"
    # Each serverless function invocation is short-lived, so we use minimal pooling
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 1,           # Minimum connections per function instance
        "max_overflow": 0,        # No overflow connections (stay within limits)
        "pool_pre_ping": True,    # Verify connection is alive before using
        "pool_recycle": 300,      # Recycle connections after 5 minutes
    }

    # --- CORS Configuration ---
    # Convert FRONTEND_URL to a list for Flask-CORS
    # Supports multiple origins separated by commas
    frontend_url = os.getenv('FRONTEND_URL', '')
    CORS_ORIGINS = [url.strip() for url in frontend_url.split(',') if url.strip()]

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

    Uses in-memory SQLite database for fast, isolated testing.
    Test database is created fresh for each test run and destroyed after.
    """
    ENV = 'testing'
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # In-memory DB - fast and isolated
    SECRET_KEY = 'test-secret-key' # Hardcoded for testing - safe since not in production
    JWT_SECRET_KEY = 'test-secret-key'
    CORS_ORIGINS = 'http://localhost:5173'  # Allow CORS in tests

    # Override PostgreSQL-specific pool settings - SQLite doesn't support these
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,  # Keep this for connection health checks
    }

class ProductionConfig(Config):
    """
    Configuration for the live production environment.

    Security features:
    - DEBUG disabled (never enable in production!)
    - SQL query logging disabled for performance
    - Requires environment variables to be set
    """
    ENV = 'production'
    DEBUG = False  # CRITICAL: Never set to True in production
    SQLALCHEMY_ECHO = False  # Disable SQL logging for performance and security

# A dictionary to easily switch between configurations in the app factory.
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}