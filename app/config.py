from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):

    # -----------------------------------------
    # GEMINI API
    # -----------------------------------------

    GEMINI_API_KEY: str = ""

    GEMINI_FLASH_MODEL: str = "gemini-3.8-flash"
    GEMINI_PRO_MODEL: str = "gemini-3.1-pro-preview"

    # -----------------------------------------
    # HUGGING FACE IMAGE GENERATION
    # -----------------------------------------

    HF_TOKEN: str = ""

    IMAGE_MODEL: str = "black-forest-labs/FLUX.1-schnell"
    IMAGE_PROVIDER: str = "auto"

    # -----------------------------------------
    # COMIC SETTINGS
    # -----------------------------------------

    # ComicCraft will generate exactly 5 panels.
    PANEL_COUNT: int = 5

    MAX_PROMPT_LENGTH: int = 2000

    # -----------------------------------------
    # ENVIRONMENT CONFIGURATION
    # -----------------------------------------

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# -----------------------------------------
# CREATE SETTINGS OBJECT
# -----------------------------------------

settings = Settings()


# -----------------------------------------
# PROJECT DIRECTORIES
# -----------------------------------------

PANELS_DIR = (
    BASE_DIR
    / "static"
    / "panels"
)

EXPORTS_DIR = (
    BASE_DIR
    / "static"
    / "exports"
)


# -----------------------------------------
# CREATE DIRECTORIES IF THEY DO NOT EXIST
# -----------------------------------------

PANELS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

EXPORTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)