#!/usr/bin/env python3
"""
Check available Gemini models for your API key
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ GEMINI_API_KEY not found in .env file")
    exit(1)

print("✅ API Key found")
print(f"SDK Version: {genai.__version__}")

# Configure the API
genai.configure(api_key=api_key)

print("\n📋 Available Models:")
print("-" * 80)

try:
    # List all available models
    for model in genai.list_models():
        # Check if model supports generateContent
        if 'generateContent' in model.supported_generation_methods:
            print(f"✅ {model.name}")
            print(f"   Display Name: {model.display_name}")
            print(f"   Description: {model.description}")
            print(f"   Methods: {', '.join(model.supported_generation_methods)}")
            print()
except Exception as e:
    print(f"❌ Error listing models: {e}")
