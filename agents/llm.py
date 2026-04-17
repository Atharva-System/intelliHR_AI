from langchain_nvidia_ai_endpoints import ChatNVIDIA, NVIDIAEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from config.Settings import settings


def get_llm(temperature: float | None = None, max_tokens: int | None = None):
    """
    Centralized LLM factory. Returns ChatOpenAI or ChatNVIDIA based on
    the USE_OPENAI flag in .env.

    Set USE_OPENAI=true  → OpenAI  (uses OPENAI_API_KEY + OPENAI_MODEL)
    Set USE_OPENAI=false → NVIDIA  (uses NVIDIA_API_KEY + NVIDIA_MODEL)

    Args:
        temperature: Override the default temperature from settings.
        max_tokens:  Override the default max_output_tokens from settings.
    """
    _temperature = temperature if temperature is not None else settings.temperature
    _max_tokens = max_tokens if max_tokens is not None else settings.max_output_tokens

    if settings.use_openai:
        return ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=_temperature,
            max_tokens=_max_tokens,
        )

    return ChatNVIDIA(
        model=settings.nvidia_model,
        api_key=settings.nvidia_api_key,
        temperature=_temperature,
        top_p=settings.top_p,
        max_tokens=_max_tokens,
    )


def get_embeddings():
    """
    Centralized Embeddings factory. Returns OpenAIEmbeddings or NVIDIAEmbeddings
    based on the USE_OPENAI flag in .env.

    Set USE_OPENAI=true  → OpenAI  (uses OPENAI_API_KEY + OPENAI_EMBEDDING_MODEL)
    Set USE_OPENAI=false → NVIDIA  (uses NVIDIA_API_KEY + NVIDIA_EMBEDDING_MODEL)
    """
    if settings.use_openai:
        return OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            api_key=settings.openai_api_key,
        )

    return NVIDIAEmbeddings(
        model=settings.nvidia_embedding_model,
        api_key=settings.nvidia_api_key,
        truncate="NONE",
    )
