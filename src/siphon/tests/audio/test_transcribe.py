from siphon.tests.fixtures.example_files import example_audio_file
from siphon.ingestion.audio.transcribe import transcribe

transcription = transcribe(example_audio_file)
print(transcription)
