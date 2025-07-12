from Siphon.data.Context import Context
from Siphon.data.SourceType import SourceType
from Siphon.data.Extensions import Extensions
from Siphon.data.URI import URI
from typing import override


class DocContext(Context):
    sourcetype: SourceType = SourceType.DOC

    @override
    @classmethod
    def from_uri(cls, uri: "DocURI") -> "DocContext":  # type: ignore
        """
        Create a DocContext from a URI.
        """
        from Siphon.uri.classes.doc_uri import DocURI

        if not isinstance(uri, DocURI):
            raise TypeError("Expected uri to be an instance of DocURI.")

        from markitdown import MarkItDown
        from pathlib import Path

        file_path = Path(uri.source)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not file_path.suffix.lower() in Extensions["Doc"]:
            raise ValueError(
                f"File type not supported for MarkItDown: {file_path.suffix}"
            )
        # Do the conversion
        md = MarkItDown()
        llm_context = md.convert(file_path)
        return cls(context=str(llm_context))
