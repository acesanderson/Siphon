from pathlib import Path
from transformers import pipeline
import torch


# Transcript workflow
def transcribe(file_name: str | Path) -> str:
    """
    Use Whisper to retrieve text content + timestamps.
    """
    transcriber = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-base",
        # model="openai/whisper-large-v3",
        return_timestamps="sentence",
        device =0, 
        torch_dtype=torch.float16,
    )
    # One line transcription
    result = transcriber(file_name)
    return result


if __name__ == "__main__":
    from example import example_file

    print(transcribe(example_file))
