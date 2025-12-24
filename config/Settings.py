from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv
from pathlib import Path
import os
import google.generativeai as genai

load_dotenv()


class QuotaLimitError(Exception):
    """Custom exception raised when all API keys have reached their quota limit"""
    pass


class Settings(BaseSettings):
    api_keys: list[str] = Field(
        default_factory=lambda: [
            os.getenv("API_KEY_1"),
            os.getenv("API_KEY_2"),
            os.getenv("API_KEY_3"),
        ]
    )
    openai_api_key: str | None = Field(default=None, env="OPENAI_API_KEY")
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

_original_generate_content = genai.GenerativeModel.generate_content






import inspect
import os
import logging
import time
from openai import OpenAI

class MockPart:
    def __init__(self, text):
        self.text = text

class MockContent:
    def __init__(self, text):
        self.parts = [MockPart(text)]

class MockCandidate:
    def __init__(self, text):
        self.content = MockContent(text)

class MockGeminiResponse:
    def __init__(self, text, usage):
        self.text = text
        self.usage_metadata = usage
        self.candidates = [MockCandidate(text)]

    def json(self):
        return self.text

def call_openai_fallback(prompt, agent_name):
    if not settings.openai_api_key:
        logging.error("❌ OpenAI API key not found. Cannot fallback.")
        return None
    
    logging.info(f"⚠️ All Gemini keys failed. Falling back to OpenAI (gpt-4o-mini) for agent: {agent_name}")
    try:
        client = OpenAI(api_key=settings.openai_api_key)
        
        # Handle prompt if it's a list (Gemini supports list of parts)
        if isinstance(prompt, list):
            prompt = " ".join([str(p) for p in prompt])
            
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": str(prompt)}],
            temperature=settings.temperature
        )
        
        content = response.choices[0].message.content
        usage = response.usage
        
        # Map OpenAI usage to Gemini format structure
        gemini_usage = type('Usage', (), {})()
        gemini_usage.prompt_token_count = usage.prompt_tokens
        gemini_usage.candidates_token_count = usage.completion_tokens
        gemini_usage.total_token_count = usage.total_tokens
        
        return MockGeminiResponse(content, gemini_usage)
    except Exception as e:
        logging.error(f"❌ OpenAI fallback failed: {e}")
        return None

def find_best_config():
    """
    Iterates through all Models and all API Keys.
    If a working combination is found, sets it and returns.
    If all fail, switches to OpenAI Fallback Mode.
    """
    print("🔄 Checking for best available API key and Model...")
    
    # Ensure current model is first in the list if not already
    current_model = os.getenv("MODEL", "gemini-2.5-flash")
    model_list = [current_model, "gemini-1.5-flash", "gemini-1.5-pro"]
    # Remove duplicates while preserving order
    model_list = list(dict.fromkeys(model_list))

    for model_name in model_list:
        print(f"  > Testing Model: {model_name}")
        for idx, key in enumerate(settings.api_keys, start=1):
            if not key:
                continue
            
            # print(f"    Trying Key #{idx}: {key[:6]}***")
            try:
                genai.configure(api_key=key)
                model = genai.GenerativeModel(model_name)
                # Use a lightweight ping
                response = _original_generate_content(model, "ping")
                if response:
                    print(f"✅ Found working config: Model={model_name}, Key=#{idx} ({key[:6]}***)")
                    settings.api_key = key
                    settings.model = model_name
                    settings.last_check_time = time.time()
                    return
            except Exception as e:
                error_msg = str(e).lower()
                if "limit" in error_msg or "quota" in error_msg:
                    pass # Expected failure
                else:
                    print(f"    ❌ Key #{idx} failed with {model_name}: {e}")

    # If we reach here, ALL Gemini combinations failed
    if settings.openai_api_key:
        print("⚠️ All Gemini keys/models failed. Switching to OpenAI Fallback Mode.")
        settings.api_key = "OPENAI_FALLBACK_MODE"
        settings.last_check_time = time.time()
        settings.all_apis_failed = False  # OpenAI is available
        return

    # All APIs failed - set flag
    print("❌ All API keys (Gemini and OpenAI) have reached their quota limit.")
    settings.api_key = "ALL_APIS_FAILED"
    settings.all_apis_failed = True
    settings.last_check_time = time.time()

# Initial Setup
try:
    find_best_config()
except Exception as e:
    print(f"Startup Warning: {e}")
    settings.all_apis_failed = True

