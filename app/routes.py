from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from .config import BASE_DIR, EXPORTS_DIR, settings
from .exporters import export_comic_to_pdf
from .gemini_flash import generate_comic_outline
from .gemini_pro import generate_comic_story
from .image_generator import generate_panel_image
from .layout_builder import build_comic_layout
from .schemas import PromptRequest


router = APIRouter()

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "page_title": "ComicCraft | AI Comic Story Creator"
        },
    )


@router.post("/generate")
async def generate_comic(
    request: Request,
    prompt: str = Form(...),
):
    prompt_request = PromptRequest(
        prompt=prompt[:settings.MAX_PROMPT_LENGTH]
    )

    print("\n" + "=" * 60)
    print("COMICCRAFT GENERATION STARTED")
    print("=" * 60)

    # -----------------------------------------
    # 1. GENERATE STORY OUTLINE
    # -----------------------------------------

    outline = generate_comic_outline(
        prompt_request.prompt
    )

    print(
        f"Outline created: {len(outline.panels)} panels"
    )

    # -----------------------------------------
    # 2. GENERATE STORY + DIALOGUE
    # -----------------------------------------

    story = generate_comic_story(outline)

    print(
        f"Story created: {len(story.panels)} panels"
    )

    # -----------------------------------------
    # 3. GENERATE PANEL IMAGES
    # -----------------------------------------

    image_paths = []

    story_by_panel = {
        panel.panel_number: panel
        for panel in story.panels
    }

    for panel in outline.panels:

        story_panel = story_by_panel.get(
            panel.panel_number
        )

        dialogues = []

        if story_panel:
            dialogues = story_panel.dialogues

        print(
            f"\nProcessing panel "
            f"{panel.panel_number}/{len(outline.panels)}"
        )

        try:
            image_path = generate_panel_image(
                panel.visual_prompt,
                panel.panel_number,
                dialogues,
            )

            image_paths.append(image_path)

            print(
                f"Panel {panel.panel_number} completed."
            )

        except Exception as error:

            print(
                f"Panel {panel.panel_number} failed: {error}"
            )

            # ---------------------------------
            # KEEP THE 10-PANEL FLOW ALIVE
            # ---------------------------------

            existing_path = (
                settings.BASE_DIR
                / "static"
                / "panels"
                / f"panel_{panel.panel_number}.png"
            )

            if existing_path.exists():

                print(
                    f"Using existing image for "
                    f"panel {panel.panel_number}."
                )

                image_paths.append(
                    str(existing_path)
                )

            else:

                # Do not stop the entire comic.
                # Store an empty path so the layout
                # can still contain this panel.

                print(
                    f"No image available for "
                    f"panel {panel.panel_number}."
                )

                image_paths.append("")

    # -----------------------------------------
    # 4. MAKE SURE ALL PANELS ARE PRESENT
    # -----------------------------------------

    expected_panels = len(outline.panels)

    while len(image_paths) < expected_panels:
        image_paths.append("")

    image_paths = image_paths[:expected_panels]

    print(
        f"\nTotal panels processed: "
        f"{len(image_paths)}/{expected_panels}"
    )

    # -----------------------------------------
    # 5. BUILD COMIC LAYOUT
    # -----------------------------------------

    comic_panels = build_comic_layout(
        outline,
        story,
        image_paths,
    )

    # -----------------------------------------
    # 6. EXPORT PDF
    # -----------------------------------------

    pdf_filename = "comiccraft_comic.pdf"

    pdf_path = export_comic_to_pdf(
        comic_panels,
        pdf_filename,
    )

    print("\n" + "=" * 60)
    print("COMICCRAFT GENERATION COMPLETED")
    print("=" * 60)
    print(
        f"Final comic panels: {len(comic_panels)}"
    )
    print(
        f"PDF: {pdf_path}"
    )

    return templates.TemplateResponse(
        request=request,
        name="comic_preview.html",
        context={
            "title": outline.title,
            "theme": outline.theme,
            "panels": comic_panels,
            "pdf_filename": pdf_filename,
            "pdf_path": str(pdf_path),
        },
    )


@router.post("/generate-comic/json")
async def generate_comic_json(
    data: PromptRequest,
):
    outline = generate_comic_outline(
        data.prompt
    )

    story = generate_comic_story(
        outline
    )

    image_paths = []

    story_by_panel = {
        panel.panel_number: panel
        for panel in story.panels
    }

    for panel in outline.panels:

        story_panel = story_by_panel.get(
            panel.panel_number
        )

        dialogues = []

        if story_panel:
            dialogues = story_panel.dialogues

        try:
            image_path = generate_panel_image(
                panel.visual_prompt,
                panel.panel_number,
                dialogues,
            )

            image_paths.append(
                image_path
            )

        except Exception:

            existing_path = (
                settings.BASE_DIR
                / "static"
                / "panels"
                / f"panel_{panel.panel_number}.png"
            )

            if existing_path.exists():
                image_paths.append(
                    str(existing_path)
                )
            else:
                image_paths.append("")

    comic_panels = build_comic_layout(
        outline,
        story,
        image_paths,
    )

    pdf_filename = "comiccraft_comic.pdf"

    export_comic_to_pdf(
        comic_panels,
        pdf_filename,
    )

    return {
        "title": outline.title,
        "theme": outline.theme,
        "pdf": f"/download/{pdf_filename}",
        "panels": [
            panel.model_dump()
            for panel in comic_panels
        ],
    }


@router.get("/test-image")
async def test_image():

    image_path = generate_panel_image(
        (
            "An original young hero "
            "discovering a mysterious "
            "glowing robot inside an "
            "old college laboratory."
        ),
        1,
        [
            {
                "speaker": "Arun",
                "text": "What is this mysterious robot?",
            }
        ],
    )

    return FileResponse(
        image_path
    )


@router.get("/download/{filename}")
async def download_file(
    filename: str,
):

    safe_filename = Path(filename).name

    file_path = (
        EXPORTS_DIR / safe_filename
    )

    if not file_path.exists():

        return {
            "error": "File not found"
        }

    return FileResponse(
        path=str(file_path),
        filename=safe_filename,
        media_type="application/pdf",
    )


@router.get("/export-success")
async def export_success(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "message":
                "Your comic is ready for export."
        },
    )


@router.get("/health")
async def health_check():

    return {
        "status": "healthy",
        "project": "ComicCraft",
        "version": "1.0.0",
    }