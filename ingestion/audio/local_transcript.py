"""
Annotated transcripts require several steps, and state of the art for open source solutions is this approach:
- diarize the audio (identified speakers + timestamps)
- transcribe the audio (text content + timestamps)
- align the two results (match time stamps)
- format the results for display
- clean up the transcript (with LLM call)
"""

from Siphon.ingestion.audio.transcribe import transcribe
from Siphon.ingestion.audio.diarize import diarize
from Siphon.ingestion.audio.combine import combine
from Siphon.ingestion.audio.format import format_transcript
from Siphon.ingestion.audio.convert import convert_to_mp3
from pathlib import Path

# Import our centralized logger - no configuration needed here!
from Siphon.logs.logging_config import get_logger

# Get logger for this module - will inherit config from retrieve_audio.py
logger = get_logger(__name__)

# Example file
dir_path = Path(__file__).parent
assets_dir = dir_path.parent / "assets"
allhands_file = assets_dir / "allhands.mp3"


def get_local_transcript(file_path: Path | str) -> str | None:
    """
    Converts audio file to a format suitable for processing.
    """
    converted = False
    if isinstance(file_path, str):
        file_path = Path(file_path)
    if not file_path.suffix.lower() == ".mp3":
        logger.info(f"Converting {file_path} to MP3 format for processing.")
        # Convert to MP3 if not already in that format
        file_path = convert_to_mp3(file_path)
        converted = True
    if file_path.exists() and file_path.suffix.lower() == ".mp3":
        logger.info(f"Processing file: {file_path}")
        # Diarize
        logger.info("Starting diarization...")
        diarization_result = diarize(str(file_path))
        # Transcribe
        logger.info("Starting transcription...")
        transcript_result = transcribe(str(file_path))
        # Combine diarization and transcription results by timestamps
        logger.info("Combining diarization and transcription results...")
        annotated = combine(diarization_result, transcript_result)
        # Format for display with a dedicate LLM call
        logger.info("Formatting transcript for readability...")
        readable_transcript = format_transcript(annotated, group_by_speaker=True)
        if converted:
            logger.info("Cleaning up temporary MP3 file created during conversion.")
            # Clean up the temporary MP3 file if it was created
            file_path.unlink(missing_ok=True)
        return readable_transcript
    else:
        if converted:
            # Clean up the temporary MP3 file if it was created
            logger.info("Cleaning up temporary MP3 file created during conversion.")
            file_path.unlink(missing_ok=True)
