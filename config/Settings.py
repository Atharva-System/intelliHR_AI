from pydantic_settings import BaseSettings
from pydantic import Field
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Settings(BaseSettings):
    # API Configuration
    api_key: str = Field(..., env="API_KEY")
    model: str = Field(default="gemini-2.0-flash", env="MODEL")
    model1: str = Field(default="gemini-2.0-flash", env="MODEL1")
    max_output_tokens: int = Field(default=10000, env="MAX_OUTPUT_TOKENS")
    temperature: float = Field(default=0.2, env="TEMPERATURE")

    # File Handling Configuration
    save_dir: str = Field(default="downloaded_files", env="SAVE_DIR")
    max_file_size: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    max_files_per_request: int = Field(default=10, env="MAX_FILES_PER_REQUEST")

    # Allowed file types
    allowed_file_types: str = Field(
        default="application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        env="ALLOWED_FILE_TYPES"
    )

    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="app.log", env="LOG_FILE")

    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    debug_mode: bool = Field(default=False, env="DEBUG_MODE")

    @property
    def allowed_mime_types(self) -> set:
        """Convert comma-separated string to set of MIME types."""
        return set(self.allowed_file_types.split(","))

    @property
    def save_directory(self) -> Path:
        """Get save directory as Path object."""
        return Path(self.save_dir)

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"

settings = Settings()