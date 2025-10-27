# application.py - Entry point for AWS Elastic Beanstalk

# import os
from app import create_app

# Create Flask app instance
application = create_app()

if __name__ == "__main__":
    # For local testing
    application.run(host='0.0.0.0', port=8000)
