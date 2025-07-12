from Siphon.data.Context import Context
from Siphon.data.SourceType import SourceType
from Siphon.data.URI import URI
from Siphon.logs.logging_config import get_logger
from typing import override, Literal

logger = get_logger(__name__)


class AudioContext(Context):
    sourcetype: SourceType = SourceType.AUDIO

    @override
    @classmethod
    def from_uri(cls, uri: "AudioURI", model: Literal["local", "openai"] = "openai") -> "AudioContext":  # type: ignore
        """
        Create a AudioContext from a URI.
        """

        from Siphon.uri.classes.audio_uri import AudioURI

        if not isinstance(uri, AudioURI):
            raise TypeError("Expected uri to be an instance of AudioURI.")

        from Siphon.ingestion.audio.local_transcript import get_local_transcript
        from Siphon.ingestion.audio.openai_transcript import get_openai_transcript
        from pathlib import Path

        audio_file = Path(uri.source)

        if model == "local":
            logger.info("Starting local transcription process.")
            llm_context = get_local_transcript(audio_file)
        elif model == "openai":
            logger.info("Starting OpenAI transcription process.")
            llm_context = get_openai_transcript(audio_file)
        else:
            raise ValueError(
                f"Invalid model option: {model}. Choose 'local' or 'openai'."
            )
        assert (
            isinstance(llm_context, str) and len(llm_context) > 0
        ), "The transcription result should be a non-empty string."
        return cls(context=llm_context)
