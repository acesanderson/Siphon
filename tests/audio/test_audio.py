from Siphon.tests.fixtures.example_files import example_audio_file
from Siphon.ingestion.audio.local_transcript import get_local_transcript
from Siphon.ingestion.audio.openai_transcript import get_openai_transcript
from pathlib import Path

dir_path = Path(__file__).parent
assets_dir = dir_path.parent.parent / "assets"

# audio_file = assets_dir / "learningmktplace6-23-2025.mp3"
audio_file = assets_dir / "demos.mp3"

# transcript = get_openai_transcript(example_audio_file)
# print(transcript)

transcript = get_local_transcript(audio_file)
print(transcript)
