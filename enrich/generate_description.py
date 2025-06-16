from pathlib import Path

dir_path = Path(__file__).parent
prompts_dir = dir_path.parent / "prompts"
title_prompt_file = prompts_dir / "enrich_description.jinja2"

print(title_prompt_file.read_text())
