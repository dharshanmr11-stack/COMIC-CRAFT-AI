from pathlib import Path
import math
import textwrap

from huggingface_hub import InferenceClient
from PIL import Image, ImageDraw, ImageFont

from .config import PANELS_DIR, settings


def get_font(
    size: int,
    bold: bool = False,
):
    paths = (
        [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
        ]
        if bold
        else [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
        ]
    )

    for font_path in paths:

        path = Path(font_path)

        if path.exists():

            return ImageFont.truetype(
                str(path),
                size,
            )

    return ImageFont.load_default()


def prepare_dialogue_text(
    text: str,
    max_chars: int = 30,
):

    text = str(text).strip()

    if not text:
        return ""

    lines = textwrap.wrap(
        text,
        width=max_chars,
        break_long_words=False,
        break_on_hyphens=False,
    )

    return "\n".join(
        lines[:3]
    )


def calculate_bubble_size(
    draw: ImageDraw.ImageDraw,
    text: str,
    font,
):

    bbox = draw.multiline_textbbox(
        (0, 0),
        text,
        font=font,
        spacing=5,
        align="center",
    )

    text_width = (
        bbox[2] - bbox[0]
    )

    text_height = (
        bbox[3] - bbox[1]
    )

    padding_x = 20
    padding_y = 12

    box_width = (
        text_width
        + padding_x * 2
    )

    box_height = (
        text_height
        + padding_y * 2
    )

    box_width = max(
        box_width,
        150,
    )

    box_height = max(
        box_height,
        60,
    )

    box_width = min(
        box_width,
        420,
    )

    box_height = min(
        box_height,
        180,
    )

    return (
        box_width,
        box_height,
        text_width,
        text_height,
    )


def draw_rounded_speech_bubble(
    draw,
    box,
    text,
    font,
    tail_x,
):

    left, top, right, bottom = box

    draw.rounded_rectangle(
        box,
        radius=22,
        fill="white",
        outline="#20243a",
        width=4,
    )

    tail = [
        (
            tail_x - 15,
            bottom - 2,
        ),
        (
            tail_x,
            bottom + 28,
        ),
        (
            tail_x + 15,
            bottom - 2,
        ),
    ]

    draw.polygon(
        tail,
        fill="white",
    )

    draw.line(
        tail,
        fill="#20243a",
        width=3,
    )

    bbox = draw.multiline_textbbox(
        (0, 0),
        text,
        font=font,
        spacing=5,
        align="center",
    )

    text_width = (
        bbox[2] - bbox[0]
    )

    text_height = (
        bbox[3] - bbox[1]
    )

    text_x = (
        (left + right - text_width)
        / 2
    )

    text_y = (
        (top + bottom - text_height)
        / 2
    )

    draw.multiline_text(
        (
            text_x,
            text_y,
        ),
        text,
        font=font,
        fill="#20243a",
        spacing=5,
        align="center",
    )


def draw_rectangle_speech_bubble(
    draw,
    box,
    text,
    font,
    tail_x,
):

    left, top, right, bottom = box

    draw.rounded_rectangle(
        box,
        radius=8,
        fill="#fffdf7",
        outline="#20243a",
        width=4,
    )

    tail = [
        (
            tail_x - 14,
            bottom - 2,
        ),
        (
            tail_x,
            bottom + 25,
        ),
        (
            tail_x + 14,
            bottom - 2,
        ),
    ]

    draw.polygon(
        tail,
        fill="#fffdf7",
    )

    draw.line(
        tail,
        fill="#20243a",
        width=3,
    )

    bbox = draw.multiline_textbbox(
        (0, 0),
        text,
        font=font,
        spacing=5,
        align="center",
    )

    text_width = (
        bbox[2] - bbox[0]
    )

    text_height = (
        bbox[3] - bbox[1]
    )

    text_x = (
        (left + right - text_width)
        / 2
    )

    text_y = (
        (top + bottom - text_height)
        / 2
    )

    draw.multiline_text(
        (
            text_x,
            text_y,
        ),
        text,
        font=font,
        fill="#20243a",
        spacing=5,
        align="center",
    )


