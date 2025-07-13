"""
Inherit from this one if you don't need custom logic.
"""

from Siphon.data.Context import Context
from Siphon.data.SourceType import SourceType
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
        breakpoint()
        prompt_templates = cls._source_prompts()
        rendered_prompts = cls._render_prompts(
            context=context, prompt_templates=prompt_templates
        )
        # Run async chains
        from Chain import AsyncChain, ModelAsync
        model = ModelAsync("gpt3")
        chain = AsyncChain(model=model)
        responses = chain.run(prompt_strings=rendered_prompts)

    @classmethod
    def _validate_context(cls, context: Context) -> None:
        """
        Validate the context for TextSyntheticData.
        """
        assert cls.__name__.replace("SyntheticData", "") == context.__class__.__name__.replace("Context", ""), (
            f"Expected context type {cls.__name__.replace('SyntheticData', '')}Context, "
            f"got {context.__class__.__name__}."
        )
        return

    @classmethod
    def _source_prompts(cls) -> list[str]:
        """
        Retrieve prompt templates.
        """
        from Siphon.prompts.synthetic_data.synthetic_data_prompts import SyntheticDataPrompts

        for syntheticdataprompt in SyntheticDataPrompts:
            if cls.__name__.replace("SyntheticData", "").lower() in syntheticdataprompt.name:
                return syntheticdataprompt.prompts


    @classmethod
    def _render_prompts(cls, context: Context, prompt_templates: list[str]) -> list[str]:
        """
        Render the prompts using the context.
        """
        rendered_prompts = []
        for template in prompt_templates:
            rendered_prompt = template.format(context.model_dump_json(indent=2))
            rendered_prompts.append(rendered_prompt)
        return rendered_prompts

