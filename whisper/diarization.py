"""https://huggingface.co/pyannote/speaker-diarization-3.1"""

from pyannote.audio import Pipeline
import os
import torch
from pathlib import Path

dir_path = Path(__file__).parent
asset_dir = dir_path.parent / "assets"
MP3_FILE = str(asset_dir / "output.mp3")

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACEHUB_API_TOKEN")
if not HUGGINGFACE_API_KEY:
    print("API KEY not found")

# instantiate the pipeline
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=HUGGINGFACE_API_KEY,
)

pipeline.to(torch.device("cuda"))

# run the pipeline on an audio file
diarization = pipeline(MP3_FILE)

# dump the diarization output to disk using RTTM format
with open("audio.rttm", "w") as rttm:
    diarization.write_rttm(rttm)
