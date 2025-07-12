import torch
from pathlib import Path
from pyannote.audio import Pipeline

# Import our centralized logger - no configuration needed here!
from Siphon.logs.logging_config import get_logger

# Get logger for this module - will inherit config from retrieve_audio.py
logger = get_logger(__name__)
# Add this to your diarize.py
import torch
import warnings


def get_safe_device():
    """Get a device that actually works, falling back to CPU if GPU has issues"""
    if not torch.cuda.is_available():
        return torch.device("cpu")

    try:
        # Test if GPU operations actually work
        test_tensor = torch.tensor([1.0]).cuda()
        test_conv = torch.nn.Conv1d(1, 1, 3).cuda()
        test_input = torch.randn(1, 1, 10).cuda()
        _ = test_conv(test_input)
        return torch.device("cuda")
    except RuntimeError as e:
        if "no kernel image" in str(e) or "sm_120" in str(e):
            warnings.warn("RTX 5090 not yet supported by PyTorch. Using CPU for now.")
            return torch.device("cpu")
        raise e


# Diarization workflow
def diarize(file_name: str | Path) -> str:
    """
    Use Pyannote to identify speakers + timestamps.
    """
    # Load the pipeline
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1")
    device = get_safe_device()
    pipeline.to(device)
    # Move the pipeline to GPU (CUDA)
    print(f"Using device: {device}")
    # Apply the pipeline to the audio file
    logger.info(f"Processing diarization for file: {file_name}")
    diarization = pipeline(file_name)
    return diarization
