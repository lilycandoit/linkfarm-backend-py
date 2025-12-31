"""
AI-Powered Features for LinkFarm

This module provides AI assistance for farmers using Google Gemini.
Features include:
- Product description generation
- Future: Image analysis, pricing suggestions
"""

import os
import json
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import google.generativeai as genai
from PIL import Image
import requests
from io import BytesIO

ai_bp = Blueprint('ai', __name__)

def get_gemini_model(vision=False):
    """
    Initialize and return Gemini model.
    Uses API key from environment variable.

    Args:
        vision (bool): If True, return vision-capable model for image analysis
    """
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    genai.configure(api_key=api_key)
    # Use Gemini 2.5 Flash - latest stable multimodal model
    # Supports both text and vision in a single model
    # Free tier: 15 requests/min, 1,500 requests/day
    return genai.GenerativeModel('models/gemini-2.5-flash')

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
        # Check for rate limit errors
        error_str = str(e)
        current_app.logger.error(f'Error generating description: {error_str}')

        if '429' in error_str or 'quota' in error_str.lower() or 'rate limit' in error_str.lower():
            return jsonify({
                'error': 'Rate Limit',
                'message': 'AI service temporarily unavailable due to high usage. Please try again in a few moments.'
            }), 429

        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Failed to generate description. Please try again.'
        }), 500


@ai_bp.route('/analyze-image', methods=['POST'])
@jwt_required()
def analyze_image():
    """
    Analyze a product image using AI vision to extract:
    - Product name
    - Product category
    - Suggested pricing
    - Marketing description

    Expected JSON:
    {
        "image_url": "https://res.cloudinary.com/..."
    }

    Returns:
    {
        "name": "Dragon Fruit",
        "category": "Fruits",
        "suggested_price": "5.99",
        "description": "Fresh, vibrant dragon fruit...",
        "confidence": "high"
    }
    """
    data = request.get_json()

    if not data or 'image_url' not in data:
        return jsonify({
            'error': 'Bad Request',
            'message': 'image_url is required'
        }), 400

    image_url = data['image_url']

    try:
        # Download the image from URL
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))

        # Construct the analysis prompt
        prompt = """You are an agricultural product expert helping farmers list their produce online.

Analyze this product image and provide:
1. Product name (e.g., "Dragon Fruit", "Organic Tomatoes")
2. Product category (choose ONE from: Fruits, Vegetables, Grains, Dairy, Meat, Other)
3. Suggested price per kg in USD (just the number, e.g., "5.99")
4. Marketing description (2-3 sentences focusing on freshness, quality, and appeal to customers)

Respond ONLY with valid JSON in this exact format:
{
    "name": "Dragon Fruit",
    "category": "Fruits",
    "suggested_price": "5.99",
    "description": "Fresh, vibrant dragon fruit harvested at peak ripeness. Sweet and juicy with striking pink skin and white flesh. Perfect for smoothies, fruit salads, or enjoying fresh.",
    "confidence": "high"
}

Use "high" confidence if you're certain, "medium" if somewhat uncertain, "low" if the image is unclear."""

        # Use vision model to analyze
        model = get_gemini_model(vision=True)
        vision_response = model.generate_content([prompt, img])

        # Parse the JSON response
        response_text = vision_response.text.strip()

        # Extract JSON from markdown code blocks if present
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()

        analysis = json.loads(response_text)

        return jsonify({
            'analysis': analysis,
            'message': 'Image analyzed successfully'
        }), 200

    except requests.exceptions.RequestException as re:
        current_app.logger.error(f'Error downloading image: {str(re)}')
        return jsonify({
            'error': 'Bad Request',
            'message': 'Failed to download image from URL. Please check the URL.'
        }), 400

    except ValueError as ve:
        # API key not configured
        current_app.logger.error(f'Gemini API key error: {str(ve)}')
        return jsonify({
            'error': 'Configuration Error',
            'message': 'AI service is not configured. Please contact support.'
        }), 500

    except json.JSONDecodeError as je:
        current_app.logger.error(f'Failed to parse AI response: {str(je)}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'AI returned invalid response. Please try again.'
        }), 500

    except Exception as e:
        # Check for rate limit errors
        error_str = str(e)
        current_app.logger.error(f'Error analyzing image: {error_str}')

        if '429' in error_str or 'quota' in error_str.lower() or 'rate limit' in error_str.lower():
            return jsonify({
                'error': 'Rate Limit',
                'message': 'AI service temporarily unavailable due to high usage. Please try again in a few moments.'
            }), 429

        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Failed to analyze image. Please try again.'
        }), 500
