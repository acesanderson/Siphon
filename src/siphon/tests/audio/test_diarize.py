from siphon.ingestion.audio.diarize import diarize
from siphon.tests.fixtures.example_files import example_audio_file

diarized = diarize(example_audio_file)
print(diarized)
