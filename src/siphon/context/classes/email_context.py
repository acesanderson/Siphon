from siphon.data.context import Context
from siphon.data.type_definitions.source_type import SourceType
from siphon.data.uri import URI
from typing import override


class EmailContext(Context):
    sourcetype: SourceType = SourceType.EMAIL

    @override
    @classmethod
    def from_uri(cls, uri: "EmailURI") -> "EmailContext":  # type: ignore
        """
        Create an EmailContext from a URI.
        """
        from siphon.uri.classes.email_uri import EmailURI

        if not isinstance(uri, EmailURI):
            raise TypeError("Expected uri to be an instance of EmailURI.")

        raise NotImplementedError(
            "EmailContext.from_uri is not implemented. EmailContext is not supported yet."
        )
