from google import genai

client = genai.Client(api_key="YOUR_API_KEY_HERE")

print("Authorized models:")
try:
    for model in client.models.list():
        if "generateContent" in model.supported_actions:
            print(model.name)
except Exception as e:
    print(f"Error connecting to API: {e}")