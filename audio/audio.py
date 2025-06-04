"""
Annotated transcripts require several steps, and state of the art for open source solutions is this approach:
- diarize the audio (identified speakers + timestamps)
- transcribe the audio (text content + timestamps)
- align the two results (match time stamps)
- format the results for display
- clean up the transcript (with LLM call)
"""

from Siphon.audio.transcribe import transcribe
from Siphon.audio.diarize import diarize
from Siphon.audio.example import example_file
from Siphon.audio.combine import combine
from Siphon.audio.format import format_transcript
from pathlib import Path

dir_path = Path(__file__).parent
assets_dir = dir_path.parent / "assets"
allhands_file = assets_dir / "allhands.mp3"


def convert_audio(file_path: Path | str) -> str:
    """
    Converts audio file to a format suitable for processing.
    Currently, this is a placeholder function.
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)
    if not file_path.suffix.lower() == ".mp3":
        raise NotImplementedError("Only MP3 files are supported at this moment.")
    if file_path.exists() and file_path.suffix.lower() == ".mp3":
        # Diarize
        diarization_result = diarize(str(file_path))
        # Transcribe
        transcript_result = transcribe(str(allhands_file))
        # Combine diarization and transcription results by timestamps
        annotated = combine(diarization_result, transcript_result)
        # Format for display with a dedicate LLM call
        readable_transcript = format_transcript(annotated, group_by_speaker=True)
        return readable_transcript


# Example usage:
if __name__ == "__main__":
    transcript = convert_audio(example_file)
    print(transcript)
