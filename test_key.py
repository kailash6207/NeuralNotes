from google import genai

# Paste your newest key right here
TEST_KEY = "YOUR_API_KEY_HERE" 

try:
    print("Testing connection to Google...")
    client = genai.Client(api_key=TEST_KEY)
    response = client.models.generate_content(
        model='gemini-flash-latest', 
        contents="Say 'Hello, your key works!'"
    )
    print("\n✅ SUCCESS: The key is perfect!")
    print("Response:", response.text)
    
except Exception as e:
    print("\n❌ FAILED: Google is actively rejecting this key.")
    print("Error:", e)