import torch
from pathlib import Path
from pyannote.audio import Pipeline


# Diarization workflow
def diarize(file_name: str | Path) -> str:
    """
    Use Pyannote to identify speakers + timestamps.
    """
    # Load the pipeline
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1")
    # Move the pipeline to GPU (CUDA)
    pipeline.to(torch.device("cuda"))
    # Apply the pipeline to the audio file
    diarization = pipeline(file_name)
    return diarization


if __name__ == "__main__":
    from example import example_file

    print(diarize(example_file))
