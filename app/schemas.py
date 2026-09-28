from pydantic import BaseModel, Field
from typing import List


class PromptRequest(BaseModel):

    prompt: str = Field(
        ...,
        min_length=3,
        max_length=2000
    )


class PanelOutline(BaseModel):

    panel_number: int

    scene_description: str

    visual_prompt: str


class ComicOutline(BaseModel):

    title: str

    theme: str

    panels: List[PanelOutline]


class DialogueLine(BaseModel):

    speaker: str

    text: str


class PanelStory(BaseModel):

    panel_number: int

    narration: str

    dialogues: List[DialogueLine]


class ComicStory(BaseModel):

    title: str

    panels: List[PanelStory]


class ComicPanel(BaseModel):

    panel_number: int

    scene_description: str

    visual_prompt: str

    narration: str

    dialogue: str

    image_path: str = ""