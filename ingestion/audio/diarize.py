import torch
from pathlib import Path
from pyannote.audio import Pipeline

# Import our centralized logger - no configuration needed here!
from Siphon.logging.logging_config import get_logger

# Get logger for this module - will inherit config from retrieve_audio.py
logger = get_logger(__name__)


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
    logger.info(f"Processing diarization for file: {file_name}")
    diarization = pipeline(file_name)
    return diarization

