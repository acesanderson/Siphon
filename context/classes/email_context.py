from Siphon.data.Context import Context
from Siphon.data.types.SourceType import SourceType
from Siphon.data.URI import URI
from typing import override


class EmailContext(Context):
    sourcetype: SourceType = SourceType.EMAIL

    @override
    @classmethod
    def from_uri(cls, uri: "EmailURI") -> "EmailContext":  # type: ignore
        """
        Create an EmailContext from a URI.
        """
        from Siphon.uri.classes.email_uri import EmailURI

        if not isinstance(uri, EmailURI):
            raise TypeError("Expected uri to be an instance of EmailURI.")

        raise NotImplementedError(
            "EmailContext.from_uri is not implemented. EmailContext is not supported yet."
        )
