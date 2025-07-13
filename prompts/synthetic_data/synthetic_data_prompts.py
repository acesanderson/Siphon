"""
This module dynamically loads all SyntheticData prompts for each SourceType defined in the Siphon.data.SourceType enum.
"""
from Siphon.data.SourceType import SourceType
from pathlib import Path

synthetic_data_prompts_dir = Path(__file__).parent
prompts = synthetic_data_prompts_dir.glob("*.jinja2")

SyntheticDataPrompts = []
for sourcetype in SourceType:
    stem = sourcetype.value.lower()
    title_prompt = synthetic_data_prompts_dir / f"{stem}_title.jinja2"
    description_prompt = synthetic_data_prompts_dir / f"{stem}_description.jinja2"
    summary_prompt = synthetic_data_prompts_dir / f"{stem}_summary.jinja2"
    if not title_prompt.exists() or not description_prompt.exists() or not summary_prompt.exists():
        raise FileNotFoundError(
            f"Missing prompt files for {sourcetype.name}. "
            f"Expected: {title_prompt}, {description_prompt}, {summary_prompt}"
        )
    SyntheticDataPrompts.append({
        "stem": stem,
        "title_prompt": title_prompt,
        "description_prompt": description_prompt,
        "summary_prompt": summary_prompt
    })
