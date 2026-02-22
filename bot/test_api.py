import os
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key found: {bool(api_key)}")
print(f"API Key: {api_key[:10]}...{api_key[-5:]}" if api_key else "No key")

genai.configure(api_key=api_key)

print("\nListing models...")
try:
    models = list(genai.list_models())
    print(f"Found {len(models)} models")
    for m in models[:5]:
        print(f"  - {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")

print("\nTesting generation...")
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello")
    print(f"Response: {response.text[:100] if response.text else 'No text'}")
except Exception as e:
    print(f"Error: {e}")