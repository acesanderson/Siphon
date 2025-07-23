"""
Inherit from this one if you don't need custom logic.
"""

from Siphon.data.Context import Context
from Siphon.data.types.SourceType import SourceType
from Siphon.data.SyntheticData import SyntheticData
from typing import override


class TextSyntheticData(SyntheticData):
    """
    AI-generated enrichments, applied as a "finishing step" to the content.
    """

    sourcetype: SourceType = SourceType.TEXT

    @override
    @classmethod
    def from_context(cls, context: Context) -> "TextSyntheticData":
        """
        Create a TextSyntheticData instance from a Context object.
        """
        cls._validate_context(context)
        prompt_templates: dict = cls._source_prompts(context=context)
        rendered_prompts: list[str] = cls._render_prompts(
            context=context, prompt_templates=prompt_templates
        )
        # Run async chains
        from Chain import AsyncChain, ModelAsync
        from rich.console import Console

        ModelAsync._console = Console()
        model = ModelAsync("gemini2.5")
        chain = AsyncChain(model=model)
        responses = chain.run(prompt_strings=rendered_prompts)
        # Create the TextSyntheticData instance
        title = responses[0].message.content.strip()
        description = responses[1].message.content.strip()
        summary = responses[2].message.content.strip()
        return cls(
            sourcetype=SourceType.TEXT,
            title=title,
            description=description,
            summary=summary,
        )

    @classmethod
    def _validate_context(cls, context: Context) -> None:
        """
        Validate the context for TextSyntheticData.
        """
        assert cls.__name__.replace(
            "SyntheticData", ""
        ) == context.__class__.__name__.replace("Context", ""), (
            f"Expected context type {cls.__name__.replace('SyntheticData', '')}Context, "
            f"got {context.__class__.__name__}."
        )
        return

    @classmethod
    def _source_prompts(cls, context: Context) -> dict:
        """
        Retrieve prompt templates.
        """
        from Siphon.prompts.synthetic_data_prompts import (
            SyntheticDataPrompts,
        )

        stem = context.__class__.__name__.replace("Context", "").lower()

        for syntheticdataprompt in SyntheticDataPrompts:
            if stem == syntheticdataprompt["stem"].lower():
                return syntheticdataprompt
        raise ValueError(f"No prompt templates found for context type {stem}.")

    @classmethod
    def _render_prompts(cls, context: Context, prompt_templates: dict) -> list[str]:
        """
        Render the prompts using the context.
        """
        from jinja2 import Template

        # Turn the prompt templates into a list, excluding the stem.
        template_list = []
        template_list.append(prompt_templates["title_prompt"])
        template_list.append(prompt_templates["description_prompt"])
        template_list.append(prompt_templates["summary_prompt"])
        # Render each template with the context data.
        rendered_prompts = []
        for template in template_list:
            jinja_template = Template(template.read_text())
            rendered_prompt = jinja_template.render(
                context=context.model_dump_json(indent=2)
            )
            rendered_prompts.append(rendered_prompt)
        return rendered_prompts
