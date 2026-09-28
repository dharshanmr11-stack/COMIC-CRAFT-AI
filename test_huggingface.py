import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables
load_dotenv()

# Get Hugging Face token
hf_token = os.getenv("HF_TOKEN")

if not hf_token:
    print("❌ HF_TOKEN not found in .env file")
    exit()

# Create Hugging Face client
client = InferenceClient(
    provider="auto",
    api_key=hf_token
)

# Image generation prompt
prompt = """
A colorful comic book panel showing a young superhero
standing on a futuristic city street at sunset,
dynamic comic-book style, clean line art, dramatic lighting
"""

try:
    print("🎨 Generating comic panel...")

    image = client.text_to_image(
        prompt,
        model="black-forest-labs/FLUX.1-schnell"
    )

    # Save generated image
    image.save("test_comic_panel.png")

    print("\n✅ Hugging Face API is working!")
    print("✅ Comic panel generated successfully!")
    print("📁 Saved as: test_comic_panel.png")

except Exception as e:
    print("\n❌ Hugging Face API test failed!")
    print("Error:", e)