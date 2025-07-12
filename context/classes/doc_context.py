from Siphon.context.classes.text_context import TextContext
from Siphon.data.SourceType import SourceType
from Siphon.data.URI import URI
from typing import override, Literal


class DocContext(TextContext):
    """
    Context class for handling document files (e.g., .doc, .docx).
    Validation, and metadata inherit from TextContext.
    """
    sourcetype: SourceType = SourceType.DOC

    @override
    @classmethod
    def _get_context(cls, uri: URI, model: Literal["local", "cloud"]) -> str:  # type: ignore
        _ = model

        from markitdown import MarkItDown
        from pathlib import Path

        file_path = Path(uri.source)

        md = MarkItDown()
        llm_context = md.convert(file_path)
        return str(llm_context)

