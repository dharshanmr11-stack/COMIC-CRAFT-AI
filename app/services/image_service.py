import os
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load .env file
load_dotenv()

# Hugging Face token
HF_TOKEN = os.getenv("HF_TOKEN")

# Image model
IMAGE_MODEL = os.getenv(
    "IMAGE_MODEL",
    "black-forest-labs/FLUX.1-schnell"
)

# Image provider
IMAGE_PROVIDER = os.getenv(
    "IMAGE_PROVIDER",
    "auto"
)

# Create Hugging Face client
if not HF_TOKEN:
    raise ValueError("HF_TOKEN is missing in .env file")

client = InferenceClient(
    provider=IMAGE_PROVIDER,
    api_key=HF_TOKEN
)


def generate_image(
    prompt: str,
    output_path: str = "static/exports/comic_panel.png"
) -> str:
    """
    Generate a comic panel image using Hugging Face.
    """

    if not prompt or not prompt.strip():
        raise ValueError("Image prompt cannot be empty")

    # Generate image
    image = client.text_to_image(
        prompt=prompt,
        model=IMAGE_MODEL
    )

    # Create output directory
    output_file = Path(output_path)
    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save image
    image.save(output_file)

    return str(output_file)


def generate_comic_panel(
    scene_description: str,
    panel_number: int
) -> str:
    """
    Generate one comic panel from a scene description.
    """

    prompt = f"""
Create a professional comic book panel.

Panel number: {panel_number}

Scene:
{scene_description}

Style requirements:
- colorful comic book illustration
- clean line art
- expressive characters
- cinematic composition
- detailed background
- consistent visual style
- dramatic but family-friendly
- no text or speech bubbles inside the image
"""

    output_path = (
        f"static/exports/"
        f"comic_panel_{panel_number}.png"
    )

    return generate_image(
        prompt=prompt,
        output_path=output_path
    )