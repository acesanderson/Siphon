from Chain import Prompt, Model, Chain
from pathlib import Path

dir_path = Path(__file__).parent
prompt_file = dir_path / "system_message.jinja2"


def clean_transcript(formatted_transcript: str) -> str:
    """
    Clean up the formatted transcript using a language model.

    Args:
        formatted_transcript (str): The formatted transcript to clean up.

    Returns:
        str: Cleaned-up transcript.
    """
    # Load the prompt template
    prompt = Prompt(prompt_file.read_text())
    model = Model("gemini2.5")
    chain = Chain(model=model, prompt=prompt)
    response = chain.run(input_variables={"transcript": formatted_transcript})
    return str(response.content).strip()


if __name__ == "__main__":
    from example import example_file
    from diarize import diarize
    from transcribe import transcribe
    from combine import combine
    from format import format_transcript

    diarization_result = diarize(example_file)
    transcript_result = transcribe(example_file)
    annotated = combine(diarization_result, transcript_result)
    formatted = format_transcript(annotated, group_by_speaker=True)
    cleaned = clean_transcript(formatted)
    print(cleaned)
