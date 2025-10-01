from siphon.data.context import Context
from siphon.data.types.source_type import SourceType
from siphon.data.uri import URI
from typing import override


class ObsidianContext(Context):
    sourcetype: SourceType = SourceType.OBSIDIAN

    @override
    @classmethod
    def from_uri(cls, uri: "ObsidianURI") -> "ObsidianContext":  # type: ignore
        """
        Create an ObsidianContext from a URI.
        """
        from siphon.uri.classes.obsidian_uri import ObsidianURI

        if not isinstance(uri, ObsidianURI):
            raise TypeError("Expected uri to be an instance of ObsidianURI.")
        raise NotImplementedError("ObsidianContext.from_uri is not implemented yet")
