from openai import OpenAI
from pathlib import Path
import os

api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=api_key)


def transcribe_with_openai(audio_file: str | Path):
    """
    Use the transcriptions API endpoint.
    We didn't implement this in Chain since it's really tied to a transcription use case.
    """
    if isinstance(audio_file, str):
        audio_file = Path(audio_file)
    extension = audio_file.suffix.lower()
    if extension[1:] not in ["mp3", "wav"]:
        raise ValueError("Wrong extension; whisper only handles mp3 and wav.")
    else:
        with open(audio_file, "rb") as f:
            transcript = openai_client.audio.transcriptions.create(
                file=f,
                model="whisper-1",
            )
    return transcript.text


if __name__ == "__main__":
    from example import example_file

    transcript = transcribe_with_openai(example_file)
    print(transcript)
