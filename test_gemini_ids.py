import os
from google import genai
from google.genai import types

# Simulated environment
api_key = "REPLACED_BY_ACTUAL_KEY" # I'll grab it from settings

def test_model(model_name):
    print(f"Testing {model_name}...")
    try:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"), http_options={'api_version': 'v1'})
        response = client.models.generate_content(
            model=model_name,
            contents="Say 'Ping'"
        )
        print(f" - SUCCESS: {response.text.strip()}")
        return True
    except Exception as e:
        print(f" - FAILED: {e}")
        return False

if __name__ == "__main__":
    # In a real run, I'll use the API key from settings
    models = ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-2.0-flash", "gemini-2.0-flash-lite-preview-02-05"]
    for m in models:
        test_model(m)
