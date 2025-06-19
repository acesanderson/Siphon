from pathlib import Path
from pydub import AudioSegment

# Import our centralized logger - no configuration needed here!
from Siphon.logging.logging_config import get_logger

# Get logger for this module - will inherit config from retrieve_audio.py
logger = get_logger(__name__)





def convert_to_mp3(input_path: Path) -> Path:
    """
    Convert an audio file to MP3 format.

    Args:
        input_path: Path object pointing to the input audio file

    Returns:
        Path object pointing to the converted MP3 file

    Raises:
        FileNotFoundError: If the input file doesn't exist
        Exception: If conversion fails
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    formats = [
        ".wav",
        ".m4a",
        ".ogg",
        ".flac",
    ]
    if input_path.suffix.lower() not in formats:
        logger.error(
            f"Unsupported file type: {input_path.suffix}. Supported formats: {formats}"
        )
        raise ValueError(
            f"Unsupported file type: {input_path.suffix}. Supported formats: {formats}"
        )

    # Create output path with .mp3 extension
    output_path = Path(__file__).parent / "temp" / input_path.with_suffix(".mp3").name

    # Load the audio file (pydub automatically detects format)
    logger.info(f"Converting {input_path} to MP3 format.")
    audio = AudioSegment.from_file(str(input_path))

    # Export as MP3
    logger.info(f"Exporting converted audio to {output_path}.")
    audio.export(str(output_path), format="mp3")

    return output_path
