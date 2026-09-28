import json

from google import genai
from google.genai import types

from .config import settings
from .schemas import ComicOutline


FALLBACK_FLASH_MODEL = "gemini-3.5-flash"


def generate_comic_outline(
    prompt: str
) -> ComicOutline:

    if not settings.GEMINI_API_KEY:
        return create_demo_outline(prompt)

    client = genai.Client(
        api_key=settings.GEMINI_API_KEY
    )

    models_to_try = [
        settings.GEMINI_FLASH_MODEL,
        FALLBACK_FLASH_MODEL,
    ]

    for model_name in models_to_try:

        try:

            response = client.models.generate_content(
                model=model_name,

                contents=f"""
You are a professional comic story planner.

Create a complete and engaging comic story
from the following idea:

{prompt}

IMPORTANT:

Create EXACTLY {settings.PANEL_COUNT} panels.

Every panel must be unique.

The story must progress naturally from
Panel 1 to Panel {settings.PANEL_COUNT}.

Do not repeat scenes.

Do not repeat visual prompts.

For every panel provide:

- panel_number
- scene_description
- visual_prompt

Also provide:

- title
- theme

Requirements:

- Keep panel numbers from 1 to {settings.PANEL_COUNT}.
- Every panel must show a different moment.
- Continue the story naturally.
- Include different locations, actions,
  expressions, or camera views when appropriate.
- Create detailed visual prompts.
- Use original characters only.
- Do not use copyrighted characters.
- Do not include text, speech bubbles,
  captions, logos, or watermarks inside
  the generated artwork.
- Make the visual prompts suitable for
  AI image generation.
- Return only valid JSON.
""",

                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ComicOutline,
                ),
            )

            data = response.parsed

            if isinstance(
                data,
                ComicOutline
            ):
                return data

            if isinstance(
                data,
                dict
            ):
                return ComicOutline.model_validate(
                    data
                )

            return ComicOutline.model_validate(
                json.loads(response.text)
            )

        except Exception as error:

            error_text = str(error)

            print(
                f"Gemini Flash model "
                f"{model_name} failed: "
                f"{error}"
            )

            if "429" in error_text:

                print(
                    "Gemini API quota is exhausted."
                )

                break

            if "503" in error_text:

                print(
                    "Gemini service is temporarily "
                    "unavailable."
                )

                continue

            continue

    print(
        "Gemini Flash unavailable."
    )

    print(
        "Using ComicCraft 10-panel "
        "demo outline fallback."
    )

    return create_demo_outline(prompt)


def create_demo_outline(
    prompt: str
) -> ComicOutline:

    scenes = [

        "The main character discovers a mysterious glowing clue inside a quiet room.",

        "The character follows the clue through a colorful hallway toward an unknown destination.",

        "The character enters an unusual laboratory and discovers a strange hidden machine.",

        "The machine suddenly activates and projects a mysterious map into the air.",

        "The character follows the map outside and reaches an abandoned building.",

        "Inside the building, the character discovers a secret room filled with glowing objects.",

        "A surprising message appears and reveals the reason behind the mysterious events.",

        "The character must make an important decision while the environment changes around them.",

        "The character solves the mystery by connecting the clues and successfully completes the challenge.",

        "The adventure ends peacefully, but a new mysterious clue appears for the next adventure.",
    ]

    panels = []

    panel_count = settings.PANEL_COUNT

    for index in range(panel_count):

        panel_number = index + 1

        scene_index = min(
            index,
            len(scenes) - 1
        )

        scene = scenes[scene_index]

        panels.append(
            {
                "panel_number":
                    panel_number,

                "scene_description":
                    scene,

                "visual_prompt":
                    (
                        "Professional original comic "
                        "illustration with original "
                        "characters, cinematic lighting, "
                        "expressive faces, detailed "
                        "environment, dynamic composition, "
                        f"different scene for panel "
                        f"{panel_number} of "
                        f"{panel_count}. "
                        f"Scene: {scene} "
                        f"Story idea: {prompt}. "
                        "No text, no speech bubbles, "
                        "no captions, no logos, "
                        "no watermark."
                    ),
            }
        )

    return ComicOutline(
        title="ComicCraft Demo Story",
        theme="Adventure",
        panels=panels,
    )