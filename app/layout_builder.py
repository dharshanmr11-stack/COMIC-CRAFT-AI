from typing import List

from .schemas import (
    ComicOutline,
    ComicStory,
    ComicPanel,
)


def build_comic_layout(
    outline: ComicOutline,
    story: ComicStory,
    image_paths: List[str],
) -> List[ComicPanel]:

    # -----------------------------------------
    # FIND STORY BY PANEL NUMBER
    # -----------------------------------------

    story_by_panel = {
        panel.panel_number: panel
        for panel in story.panels
    }

    # -----------------------------------------
    # FIND IMAGE BY PANEL NUMBER
    # -----------------------------------------

    image_by_panel = {
        index + 1: path
        for index, path in enumerate(
            image_paths
        )
    }

    comic_panels = []

    # -----------------------------------------
    # BUILD FINAL COMIC PANELS
    # -----------------------------------------

    for panel in outline.panels:

        story_panel = story_by_panel.get(
            panel.panel_number
        )

        # -------------------------------------
        # NARRATION
        # -------------------------------------

        narration = ""

        if story_panel:

            narration = (
                story_panel.narration
            )

        # -------------------------------------
        # COMBINE DIALOGUES FOR PREVIEW/PDF
        #
        # The actual image already contains
        # separate dialogue bubbles.
        # This text is only used by the
        # existing preview/PDF system.
        # -------------------------------------

        dialogue_text = ""

        if story_panel:

            dialogue_lines = []

            for dialogue in (
                story_panel.dialogues
            ):

                speaker = (
                    dialogue.speaker
                    .strip()
                )

                text = (
                    dialogue.text
                    .strip()
                )

                if not text:
                    continue

                if speaker:

                    dialogue_lines.append(
                        f"{speaker}: {text}"
                    )

                else:

                    dialogue_lines.append(
                        text
                    )

            dialogue_text = "\n".join(
                dialogue_lines
            )

        # -------------------------------------
        # CREATE COMIC PANEL
        # -------------------------------------

        comic_panels.append(
            ComicPanel(
                panel_number=(
                    panel.panel_number
                ),

                scene_description=(
                    panel.scene_description
                ),

                visual_prompt=(
                    panel.visual_prompt
                ),

                narration=narration,

                dialogue=dialogue_text,

                image_path=(
                    image_by_panel.get(
                        panel.panel_number,
                        "",
                    )
                ),
            )
        )

    return comic_panels