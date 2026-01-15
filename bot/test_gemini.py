import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import google.generativeai as genai

async def test_gemini():
    api_key = os.getenv('GEMINI_API_KEY')
    print(f"API Key: {api_key[:20]}..." if api_key else "API Key not found!")
    
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set")
        return
    
    try:
        genai.configure(api_key=api_key)
        
        # List available models
        print("\n=== Available Models ===")
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"  - {model.name}")
        
        # Test with gemini-1.5-flash
        print("\n=== Testing gemini-1.5-flash ===")
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content("Say hello in Japanese")
        print(f"Response: {response.text}")
        print("\n✅ Gemini API is working!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gemini())