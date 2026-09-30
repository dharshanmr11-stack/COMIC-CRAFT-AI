from pathlib import Path
import math
import textwrap

from huggingface_hub import InferenceClient
from PIL import Image, ImageDraw, ImageFont

from .config import PANELS_DIR, settings


# ============================================================
# OpenCV
# ============================================================

try:
    import cv2

    OPENCV_AVAILABLE = True

except Exception:

    cv2 = None
    OPENCV_AVAILABLE = False


# ============================================================
# FONT
# ============================================================

def get_font(
    size: int,
    bold: bool = False,
):

    if bold:

        font_paths = [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
        ]

    else:

        font_paths = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
        ]

    for font_path in font_paths:

        path = Path(font_path)

        if path.exists():

            try:

                return ImageFont.truetype(
                    str(path),
                    size,
                )

            except Exception:

                pass

    return ImageFont.load_default()


# ============================================================
# DIALOGUE TEXT
# ============================================================

def prepare_dialogue_text(
    text: str,
    max_chars: int = 26,
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
        lines[:4]
    )


# ============================================================
# NORMALIZE DIALOGUE
# ============================================================

def normalize_dialogue(
    dialogue,
):

    """
    Supports:

    1. Pydantic DialogueLine objects
    2. dictionaries
    3. normal strings

    This prevents text such as:

    speaker='Arun' text='Hello'

    from appearing inside the bubble.
    """

    speaker = ""
    text = ""

    # --------------------------------------------------------
    # Pydantic / object
    # --------------------------------------------------------

    if hasattr(
        dialogue,
        "speaker",
    ):

        speaker = str(
            getattr(
                dialogue,
                "speaker",
                "",
            )
        ).strip()

        text = str(
            getattr(
                dialogue,
                "text",
                "",
            )
        ).strip()

    # --------------------------------------------------------
    # Dictionary
    # --------------------------------------------------------

    elif isinstance(
        dialogue,
        dict,
    ):

        speaker = str(
            dialogue.get(
                "speaker",
                "",
            )
        ).strip()

        text = str(
            dialogue.get(
                "text",
                "",
            )
        ).strip()

    # --------------------------------------------------------
    # String
    # --------------------------------------------------------

    else:

        text = str(
            dialogue
        ).strip()

    return {
        "speaker": speaker,
        "text": text,
    }


# ============================================================
# BUBBLE SIZE
# ============================================================

def calculate_bubble_size(
    draw,
    text,
    font,
):

    bbox = draw.multiline_textbbox(
        (0, 0),
        text,
        font=font,
        spacing=6,
        align="center",
    )

    text_width = (
        bbox[2] - bbox[0]
    )

    text_height = (
        bbox[3] - bbox[1]
    )

    padding_x = 28
    padding_y = 20

    width = (
        text_width
        + padding_x * 2
    )

    height = (
        text_height
        + padding_y * 2
    )

    width = max(
        width,
        170,
    )

    height = max(
        height,
        75,
    )

    width = min(
        width,
        430,
    )

    height = min(
        height,
        190,
    )

    return width, height


# ============================================================
# FACE DETECTION
# ============================================================

def detect_faces(
    image: Image.Image,
):

    if not OPENCV_AVAILABLE:

        return []

    try:

        rgb = image.convert(
            "RGB"
        )

        frame = cv2.cvtColor(
            __import__(
                "numpy"
            ).array(rgb),
            cv2.COLOR_RGB2GRAY,
        )

        cascade_path = (
            cv2.data.haarcascades
            + "haarcascade_frontalface_default.xml"
        )

        classifier = (
            cv2.CascadeClassifier(
                cascade_path
            )
        )

        faces = classifier.detectMultiScale(
            frame,
            scaleFactor=1.12,
            minNeighbors=5,
            minSize=(50, 50),
        )

        result = []

        for x, y, w, h in faces:

            result.append(
                {
                    "x": x + w // 2,
                    "y": y + h // 2,
                    "width": w,
                    "height": h,
                }
            )

        result.sort(
            key=lambda face: face["x"]
        )

        return result

    except Exception as error:

        print(
            f"Face detection skipped: {error}"
        )

        return []


