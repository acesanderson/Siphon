from pathlib import Path


dir_path = Path(__file__).parent
prompts_dir = dir_path.parent.parent / "prompts"
format_prompt_file = prompts_dir / "format_transcript.jinja2"


def format_youtube(transcript: str, preferred_model: str = "claude") -> str:
    """
    This function takes a raw transcript and formats it.
    """
    from Chain import Model, Prompt, Chain

    model = Model(preferred_model)
    prompt = Prompt(format_prompt_file.read_text())
    chain = Chain(prompt=prompt, model=model)
    response = chain.run(input_variables={"transcript": transcript}, verbose=True)
    return str(response.content)
