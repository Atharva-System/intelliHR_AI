# config/Settings.py
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv
from pathlib import Path
import os
import google.generativeai as genai

load_dotenv()


class Settings(BaseSettings):
    # API keys for fallback rotation
    api_keys: list[str] = Field(
        default_factory=lambda: [
            os.getenv("API_KEY_1"),
            os.getenv("API_KEY_2"),
            os.getenv("API_KEY_3"),
        ]
    )

    # Model configuration
    model: str = Field(default="gemini-2.0-flash", env="MODEL")
    max_output_tokens: int = Field(default=10000, env="MAX_OUTPUT_TOKENS")
    temperature: float = Field(default=0.2, env="TEMPERATURE")

    # File handling
    save_dir: str = Field(default="downloaded_files", env="SAVE_DIR")
    max_file_size: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")
    max_files_per_request: int = Field(default=10, env="MAX_FILES_PER_REQUEST")
    minimum_eligible_score: int = Field(default=60, env="MINIMUM_ELIGIBLE_SCORE")

    allowed_file_types: str = Field(
        default=(
            "application/pdf,"
            "application/msword,"
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ),
        env="ALLOWED_FILE_TYPES"
    )

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="app.log", env="LOG_FILE")

    # API host configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    debug_mode: bool = Field(default=False, env="DEBUG_MODE")

    @property
    def allowed_mime_types(self) -> set:
        return set(self.allowed_file_types.split(","))

    @property
    def save_directory(self) -> Path:
        return Path(self.save_dir)

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"


settings = Settings()


def get_working_api_key():
    """Try each Gemini API key until one works."""
    for key in settings.api_keys:
        if not key:
            continue
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel(settings.model)
            response = model.generate_content("ping")
            if response and hasattr(response, "text"):
                print(f"✅ Using API key: {key[:6]}***")
                return key
        except Exception as e:
            print(f"❌ API key {key[:6]}*** failed: {e}")
    raise RuntimeError("All API keys failed or hit limits!")


# ✅ Export a working API key
api_key = get_working_api_key()
