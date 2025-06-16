from pathlib import Path
from Chain import Model, Prompt, Chain

dir_path = Path(__file__).parent
prompts_dir = dir_path.parent / "prompts"
title_prompt_file = prompts_dir / "enrich_title.jinja2"

prompt = Prompt(title_prompt_file.read_text())
