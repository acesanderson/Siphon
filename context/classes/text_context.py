from Siphon.data.Context import Context
from Siphon.data.SourceType import SourceType
from Siphon.data.URI import URI
from typing import override


class TextContext(Context):
    sourcetype: SourceType = SourceType.TEXT

    @override
    @classmethod
    def from_uri(cls, uri: URI) -> "TextContext":  # type: ignore
        """
        Create a TextContext from a URI.
        """
        with open(uri.source, "r") as file:
            text_content = file.read()
        return cls(context=text_content)
