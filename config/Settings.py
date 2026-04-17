from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

class QuotaLimitError(Exception):
    """Custom exception raised when all API keys have reached their quota limit"""
    pass

class Settings(BaseSettings):
    # Provider flag: set USE_OPENAI=true in .env to switch to OpenAI
    use_openai: bool = Field(default=False, env="USE_OPENAI")

    openai_api_key: str | None = Field(default=None, env="OPENAI_API_KEY")
    nvidia_api_key: str | None = Field(default=None, env="NVIDIA_API_KEY")

    # OpenAI defaults (used when USE_OPENAI=true)
    openai_model: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")
    openai_embedding_model: str = Field(default="text-embedding-3-small", env="OPENAI_EMBEDDING_MODEL")

    # NVIDIA defaults (used when USE_OPENAI=false)
    nvidia_model: str = Field(default="openai/gpt-oss-120b", env="NVIDIA_MODEL")
    nvidia_embedding_model: str = Field(default="nvidia/llama-3.2-nemoretriever-300m-embed-v1", env="NVIDIA_EMBEDDING_MODEL")

    max_output_tokens: int = Field(default=32768, env="MAX_OUTPUT_TOKENS")
    temperature: float = Field(default=1, env="TEMPERATURE")
    top_p: float = Field(default=1, env="TOP_P")

    save_dir: str = Field(default="downloaded_files", env="SAVE_DIR")
    max_file_size: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")
    max_files_per_request: int = Field(default=10, env="MAX_FILES_PER_REQUEST")
    minimum_eligible_score: int = Field(default=60, env="MINIMUM_ELIGIBLE_SCORE")
    batch_concurrent_limit: int = Field(default=10, env="BATCH_CONCURRENT_LIMIT")

    allowed_file_types: str = Field(
        default=(
            "application/pdf,"
            "application/msword,"
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ),
        env="ALLOWED_FILE_TYPES"
    )

    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="app.log", env="LOG_FILE")

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
