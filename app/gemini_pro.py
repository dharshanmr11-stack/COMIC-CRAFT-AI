import json

from google import genai
from google.genai import types

from .config import settings
from .schemas import ComicOutline, ComicStory


def generate_comic_story(
    outline: ComicOutline,
) -> ComicStory:

    # -----------------------------------------
    # LOCAL FALLBACK IF API KEY IS MISSING
    # -----------------------------------------

    if not settings.GEMINI_API_KEY:
        return create_demo_story(outline)

    client = genai.Client(
        api_key=settings.GEMINI_API_KEY
    )

    prompt = f"""
You are a professional comic script writer.

Create a complete comic script for the following
comic outline.

COMIC OUTLINE:
{outline.model_dump_json(indent=2)}

IMPORTANT REQUIREMENTS:

- Create exactly {settings.PANEL_COUNT} story entries.
- Create exactly one story entry for every panel.
- Keep every panel_number unchanged.
- Do not create extra panels.
- Give every panel unique narration.
- Give every panel natural dialogue.
- A panel may have one or two speakers.
- When two characters are present, create two separate
  dialogue lines whenever it makes sense.
- Each dialogue line must have a clear speaker name.
- Never combine two speakers into one dialogue string.
- Keep dialogue short and natural.
- Do not repeat narration.
- Do not repeat dialogue.
- Continue the story naturally from panel to panel.
- Make the final panel feel like a satisfying ending.
- Use original character names.
- Return exactly {settings.PANEL_COUNT} panels.
- Return only valid JSON.

Required structure:

title
panels

Each panel must contain:

panel_number
narration
dialogues

Each dialogue must contain:

speaker
text

Example structure:

"dialogues": [
    {{
        "speaker": "Arun",
        "text": "We found the secret!"
    }},
    {{
        "speaker": "Maya",
        "text": "Let's see what happens next."
    }}
]

Do not put multiple speakers inside one dialogue text.
"""

    model_name = settings.GEMINI_PRO_MODEL

    try:

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ComicStory,
            ),
        )

        data = response.parsed

        if isinstance(
            data,
            ComicStory
        ):

            data.panels = data.panels[
                :settings.PANEL_COUNT
            ]

            return data

        if isinstance(
            data,
            dict
        ):

            story = ComicStory.model_validate(
                data
            )

            story.panels = story.panels[
                :settings.PANEL_COUNT
            ]

            return story

        story = ComicStory.model_validate(
            json.loads(response.text)
        )

        story.panels = story.panels[
            :settings.PANEL_COUNT
        ]

        return story

    except Exception as error:

        error_text = str(error)

        print(
            f"Comic story generation failed: "
            f"{error}"
        )

        if "429" in error_text:

            print(
                "Gemini API quota is exhausted."
            )

        elif "503" in error_text:

            print(
                "Gemini service is temporarily "
                "unavailable."
            )

        print(
            "Using ComicCraft local fallback story."
        )

        return create_demo_story(outline)


def create_demo_story(
    outline: ComicOutline,
) -> ComicStory:

    # -----------------------------------------
    # EXACTLY 5 NARRATIONS
    # -----------------------------------------

    narrations = [

        "Arun discovers a mysterious glowing robot inside the college laboratory.",

        "The robot leads Arun through a hidden hallway toward a secret room.",

        "Inside the room, the robot activates a glowing map that reveals a mystery.",

        "Arun and the robot work together to solve the mystery using the clues.",

        "The mystery is solved, but a new glowing clue appears for their next adventure.",
    ]

    # -----------------------------------------
    # EXACTLY 5 DIALOGUE SETS
    # -----------------------------------------

    dialogue_sets = [

        [
            {
                "speaker": "Arun",
                "text": "What is this mysterious robot?"
            }
        ],

        [
            {
                "speaker": "Arun",
                "text": "Where are you taking me?"
            },
            {
                "speaker": "Maya",
                "text": "Look! There is a hidden door."
            }
        ],

        [
            {
                "speaker": "Maya",
                "text": "The map is showing something!"
            },
            {
                "speaker": "Arun",
                "text": "Then this must be the secret."
            }
        ],

        [
            {
                "speaker": "Arun",
                "text": "We can solve this together."
            },
            {
                "speaker": "Maya",
                "text": "I found the final clue!"
            }
        ],

        [
            {
                "speaker": "Arun",
                "text": "We solved the mystery!"
            },
            {
                "speaker": "Maya",
                "text": "Wait... another clue just appeared."
            }
        ],
    ]

    panels = []

    # -----------------------------------------
    # CREATE ONLY THE PANELS THAT EXIST
    # -----------------------------------------

    panel_limit = min(
        len(outline.panels),
        settings.PANEL_COUNT,
        len(narrations),
        len(dialogue_sets),
    )

    for index in range(panel_limit):

        panel = outline.panels[index]

        panels.append(
            {
                "panel_number":
                    panel.panel_number,

                "narration":
                    narrations[index],

                "dialogues":
                    dialogue_sets[index],
            }
        )

    return ComicStory(
        title=outline.title,
        panels=panels,
    )