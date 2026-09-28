from pathlib import Path

from fpdf import FPDF
from PIL import Image

from .config import EXPORTS_DIR


def clean_text(text: str) -> str:
    """
    Convert text into PDF-safe characters.
    """

    if not text:
        return ""

    replacements = {
        "—": "-",
        "–": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "…": "...",
        "✨": "*",
        "💬": "",
        "🎨": "",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.encode(
        "latin-1",
        "replace",
    ).decode("latin-1")


def export_comic_to_pdf(
    panels,
    filename: str = "comiccraft_comic.pdf",
) -> Path:

    EXPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        EXPORTS_DIR / filename
    )

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4",
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15,
    )

    for panel in panels:

        pdf.add_page()

        panel_number = getattr(
            panel,
            "panel_number",
            None,
        )

        image_path = getattr(
            panel,
            "image_path",
            "",
        )

        narration = getattr(
            panel,
            "narration",
            "",
        )

        dialogue = getattr(
            panel,
            "dialogue",
            "",
        )

        # -----------------------------------------
        # TITLE
        # -----------------------------------------

        pdf.set_font(
            "Helvetica",
            "B",
            18,
        )

        pdf.cell(
            0,
            12,
            f"COMICCRAFT - PANEL {panel_number}",
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )

        pdf.ln(4)

        # -----------------------------------------
        # IMAGE
        # -----------------------------------------

        if image_path:

            image_file = Path(
                str(image_path)
            )

            if image_file.exists():

                try:

                    with Image.open(
                        image_file
                    ) as image:

                        width, height = (
                            image.size
                        )

                    max_width = 175
                    max_height = 155

                    ratio = min(
                        max_width / width,
                        max_height / height,
                    )

                    display_width = (
                        width * ratio
                    )

                    display_height = (
                        height * ratio
                    )

                    x_position = (
                        210 - display_width
                    ) / 2

                    pdf.image(
                        str(image_file),
                        x=x_position,
                        y=35,
                        w=display_width,
                        h=display_height,
                    )

                    pdf.set_y(
                        35 + display_height + 8
                    )

                except Exception as error:

                    print(
                        f"PDF image error: {error}"
                    )

                    pdf.set_y(45)

                    pdf.set_font(
                        "Helvetica",
                        "",
                        12,
                    )

                    pdf.cell(
                        0,
                        10,
                        "Comic image could not be loaded.",
                        align="C",
                        new_x="LMARGIN",
                        new_y="NEXT",
                    )

            else:

                pdf.set_y(45)

                pdf.set_font(
                    "Helvetica",
                    "",
                    12,
                )

                pdf.cell(
                    0,
                    10,
                    "Comic image is not available.",
                    align="C",
                    new_x="LMARGIN",
                    new_y="NEXT",
                )

        # -----------------------------------------
        # NARRATION
        # -----------------------------------------

        if narration:

            pdf.set_font(
                "Helvetica",
                "B",
                12,
            )

            pdf.cell(
                0,
                8,
                "Narration",
                new_x="LMARGIN",
                new_y="NEXT",
            )

            pdf.set_font(
                "Helvetica",
                "",
                11,
            )

            pdf.multi_cell(
                0,
                7,
                clean_text(
                    narration
                ),
            )

            pdf.ln(3)

        # -----------------------------------------
        # DIALOGUE
        # -----------------------------------------

        if dialogue:

            pdf.set_font(
                "Helvetica",
                "B",
                12,
            )

            pdf.cell(
                0,
                8,
                "Dialogue",
                new_x="LMARGIN",
                new_y="NEXT",
            )

            pdf.set_font(
                "Helvetica",
                "",
                11,
            )

            pdf.multi_cell(
                0,
                7,
                clean_text(
                    dialogue
                ),
            )

    # -----------------------------------------
    # SAVE PDF
    # -----------------------------------------

    pdf.output(
        str(output_path)
    )

    print(
        f"Comic PDF created: {output_path}"
    )

    return output_path