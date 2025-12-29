"""
Vercel Serverless Entry Point for LinkFarm Backend

This file exports the Flask application for Vercel's serverless platform.
Vercel will automatically detect and deploy this as a serverless function.

The Flask app factory pattern (create_app) makes this very simple -
we just import and call it, then Vercel handles the rest.
"""

from app import create_app

# Create the Flask application using the factory pattern
# Vercel will use this 'app' variable as the WSGI application
app = create_app('production')

# Vercel handles routing, scaling, and everything else.
