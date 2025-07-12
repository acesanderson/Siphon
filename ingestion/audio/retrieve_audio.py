from pathlib import Path
from typing import Literal

# Import our centralized logging configuration
from Siphon.logs.logging_config import get_logger


# Configure logging once at the entry point
logger = get_logger(__name__)


def retrieve_audio(
    audio_file: str | Path, model: Literal["local", "openai"] = "local"
) -> str:
    """
    Wrapper script; has option of requesting openai instead of local, defaults to local.
    """
    from Siphon.ingestion.audio.local_transcript import get_local_transcript
    from Siphon.ingestion.audio.openai_transcript import get_openai_transcript

    if model == "local":
        logger.info("Starting local transcription process.")
        return str(get_local_transcript(audio_file))
    elif model == "openai":
        logger.info("Starting OpenAI transcription process.")
        return get_openai_transcript(audio_file)
    else:
        raise ValueError(f"Invalid model option: {model}. Choose 'local' or 'openai'.")