def _smart_generate_content(self, *args, **kwargs):
    # 0. Check if all APIs have failed - return immediately without executing logic
    if getattr(settings, 'all_apis_failed', False):
        logging.error("❌ All API keys have reached their quota limit. Request rejected.")
        raise QuotaLimitError("All API keys have reached their quota limit. Please try again later.")
    
    # 1. Periodic Check (Every 1 Hour)
    if hasattr(settings, 'last_check_time') and (time.time() - settings.last_check_time > 3600):
        logging.info("🕐 1 Hour passed. Attempting to restore primary Gemini keys/models...")
        try:
            find_best_config()
            # If we switched back to a Gemini key, we should re-initialize the model in the current call?
            # The current 'self' is bound to the old model/key configuration.
            # We will handle rotation below if the current one fails, or we can force a reload.
            # For simplicity, we just update settings. If the current call fails, the retry logic will pick up the new settings.
        except Exception:
            logging.warning("Restoration check failed. Continuing with current config.")

    # Helper to identify the calling agent
    agent_name = "Unknown Agent"
    try:
        stack = inspect.stack()
        for frame in stack:
            filename = frame.filename
            if "agents" in filename and filename.endswith(".py"):
                agent_name = os.path.basename(filename).replace(".py", "")
                break
    except Exception:
        pass

    # 2. Check for Fallback Mode
    if getattr(settings, "api_key", None) == "OPENAI_FALLBACK_MODE":
        fallback_response = call_openai_fallback(args[0] if args else kwargs.get('contents'), agent_name)
        if fallback_response:
            usage = fallback_response.usage_metadata
            input_tokens = usage.prompt_token_count
            output_tokens = usage.candidates_token_count
            total_tokens = usage.total_token_count
            logging.info(f"[{agent_name}] (OpenAI Fallback) Input Tokens: {input_tokens} | Output Tokens: {output_tokens} | Total: {total_tokens}")
            return fallback_response
        # If OpenAI fails, we might want to try finding Gemini again?
        logging.error("OpenAI Fallback failed. Retrying Gemini config search...")
        try:
            find_best_config()
            # If found, recursively call smart_generate (which will use the new key)
            # We need to reconstruct the model though.
            model_name = settings.model
            new_model = genai.GenerativeModel(model_name)
            return _original_generate_content(new_model, *args, **kwargs)
        except:
            # All APIs have failed
            settings.all_apis_failed = True
            logging.error("❌ System completely unavailable (Gemini & OpenAI failed).")
            raise QuotaLimitError("All API keys have reached their quota limit. Please try again later.")

    # 3. Standard Gemini Call
    try:
        response = _original_generate_content(self, *args, **kwargs)
        if hasattr(response, "usage_metadata"):
            usage = response.usage_metadata
            input_tokens = usage.prompt_token_count
            output_tokens = usage.candidates_token_count
            total_tokens = usage.total_token_count
            logging.info(f"[{agent_name}] Input Tokens: {input_tokens} | Output Tokens: {output_tokens} | Total: {total_tokens}")
        return response
    except Exception as e:
        error_str = str(e).lower()
        if "429" in error_str or "quota" in error_str or "limit" in error_str:
            logging.warning(f"⚠️ Quota exceeded. Initiating full rotation strategy...")
            try:
                # Rotate to next available config
                find_best_config()
                
                # Check if all APIs failed
                if settings.api_key == "ALL_APIS_FAILED":
                    settings.all_apis_failed = True
                    logging.error("❌ All API keys have reached their quota limit.")
                    raise QuotaLimitError("All API keys have reached their quota limit. Please try again later.")
                
                # Check if we switched to OpenAI
                if settings.api_key == "OPENAI_FALLBACK_MODE":
                     return _smart_generate_content(self, *args, **kwargs) # Recurse to hit fallback block

                # If we found a new Gemini config
                model_name = settings.model
                logging.info(f"Retrying with new config: Model={model_name}")
                new_model = genai.GenerativeModel(model_name)
                
                response = _original_generate_content(new_model, *args, **kwargs)
                if hasattr(response, "usage_metadata"):
                    usage = response.usage_metadata
                    input_tokens = usage.prompt_token_count
                    output_tokens = usage.candidates_token_count
                    total_tokens = usage.total_token_count
                    logging.info(f"[{agent_name}] Input Tokens: {input_tokens} | Output Tokens: {output_tokens} | Total: {total_tokens}")
                return response
            except QuotaLimitError:
                # Re-raise QuotaLimitError as-is
                raise
            except Exception as retry_error:
                logging.error(f"❌ Retry failed after rotation: {retry_error}")
                settings.all_apis_failed = True
                raise QuotaLimitError("All API keys have reached their quota limit. Please try again later.")
        raise e

genai.GenerativeModel.generate_content = _smart_generate_content
logging.info("✅ Smart API Key Rotation initialized.")
