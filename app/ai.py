import google.generativeai as genai
from config.settings import config

# Configure Google AI
api_key = config["GOOGLE_AI_API_KEY"]
if not api_key:
    print("GOOGLE_AI_API_KEY not found in environment variables")
    model = None
else:
    try:
        genai.configure(api_key=api_key)
        
        # Try different model names that are currently available
        model_names = [
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-1.0-pro'
        ]
        
        model = None
        for model_name in model_names:
            try:
                test_model = genai.GenerativeModel(model_name)
                test_response = test_model.generate_content("Hello")
                print(f"Success with {model_name}: {test_response.text[:50]}...")
                model = test_model
                break
            except Exception as e:
                print(f"Model {model_name} failed: {e}")
                continue
        
        if model:
            print("Google AI configured successfully")
        else:
            print("All model attempts failed")
    except Exception as e:
        print(f"Error configuring Google AI: {e}")
        model = None
