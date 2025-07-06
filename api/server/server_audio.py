"""
This adapts our transcription code to work with the ContextCall object.
TBD:
- allow progress tracking (at least for steps within the transcription process).
- allow rough estimation of time to completion.
"""

from Siphon.data.ContextCall import ContextCall
from Siphon.ingestion.audio.audio import get_transcript
from Siphon.ingestion.audio.convert import convert_to_mp3
from pathlib import Path
import base64, tempfile


def transcribe_ContextCall(context_call: ContextCall) -> str:
    """
    Transcribe audio from a ContextCall object and return the transcript.
    This is a very minimal implementation -- we send only file extension and base64 data.
    """
    # Decode base64 data to bytes
    base64_bytes = base64.b64decode(context_call.base64_data)
    # Create a temporary file path
    temp_file = tempfile.NamedTemporaryFile(
        delete=False, suffix=f".{context_call.extension}"
    )
    temp_file.write(base64_bytes)
    temp_file.close()
    temp_path = Path(temp_file.name)
    converted = False
    # See if we need to convert to mp3.
    if context_call.extension != ".mp3":
        # Convert to MP3 if not already in that format
        temp_mp3_file = convert_to_mp3(temp_path)  # type: ignore
        converted = True
    try:
        # Transcribe the audio file
        transcript = get_transcript(temp_path)
        if not transcript:
            raise ValueError("No transcript found for the audio file.")
        return str(transcript)
    finally:
        # Clean up the temporary file(s)
        temp_path.unlink(missing_ok=True)
        if converted:
            temp_mp3_file.unlink(missing_ok=True)  # type: ignore


if __name__ == "__main__":
    from Siphon.data.ContextCall import create_ContextCall_from_file

    dir_path = Path(__file__).parent
    file_path = dir_path.parent / "assets" / "allhands.m4a"
    context_call = create_ContextCall_from_file(file_path)
    print(context_call)
    transcript = transcribe_ContextCall(context_call)
    print(transcript)
