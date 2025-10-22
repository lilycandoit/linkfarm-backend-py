"""
AI-Powered Features for LinkFarm

This module provides AI assistance for farmers using Google Gemini.
Features include:
- Product description generation
- Future: Image analysis, pricing suggestions
"""

import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import google.generativeai as genai

ai_bp = Blueprint('ai', __name__)

def get_gemini_model():
    """
    Initialize and return Gemini model.
    Uses API key from environment variable.
    """
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    genai.configure(api_key=api_key)
    # Use Gemini 2.5 Flash for fast, free responses
    return genai.GenerativeModel('gemini-2.5-flash')

@ai_bp.route('/generate-description', methods=['POST'])
@jwt_required()
def generate_description():
    """
    Generate a product description using AI.

    Expected JSON:
    {
        "product_name": "Organic Tomatoes",
        "keywords": "fresh, organic, heirloom" (optional)
    }

    Returns:
    {
        "description": "Generated marketing description..."
    }
    """
    data = request.get_json()

    if not data or 'product_name' not in data:
        return jsonify({
            'error': 'Bad Request',
            'message': 'product_name is required'
        }), 400

    product_name = data['product_name']
    keywords = data.get('keywords', '')

    try:
        # Construct the prompt for Gemini
        prompt = f"""You are a helpful assistant for farmers selling their produce online.

Generate an appealing, concise product description for a marketplace listing.

Product name: {product_name}
Additional keywords: {keywords if keywords else 'None provided'}

Requirements:
- 2-3 sentences maximum
- Focus on freshness, quality, and benefits
- Use simple, customer-friendly language
- Do not use overly flowery language
- Mention if organic/local if in keywords
- Make it appealing to health-conscious customers

Generate only the description text, nothing else."""

        model = get_gemini_model()
        response = model.generate_content(prompt)

        description = response.text.strip()

        return jsonify({
            'description': description,
            'message': 'Description generated successfully'
        }), 200

    except ValueError as ve:
        # API key not configured
        current_app.logger.error(f'Gemini API key error: {str(ve)}')
        return jsonify({
            'error': 'Configuration Error',
            'message': 'AI service is not configured. Please contact support.'
        }), 500

    except Exception as e:
        # Other errors (rate limit, network, etc.)
        current_app.logger.error(f'Error generating description: {str(e)}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Failed to generate description. Please try again.'
        }), 500
