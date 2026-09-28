import os
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env
load_dotenv()

# Get Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

# Check API key
if not api_key:
    print("❌ GEMINI_API_KEY not found in .env file")
    exit()

# Create Gemini client
client = genai.Client(api_key=api_key)

# Send a test request to Gemini
response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="Write one short sentence about a comic story."
)

# Display result
print("\n✅ Gemini API is working!\n")
print(response.text)