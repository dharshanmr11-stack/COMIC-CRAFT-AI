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

Do not create extra panels.

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
- Give each panel a different action,
  location, expression, or camera view
  when appropriate.
- Create detailed visual prompts.
- Use original characters only.
- Do not use copyrighted characters.
- Do not include text, speech bubbles,
  captions, logos, or watermarks inside
  the generated artwork.
- Leave clear visual space around the
  characters for ComicCraft dialogue bubbles.
- Make the visual prompts suitable for
  AI image generation.
- Return exactly {settings.PANEL_COUNT}
  panel objects.
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

                # Keep exactly the requested number.
                data.panels = data.panels[
                    :settings.PANEL_COUNT
                ]

                return data

            if isinstance(
                data,
                dict
            ):

                outline = ComicOutline.model_validate(
                    data
                )

                outline.panels = outline.panels[
                    :settings.PANEL_COUNT
                ]

                return outline

            outline = ComicOutline.model_validate(
                json.loads(response.text)
            )

            outline.panels = outline.panels[
                :settings.PANEL_COUNT
            ]

            return outline

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
        f"Using ComicCraft "
        f"{settings.PANEL_COUNT}-panel "
        "demo outline fallback."
    )

    return create_demo_outline(prompt)


def create_demo_outline(
    prompt: str
) -> ComicOutline:

    # -----------------------------------------
    # EXACTLY 5 UNIQUE SCENES
    # -----------------------------------------

    scenes = [

        (
            "Panel 1: The young student discovers "
            "a mysterious glowing robot inside "
            "a quiet college laboratory."
        ),

        (
            "Panel 2: The student follows the "
            "robot's glowing signal through a "
            "colorful college hallway and discovers "
            "a hidden laboratory door."
        ),

        (
            "Panel 3: Inside the secret laboratory, "
            "the robot activates a mysterious map "
            "and reveals the secret behind the clue."
        ),

        (
            "Panel 4: The student and the robot "
            "work together to solve the mystery "
            "while the laboratory fills with "
            "glowing lights."
        ),

        (
            "Panel 5: The mystery is solved, the "
            "student celebrates with the robot, "
            "but a new glowing clue appears "
            "hinting at another adventure."
        ),
    ]

    panels = []

    panel_count = settings.PANEL_COUNT

    # Safety: always use the first 5 scenes.
    scenes = scenes[:panel_count]

    for index, scene in enumerate(scenes):

        panel_number = index + 1

        visual_prompt = (
            "Professional original 2D animated "
            "comic-book illustration. "
            "High-quality colorful cartoon style, "
            "clean bold outlines, cinematic lighting, "
            "expressive original characters, "
            "detailed environment, dynamic composition. "
            "Keep the main student and original robot "
            "visually consistent across all panels. "
            f"This is panel {panel_number} of "
            f"{panel_count}. "
            f"Scene: {scene} "
            f"Story idea: {prompt}. "
            "Place characters clearly in the scene "
            "and leave some clean space around them "
            "for ComicCraft dialogue bubbles. "
            "Do not create text. "
            "Do not create speech bubbles. "
            "Do not create captions. "
            "Do not create logos. "
            "Do not create watermarks. "
            "Use original characters only."
        )

        panels.append(
            {
                "panel_number": panel_number,

                "scene_description": scene,

                "visual_prompt": visual_prompt,
            }
        )

    return ComicOutline(
        title="ComicCraft Adventure",
        theme="Mystery Adventure",
        panels=panels,
    )