# ============================================================
# BOX OVERLAP
# ============================================================

def boxes_overlap(
    box1,
    box2,
    gap=18,
):

    l1, t1, r1, b1 = box1

    l2, t2, r2, b2 = box2

    return not (
        r1 + gap < l2
        or r2 + gap < l1
        or b1 + gap < t2
        or b2 + gap < t1
    )


# ============================================================
# KEEP BOX INSIDE IMAGE
# ============================================================

def keep_box_inside(
    box,
    image_width,
    image_height,
    margin=24,
):

    left, top, right, bottom = box

    width = (
        right - left
    )

    height = (
        bottom - top
    )

    if left < margin:

        left = margin

        right = (
            left + width
        )

    if right > image_width - margin:

        right = (
            image_width - margin
        )

        left = (
            right - width
        )

    if top < margin:

        top = margin

        bottom = (
            top + height
        )

    if bottom > image_height - margin:

        bottom = (
            image_height - margin
        )

        top = (
            bottom - height
        )

    return (
        int(left),
        int(top),
        int(right),
        int(bottom),
    )


# ============================================================
# FIND SAFE BUBBLE POSITION
# ============================================================

def find_safe_position(
    center_x,
    preferred_y,
    bubble_width,
    bubble_height,
    image_width,
    image_height,
    existing_boxes,
    face=None,
):

    candidate_offsets = [

        (0, 0),

        (-80, 0),

        (80, 0),

        (0, 90),

        (0, -90),

        (-120, 80),

        (120, 80),

        (-120, -80),

        (120, -80),

        (-180, 0),

        (180, 0),

    ]

    for dx, dy in candidate_offsets:

        cx = (
            center_x + dx
        )

        cy = (
            preferred_y + dy
        )

        box = (
            int(
                cx
                - bubble_width / 2
            ),
            int(cy),
            int(
                cx
                + bubble_width / 2
            ),
            int(
                cy
                + bubble_height
            ),
        )

        box = keep_box_inside(
            box,
            image_width,
            image_height,
        )

        collision = False

        for existing in existing_boxes:

            if boxes_overlap(
                box,
                existing,
                gap=24,
            ):

                collision = True

                break

        if collision:

            continue

        # ----------------------------------------------------
        # Avoid face
        # ----------------------------------------------------

        if face:

            face_left = (
                face["x"]
                - face["width"] // 2
                - 20
            )

            face_top = (
                face["y"]
                - face["height"] // 2
                - 20
            )

            face_right = (
                face["x"]
                + face["width"] // 2
                + 20
            )

            face_bottom = (
                face["y"]
                + face["height"] // 2
                + 20
            )

            face_box = (
                face_left,
                face_top,
                face_right,
                face_bottom,
            )

            if boxes_overlap(
                box,
                face_box,
                gap=10,
            ):

                continue

        return box

    return keep_box_inside(
        (
            center_x
            - bubble_width / 2,

            preferred_y,

            center_x
            + bubble_width / 2,

            preferred_y
            + bubble_height,
        ),
        image_width,
        image_height,
    )


# ============================================================
# DRAW SPEECH BUBBLE
# ============================================================

