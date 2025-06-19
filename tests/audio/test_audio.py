from Siphon.tests.fixtures.example_files import example_audio_file
from Siphon.ingestion.audio.local_transcript import get_local_transcript
from Siphon.ingestion.audio.openai_transcript import get_openai_transcript

transcript = get_openai_transcript(example_audio_file)
print(transcript)

# transcript = get_local_transcript(example_audio_file)
# print(transcript)