def draw_cloud_bubble(
    draw,
    box,
    text,
    font,
    tail_x,
):

    left, top, right, bottom = box

    draw.rounded_rectangle(
        box,
        radius=28,
        fill="white",
        outline="#20243a",
        width=4,
    )

    circles = [
        (
            left + 5,
            top + 12,
            left + 45,
            top + 52,
        ),
        (
            right - 48,
            top + 8,
            right - 8,
            top + 48,
        ),
    ]

    for circle in circles:

        draw.ellipse(
            circle,
            fill="white",
            outline="#20243a",
            width=3,
        )

    draw.ellipse(
        (
            tail_x - 15,
            bottom + 5,
            tail_x + 12,
            bottom + 32,
        ),
        fill="white",
        outline="#20243a",
        width=3,
    )

    bbox = draw.multiline_textbbox(
        (0, 0),
        text,
        font=font,
        spacing=5,
        align="center",
    )

    text_width = (
        bbox[2] - bbox[0]
    )

    text_height = (
        bbox[3] - bbox[1]
    )

    text_x = (
        (left + right - text_width)
        / 2
    )

    text_y = (
        (top + bottom - text_height)
        / 2
    )

    draw.multiline_text(
        (
            text_x,
            text_y,
        ),
        text,
        font=font,
        fill="#20243a",
        spacing=5,
        align="center",
    )


def draw_burst_bubble(
    draw,
    box,
    text,
    font,
    tail_x,
):

    left, top, right, bottom = box

    center_x = (
        left + right
    ) / 2

    center_y = (
        top + bottom
    ) / 2

    radius_x = (
        right - left
    ) / 2

    radius_y = (
        bottom - top
    ) / 2

    points = []

    for index in range(24):

        angle = (
            index
            * math.pi
            / 12
        )

        if index % 2 == 0:

            current_x = radius_x
            current_y = radius_y

        else:

            current_x = radius_x * 0.82
            current_y = radius_y * 0.82

        x = (
            center_x
            + current_x
            * math.cos(angle)
        )

        y = (
            center_y
            + current_y
            * math.sin(angle)
        )

        points.append(
            (
                x,
                y,
            )
        )

    draw.polygon(
        points,
        fill="white",
        outline="#20243a",
    )

    draw.polygon(
        [
            (
                tail_x - 13,
                bottom - 2,
            ),
            (
                tail_x,
                bottom + 25,
            ),
            (
                tail_x + 13,
                bottom - 2,
            ),
        ],
        fill="white",
        outline="#20243a",
    )

    bbox = draw.multiline_textbbox(
        (0, 0),
        text,
        font=font,
        spacing=5,
        align="center",
    )

    text_width = (
        bbox[2] - bbox[0]
    )

    text_height = (
        bbox[3] - bbox[1]
    )

    text_x = (
        center_x
        - text_width / 2
    )

    text_y = (
        center_y
        - text_height / 2
    )

    draw.multiline_text(
        (
            text_x,
            text_y,
        ),
        text,
        font=font,
        fill="#20243a",
        spacing=5,
        align="center",
    )


