import json

from google import genai
from google.genai import types

from .config import settings
from .schemas import ComicOutline, ComicStory


def generate_comic_story(
    outline: ComicOutline,
) -> ComicStory:

    # -----------------------------------------
    # USE LOCAL FALLBACK IF API KEY IS MISSING
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

- Create exactly one story entry for every panel.
- Keep every panel_number unchanged.
- Give every panel unique narration.
- Give every panel natural dialogue.
- A panel may have one or two speakers.
- When two characters are present, create two separate
  dialogue lines whenever it makes sense.
- Each dialogue line must have a clear speaker name.
- Never combine two speakers into one dialogue string.
- Keep each dialogue line short and natural.
- Do not repeat narration.
- Do not repeat dialogue.
- Continue the story naturally from panel to panel.
- Make the final panel feel like a satisfying ending.
- Use original character names.
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
        "text": "This cable must land smoothly."
    }},
    {{
        "speaker": "Maya",
        "text": "I think I understand the mystery now."
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
            return data

        if isinstance(
            data,
            dict
        ):
            return ComicStory.model_validate(
                data
            )

        return ComicStory.model_validate(
            json.loads(response.text)
        )

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

    narrations = [
        "The adventure begins as a mysterious clue appears.",
        "The heroes follow the clue into an unknown place.",
        "A hidden discovery changes their entire plan.",
        "The heroes work together to solve the difficult challenge.",
        "The mystery becomes clearer as they find another clue.",
        "A strange signal leads them deeper into the adventure.",
        "The heroes finally discover who created the mystery.",
        "They must make one important decision before moving forward.",
        "The final challenge is solved through teamwork.",
        "The adventure ends with a new mystery waiting to be discovered.",
    ]

    dialogue_sets = [
        [
            {
                "speaker": "Arun",
                "text": "Something strange is happening here!"
            }
        ],

        [
            {
                "speaker": "Arun",
                "text": "This clue must lead somewhere."
            },
            {
                "speaker": "Maya",
                "text": "Then let's follow it carefully."
            }
        ],

        [
            {
                "speaker": "Maya",
                "text": "I can't believe what we found!"
            }
        ],

        [
            {
                "speaker": "Arun",
                "text": "We need to solve this together."
            },
            {
                "speaker": "Maya",
                "text": "Look! The answer is right there."
            }
        ],

        [
            {
                "speaker": "Arun",
                "text": "There is another clue!"
            }
        ],

        [
            {
                "speaker": "Maya",
                "text": "Did you hear that signal?"
            },
            {
                "speaker": "Arun",
                "text": "Yes. It is coming from ahead."
            }
        ],

        [
            {
                "speaker": "Arun",
                "text": "Now we know who started this."
            }
        ],

        [
            {
                "speaker": "Maya",
                "text": "We have to choose our next step."
            },
            {
                "speaker": "Arun",
                "text": "Let's trust what we discovered."
            }
        ],

        [
            {
                "speaker": "Arun",
                "text": "We did it!"
            },
            {
                "speaker": "Maya",
                "text": "Teamwork solved the mystery."
            }
        ],

        [
            {
                "speaker": "Maya",
                "text": "This adventure is finally over."
            },
            {
                "speaker": "Arun",
                "text": "Maybe... but another mystery is waiting."
            }
        ],
    ]

    panels = []

    for index, panel in enumerate(
        outline.panels
    ):

        story_index = min(
            index,
            len(narrations) - 1
        )

        panels.append(
            {
                "panel_number":
                    panel.panel_number,

                "narration":
                    narrations[story_index],

                "dialogues":
                    dialogue_sets[story_index],
            }
        )

    return ComicStory(
        title=outline.title,
        panels=panels,
    )