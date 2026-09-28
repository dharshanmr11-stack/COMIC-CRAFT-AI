import os
from dotenv import load_dotenv
from google import genai

# Load .env file
load_dotenv()

# Get Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Get Gemini model from .env
GEMINI_MODEL = os.getenv(
    "GEMINI_FLASH_MODEL",
    "gemini-3.8-flash"
)

# Create Gemini client
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing in .env file")

client = genai.Client(api_key=GEMINI_API_KEY)


def generate_story(story_idea: str) -> str:
    """
    Generate a comic story using Gemini AI.
    """

    prompt = f"""
You are an expert comic book story writer.

Create a short and interesting comic story based on the following idea:

{story_idea}

The story should include:
1. A suitable title
2. Main characters
3. Story setting
4. Beginning
5. Middle
6. Ending

Write the story in a simple and creative format.
Make it suitable for generating comic panels.
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    if not response or not response.text:
        raise RuntimeError("Gemini returned an empty response")

    return response.text.strip()


def generate_panel_descriptions(story: str, panel_count: int = 5) -> list:
    """
    Convert the generated story into comic panel descriptions.
    """

    prompt = f"""
You are a professional comic storyboard writer.

Convert the following story into exactly {panel_count} comic panels.

For each panel provide:
- Panel number
- Scene description
- Characters
- Action
- Dialogue
- Image generation prompt

Story:

{story}

Return the panels in a clear numbered format.
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    if not response or not response.text:
        raise RuntimeError("Gemini returned an empty panel response")

    panels = []

    # Split the response into simple panel sections
    sections = response.text.split("Panel ")

    for section in sections:
        section = section.strip()

        if section:
            panels.append(section)

    return panels[:panel_count]


def generate_comic_content(
    story_idea: str,
    panel_count: int = 5
) -> dict:
    """
    Generate complete comic content:
    story + panel descriptions.
    """

    story = generate_story(story_idea)

    panels = generate_panel_descriptions(
        story,
        panel_count
    )

    return {
        "story": story,
        "panels": panels
    }