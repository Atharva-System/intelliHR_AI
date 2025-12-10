from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv
from pathlib import Path
import os
import google.generativeai as genai

load_dotenv()


class Settings(BaseSettings):
    api_keys: list[str] = Field(
        default_factory=lambda: [
            os.getenv("API_KEY_1"),
            os.getenv("API_KEY_2"),
            os.getenv("API_KEY_3"),
        ]
    )

    model: str = Field(default="gemini-2.5-flash", env="MODEL")
    max_output_tokens: int = Field(default=10000, env="MAX_OUTPUT_TOKENS")
    temperature: float = Field(default=0.2, env="TEMPERATURE")

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


def get_working_api_key():
    for idx, key in enumerate(settings.api_keys, start=1):
        if not key:
            continue
        print(f"Trying API key #{idx}: {key[:6]}***")
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel(settings.model)
            response = model.generate_content("ping")
            if response and hasattr(response, "text"):
                print(f"✅ Using API key #{idx}: {key[:6]}***")
                settings.api_key = key
                return key
        except Exception as e:
            error_msg = str(e).lower()
            print(f"❌ API key #{idx}: {key[:6]}*** failed: {e}")
            if "limit" in error_msg or "quota" in error_msg:
                print("API key limit reached.")
    raise RuntimeError("All API keys failed or hit limits!")

settings.api_key = get_working_api_key()

def set_and_validate_api_key(new_key: str) -> str:
    if not new_key:
        raise RuntimeError("No API key provided!")
    print(f"Checking API key: {new_key[:6]}***")
    try:
        genai.configure(api_key=new_key)
        model = genai.GenerativeModel(settings.model)
        response = model.generate_content("ping")
        if response and hasattr(response, "text"):
            settings.api_key = new_key
            return new_key
        else:
            print(f"API key {new_key[:6]}*** failed to generate content!")
            raise RuntimeError("API key failed to generate content!")
    except Exception as e:
        error_msg = str(e).lower()
        print(f"API key {new_key[:6]}*** failed: {e}")
        if "limit" in error_msg or "quota" in error_msg:
            print("API key limit reached.")
        raise RuntimeError("API key failed or hit limits!")


