from Siphon.context.classes.text_context import TextContext
from Siphon.data.types.SourceType import SourceType
from Siphon.data.URI import URI
from Siphon.logs.logging_config import get_logger
from typing import override, Literal

logger = get_logger(__name__)


class AudioContext(TextContext):
    """
    Context class for handling audio files.
    Inherits from TextContext to provide common functionality; from_uri, _validate_uri, and _get_metadata work under the hood.
    """

    sourcetype: SourceType = SourceType.AUDIO

    @override
    @classmethod
    def _get_context(cls, uri: URI, model: Literal["local", "cloud"]) -> str:
        from pathlib import Path

        audio_file = Path(uri.source)
        from Siphon.ingestion.audio.retrieve_audio import retrieve_audio

        logger.info("Starting transcription process.")
        llm_context = retrieve_audio(audio_file, model=model)
        return llm_context
