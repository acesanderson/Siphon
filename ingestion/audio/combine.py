# Import our centralized logger - no configuration needed here!
from Siphon.logs.logging_config import get_logger

# Get logger for this module - will inherit config from retrieve_audio.py
logger = get_logger(__name__)


def combine(diarization_result, transcript_result):
    """
    Combine diarization and transcription results into an annotated transcript.

    Args:
        diarization_result: pyannote diarization output
        transcript_result: transformers transcription output with word timestamps

    Returns:
        list: List of dictionaries with word, speaker, start_time, end_time
    """
    # Extract word-level data from transcript
    words = transcript_result["chunks"]

    # Convert diarization to list of (start, end, speaker) tuples
    logger.info("Extracting diarization segments...")
    diarization_segments = []
    for turn, _, speaker in diarization_result.itertracks(yield_label=True):
        diarization_segments.append((turn.start, turn.end, speaker))

    # Align words with speakers
    logger.info("Aligning words with speakers...")
    annotated_transcript = []

    for word_data in words:
        try:
            word_text = word_data["text"].strip()
            word_start, word_end = word_data["timestamp"]

            # Find speaker for this word using midpoint timestamp
            word_midpoint = (word_start + word_end) / 2
            speaker = find_speaker_at_time(word_midpoint, diarization_segments)

            annotated_transcript.append(
                {
                    "word": word_text,
                    "speaker": speaker,
                    "start_time": word_start,
                    "end_time": word_end,
                }
            )
        except:
            print("SINGLE ERROR")

    return annotated_transcript


def find_speaker_at_time(timestamp, diarization_segments):
    """
    Find which speaker is talking at a given timestamp.

    Args:
        timestamp: Time in seconds
        diarization_segments: List of (start, end, speaker) tuples

    Returns:
        str: Speaker label or "Unknown"
    """
    for start, end, speaker in diarization_segments:
        if start <= timestamp <= end:
            return speaker
    return "Unknown"
