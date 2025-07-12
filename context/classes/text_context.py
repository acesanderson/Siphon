from Siphon.data.Context import Context
from Siphon.data.SourceType import SourceType
from Siphon.data.URI import URI
from typing import override


class TextContext(Context):
    sourcetype: SourceType = SourceType.TEXT

    @override
    @classmethod
    def from_uri(cls, uri: "TextURI") -> "TextContext":  # type: ignore
        """
        Create a TextContext from a URI.
        """
        from Siphon.uri.classes.text_uri import TextURI

        if not isinstance(uri, TextURI):
            raise TypeError("Expected uri to be an instance of TextURI.")

        with open(uri.source, "r") as file:
            text_content = file.read()
        return cls(context=text_content)