def draw_speech_bubble(
    draw,
    box,
    text,
    font,
    tail_x,
    style=0,
):

    left, top, right, bottom = box

    # --------------------------------------------------------
    # Rounded bubble
    # --------------------------------------------------------

    if style == 0:

        draw.rounded_rectangle(
            box,
            radius=28,
            fill="white",
            outline="#20243a",
            width=4,
        )

        tail = [

            (
                tail_x - 18,
                bottom - 3,
            ),

            (
                tail_x,
                bottom + 30,
            ),

            (
                tail_x + 18,
                bottom - 3,
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

    # --------------------------------------------------------
    # Square bubble
    # --------------------------------------------------------

    elif style == 1:

        draw.rounded_rectangle(
            box,
            radius=12,
            fill="#fffdf7",
            outline="#20243a",
            width=4,
        )

        tail = [

            (
                tail_x - 16,
                bottom - 3,
            ),

            (
                tail_x,
                bottom + 27,
            ),

            (
                tail_x + 16,
                bottom - 3,
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

    # --------------------------------------------------------
    # Cloud bubble
    # --------------------------------------------------------

    elif style == 2:

        draw.rounded_rectangle(
            box,
            radius=35,
            fill="white",
            outline="#20243a",
            width=4,
        )

        circles = [

            (
                left + 5,
                top + 8,
                left + 48,
                top + 51,
            ),

            (
                right - 53,
                top + 6,
                right - 10,
                top + 49,
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
                tail_x - 13,
                bottom + 5,
                tail_x + 12,
                bottom + 30,
            ),
            fill="white",
            outline="#20243a",
            width=3,
        )

    # --------------------------------------------------------
    # Star bubble
    # --------------------------------------------------------

    else:

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

        for i in range(24):

            angle = (
                i * math.pi / 12
            )

            if i % 2 == 0:

                rx = radius_x
                ry = radius_y

            else:

                rx = (
                    radius_x * 0.82
                )

                ry = (
                    radius_y * 0.82
                )

            x = (
                center_x
                + rx * math.cos(angle)
            )

            y = (
                center_y
                + ry * math.sin(angle)
            )

            points.append(
                (x, y)
            )

        draw.polygon(
            points,
            fill="white",
            outline="#20243a",
        )

    # --------------------------------------------------------
    # Bubble text
    # --------------------------------------------------------

    bbox = draw.multiline_textbbox(
        (0, 0),
        text,
        font=font,
        spacing=6,
        align="center",
    )

    text_width = (
        bbox[2] - bbox[0]
    )

    text_height = (
        bbox[3] - bbox[1]
    )

    text_x = (
        left
        + (
            right
            - left
            - text_width
        ) / 2
    )

    text_y = (
        top
        + (
            bottom
            - top
            - text_height
        ) / 2
    )

    draw.multiline_text(
        (
            text_x,
            text_y,
        ),
        text,
        font=font,
        fill="#20243a",
        spacing=6,
        align="center",
    )


# ============================================================
# ADD DIALOGUE BOXES
# ============================================================

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

    image_width, image_height = (
        image.size
    )

    font = get_font(
        24,
        bold=True,
    )

    # --------------------------------------------------------
    # Normalize ALL dialogue formats
    # --------------------------------------------------------

    normalized = []

    for dialogue in dialogues:

        item = normalize_dialogue(
            dialogue
        )

        speaker = item[
            "speaker"
        ]

        text = item[
            "text"
        ]

        if not text:

            continue

        normalized.append(
            {
                "speaker": speaker,
                "text": text,
            }
        )

    # Maximum two bubbles per panel

    normalized = normalized[:2]

    if not normalized:

        return image

    faces = detect_faces(
        image
    )

    existing_boxes = []

    # ========================================================
    # ONE DIALOGUE
    # ========================================================

    if len(normalized) == 1:

        dialogue = normalized[0]

        text = prepare_dialogue_text(
            dialogue["text"]
        )

        bubble_width, bubble_height = (
            calculate_bubble_size(
                draw,
                text,
                font,
            )
        )

        if faces:

            face = faces[0]

            center_x = face[
                "x"
            ]

            preferred_y = max(
                30,

                face["y"]
                - face["height"]
                - bubble_height
                - 30,
            )

        else:

            face = None

            center_x = (
                image_width // 2
            )

            preferred_y = 55

        box = find_safe_position(
            center_x,
            preferred_y,
            bubble_width,
            bubble_height,
            image_width,
            image_height,
            existing_boxes,
            face,
        )

        existing_boxes.append(
            box
        )

        left, top, right, bottom = (
            box
        )

        if face:

            tail_x = max(
                left + 25,

                min(
                    right - 25,
                    face["x"],
                ),
            )

        else:

            tail_x = (
                left + right
            ) // 2

        draw_speech_bubble(
            draw,
            box,
            text,
            font,
            int(tail_x),
            style=(
                panel_number % 4
            ),
        )

        return image

    # ========================================================
    # TWO DIALOGUES
    # ========================================================

    first = normalized[0]

    second = normalized[1]

    first_text = prepare_dialogue_text(
        first["text"]
    )

    second_text = prepare_dialogue_text(
        second["text"]
    )

    first_width, first_height = (
        calculate_bubble_size(
            draw,
            first_text,
            font,
        )
    )

    second_width, second_height = (
        calculate_bubble_size(
            draw,
            second_text,
            font,
        )
    )

    # --------------------------------------------------------
    # Face positions
    # --------------------------------------------------------

    if len(faces) >= 2:

        first_face = faces[0]

        second_face = faces[-1]

    elif len(faces) == 1:

        first_face = faces[0]

        second_face = {
            "x": (
                image_width
                - first_face["x"]
            ),
            "y": first_face["y"],
            "width": first_face[
                "width"
            ],
            "height": first_face[
                "height"
            ],
        }

    else:

        first_face = {
            "x": image_width * 0.30,
            "y": image_height * 0.55,
            "width": 100,
            "height": 120,
        }

        second_face = {
            "x": image_width * 0.70,
            "y": image_height * 0.55,
            "width": 100,
            "height": 120,
        }

    # --------------------------------------------------------
    # First bubble
    # --------------------------------------------------------

    first_preferred_y = max(
        30,

        first_face["y"]
        - first_face["height"]
        - first_height
        - 25,
    )

    first_box = find_safe_position(
        first_face["x"],
        first_preferred_y,
        first_width,
        first_height,
        image_width,
        image_height,
        existing_boxes,
        first_face,
    )

    existing_boxes.append(
        first_box
    )

    # --------------------------------------------------------
    # Second bubble
    # --------------------------------------------------------

    second_preferred_y = max(
        50,

        second_face["y"]
        - second_face["height"]
        - second_height
        - 25,
    )

    second_box = find_safe_position(
        second_face["x"],
        second_preferred_y,
        second_width,
        second_height,
        image_width,
        image_height,
        existing_boxes,
        second_face,
    )

    existing_boxes.append(
        second_box
    )

    # --------------------------------------------------------
    # Draw first bubble
    # --------------------------------------------------------

    left, top, right, bottom = (
        first_box
    )

    first_tail_x = max(
        left + 25,

        min(
            right - 25,
            first_face["x"],
        ),
    )

    draw_speech_bubble(
        draw,
        first_box,
        first_text,
        font,
        int(first_tail_x),
        style=(
            panel_number % 4
        ),
    )

    # --------------------------------------------------------
    # Draw second bubble
    # --------------------------------------------------------

    left, top, right, bottom = (
        second_box
    )

    second_tail_x = max(
        left + 25,

        min(
            right - 25,
            second_face["x"],
        ),
    )

    draw_speech_bubble(
        draw,
        second_box,
        second_text,
        font,
        int(second_tail_x),
        style=(
            (panel_number + 1) % 4
        ),
    )

    return image


# ============================================================
# GENERATE PANEL IMAGE
# ============================================================

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

    # ========================================================
    # HF TOKEN CHECK
    # ========================================================

    if not settings.HF_TOKEN:

        if output_path.exists():

            print(
                f"Using existing image "
                f"for panel {panel_number}."
            )

            return str(
                output_path
            )

        raise RuntimeError(
            "HF_TOKEN is missing."
        )

    # ========================================================
    # HUGGING FACE CLIENT
    # ========================================================

    client = InferenceClient(
        provider=settings.IMAGE_PROVIDER,
        api_key=settings.HF_TOKEN,
    )

    # ========================================================
    # AI IMAGE PROMPT
    # ========================================================

    prompt = f"""
Create ONE professional original 2D animated
comic-book illustration.

IMPORTANT IMAGE RULES:

This is an illustration only.

DO NOT DRAW ANY SPEECH BUBBLES.

DO NOT DRAW ANY DIALOGUE BUBBLES.

DO NOT DRAW ANY WORDS.

DO NOT DRAW ANY LETTERS.

DO NOT DRAW ANY SENTENCES.

DO NOT DRAW ANY CAPTIONS.

DO NOT DRAW ANY TEXT BOXES.

DO NOT DRAW ANY COMIC TEXT.

DO NOT DRAW ANY SUBTITLES.

DO NOT DRAW ANY UI.

DO NOT DRAW ANY LOGOS.

DO NOT DRAW ANY WATERMARKS.

The final image must contain ONLY the
characters, environment, objects and lighting.

ComicCraft will add the dialogue bubbles
after the image is generated.

STYLE:

High-quality colorful cartoon animation.

Clean bold outlines.

Professional digital illustration.

Cinematic lighting.

Expressive original characters.

Detailed environment.

Dynamic composition.

Strong facial expressions.

Bright attractive colors.

CHARACTERS:

Create completely original characters.

Keep characters visually consistent.

Do not copy famous cartoon characters.

Do not use copyrighted characters.

If two characters are present, clearly separate
their positions.

PANEL:

This is panel {panel_number}
of {settings.PANEL_COUNT}.

SCENE:

{visual_prompt}

COMPOSITION:

Keep the characters clearly visible.

Keep the main action easy to understand.

Leave clean empty visual space near the
upper and side areas of the composition.

That empty space will be used later by
ComicCraft for its own dialogue bubbles.

FINAL REQUIREMENT:

NO TEXT OF ANY KIND.

NO SPEECH BUBBLES.

NO DIALOGUE BUBBLES.

NO CAPTIONS.

NO WORDS.

NO LETTERS.

NO WATERMARKS.
"""

    # ========================================================
    # GENERATE
    # ========================================================

    try:

        print(
            f"Generating AI cartoon "
            f"panel {panel_number}/"
            f"{settings.PANEL_COUNT}..."
        )

        image = client.text_to_image(
            prompt=prompt,
            model=settings.IMAGE_MODEL,
        )

        # ====================================================
        # ADD OUR OWN CLEAN DIALOGUE BUBBLES
        # ====================================================

        image = add_dialogue_boxes(
            image,
            dialogues,
            panel_number,
        )

        # ====================================================
        # SAVE
        # ====================================================

        image.save(
            output_path,
            format="PNG",
        )

        print(
            f"Panel {panel_number} "
            f"created successfully."
        )

        return str(
            output_path
        )

    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as error:

        error_text = str(
            error
        )

        print(
            f"Panel {panel_number} "
            f"image generation unavailable."
        )

        print(
            f"Image generation error: "
            f"{error}"
        )

        # ----------------------------------------------------
        # Reuse old image if available
        # ----------------------------------------------------

        if output_path.exists():

            print(
                f"Reusing existing AI image "
                f"for panel {panel_number}."
            )

            return str(
                output_path
            )

        # ----------------------------------------------------
        # Payment / quota error
        # ----------------------------------------------------

        if "402" in error_text:

            raise RuntimeError(
                f"Panel {panel_number} "
                f"could not be generated because "
                f"the image generation service "
                f"quota is currently unavailable."
            ) from error

        # ----------------------------------------------------
        # Other error
        # ----------------------------------------------------

        raise RuntimeError(
            f"Panel {panel_number} "
            f"image generation failed."
        ) from error