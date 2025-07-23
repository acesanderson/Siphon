"""
This module dynamically loads all SyntheticData prompts for each SourceType defined in the Siphon.data.types.SourceType enum.

For each sourcetype, we have a dict with the following:
- `stem`: The lowercase name of the SourceType.
- `title_prompt`: Path to the title prompt file.
- `description_prompt`: Path to the description prompt file.
- `summary_prompt`: Path to the summary prompt file.
"""

from Siphon.data.types.SourceType import SourceType
from pathlib import Path

synthetic_data_prompts_dir = Path(__file__).parent / "synthetic_data"
prompts = synthetic_data_prompts_dir.glob("*.jinja2")

SyntheticDataPrompts = []
for sourcetype in SourceType:
    stem = sourcetype.value.lower()
    title_prompt = synthetic_data_prompts_dir / f"{stem}_title.jinja2"
    description_prompt = synthetic_data_prompts_dir / f"{stem}_description.jinja2"
    summary_prompt = synthetic_data_prompts_dir / f"{stem}_summary.jinja2"
    if (
        not title_prompt.exists()
        or not description_prompt.exists()
        or not summary_prompt.exists()
    ):
        raise FileNotFoundError(
            f"Missing prompt files for {sourcetype.name}. "
            f"Expected: {title_prompt}, {description_prompt}, {summary_prompt}"
        )
    SyntheticDataPrompts.append(
        {
            "stem": stem,
            "title_prompt": title_prompt,
            "description_prompt": description_prompt,
            "summary_prompt": summary_prompt,
        }
    )