def add_dialogue_boxes(
    image: Image.Image,
    dialogues,
    panel_number: int,
):

    if not dialogues:
        return image

    draw = ImageDraw.Draw(
        image
    )

    width, height = image.size

    # -----------------------------------------
    # NORMALIZE DIALOGUES
    # -----------------------------------------

    normalized = []

    for dialogue in dialogues:

        if isinstance(
            dialogue,
            dict,
        ):

            speaker = str(
                dialogue.get(
                    "speaker",
                    "Speaker",
                )
            )

            text = str(
                dialogue.get(
                    "text",
                    "",
                )
            )

        else:

            speaker = "Speaker"

            text = str(
                dialogue
            )

        text = text.strip()

        if text:

            normalized.append(
                {
                    "speaker":
                        speaker,

                    "text":
                        text,
                }
            )

    if not normalized:
        return image

    # Maximum two visible bubbles.
    normalized = normalized[:2]

    font = get_font(
        24,
        bold=True,
    )

    # -----------------------------------------
    # POSITION SYSTEM
    # -----------------------------------------

    if len(normalized) == 1:

        positions = [
            {
                "x_ratio": 0.50,
                "y": 95,
                "side": "center",
            }
        ]

    else:

        positions = [
            {
                "x_ratio": 0.30,
                "y": 80,
                "side": "left",
            },
            {
                "x_ratio": 0.70,
                "y": 220,
                "side": "right",
            },
        ]

    # -----------------------------------------
    # DRAW EACH SPEAKER SEPARATELY
    # -----------------------------------------

    for index, dialogue in enumerate(
        normalized
    ):

        text = prepare_dialogue_text(
            dialogue["text"],
            max_chars=27,
        )

        if not text:
            continue

        (
            box_width,
            box_height,
            _,
            _,
        ) = calculate_bubble_size(
            draw,
            text,
            font,
        )

        position = positions[
            index
        ]

        center_x = int(
            width
            * position["x_ratio"]
        )

        box_left = int(
            center_x
            - box_width / 2
        )

        box_top = int(
            position["y"]
        )

        box_right = int(
            box_left
            + box_width
        )

        box_bottom = int(
            box_top
            + box_height
        )

        # -------------------------------------
        # KEEP INSIDE IMAGE
        # -------------------------------------

        if box_left < 20:

            shift = (
                20
                - box_left
            )

            box_left += shift
            box_right += shift

        if box_right > width - 20:

            shift = (
                box_right
                - (width - 20)
            )

            box_left -= shift
            box_right -= shift

        if box_top < 20:

            box_top = 20

            box_bottom = int(
                box_top
                + box_height
            )

        if box_bottom > height - 40:

            box_bottom = (
                height - 40
            )

            box_top = int(
                box_bottom
                - box_height
            )

        box = (
            box_left,
            box_top,
            box_right,
            box_bottom,
        )

        # -------------------------------------
        # DIFFERENT BUBBLE TYPE
        # -------------------------------------

        style = index % 4

        tail_x = int(
            (
                box_left
                + box_right
            ) / 2
        )

        if style == 0:

            draw_rounded_speech_bubble(
                draw,
                box,
                text,
                font,
                tail_x,
            )

        elif style == 1:

            draw_rectangle_speech_bubble(
                draw,
                box,
                text,
                font,
                tail_x,
            )

        elif style == 2:

            draw_cloud_bubble(
                draw,
                box,
                text,
                font,
                tail_x,
            )

        else:

            draw_burst_bubble(
                draw,
                box,
                text,
                font,
                tail_x,
            )

    return image


def generate_panel_image(
    visual_prompt: str,
    panel_number: int,
    dialogues=None,
) -> str:

    PANELS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        PANELS_DIR
        / f"panel_{panel_number}.png"
    )

    # -----------------------------------------
    # CHECK HUGGING FACE TOKEN
    # -----------------------------------------

    if not settings.HF_TOKEN:

        raise RuntimeError(
            "HF_TOKEN is missing. "
            "Please add your Hugging Face "
            "token to the .env file."
        )

    # -----------------------------------------
    # AI IMAGE CLIENT
    # -----------------------------------------

    client = InferenceClient(
        provider=settings.IMAGE_PROVIDER,
        api_key=settings.HF_TOKEN,
    )

    # -----------------------------------------
    # AI CARTOON PROMPT
    # -----------------------------------------

    prompt = f"""
Create a professional original 2D animated
comic-book illustration.

VISUAL STYLE:
- High-quality cartoon animation
- Clean bold outlines
- Vibrant cinematic colors
- Expressive original characters
- Detailed environment
- Professional digital illustration
- Dynamic comic composition
- Cinematic lighting
- Strong facial expressions
- Clear foreground and background

CHARACTERS:
- Create completely original characters.
- Keep character appearance consistent.
- If two characters are present, clearly separate
  them visually.
- Give each character a distinct position.
- Do not copy famous cartoon characters.
- Do not use copyrighted characters.

PANEL:
Panel {panel_number} of 10.

SCENE:
{visual_prompt}

IMPORTANT:
- Do not generate any text.
- Do not generate speech bubbles.
- Do not generate captions.
- Do not generate logos.
- Do not generate watermarks.

ComicCraft will add the dialogue bubbles
after the AI image is generated.
"""

    try:

        print(
            f"Generating AI cartoon "
            f"panel {panel_number}/10..."
        )

        image = client.text_to_image(
            prompt=prompt,
            model=settings.IMAGE_MODEL,
        )

        # -----------------------------------------
        # ADD SEPARATE DIALOGUE BUBBLES
        # -----------------------------------------

        image = add_dialogue_boxes(
            image,
            dialogues,
            panel_number,
        )

        # -----------------------------------------
        # SAVE IMAGE
        # -----------------------------------------

        image.save(
            output_path,
            format="PNG",
        )

        print(
            f"Panel {panel_number} "
            f"created successfully."
        )

        return str(output_path)

    except Exception as error:

        print(
            f"Panel {panel_number} "
            f"generation failed: "
            f"{error}"
        )

        raise RuntimeError(
            "AI comic image generation failed."
        ) from error