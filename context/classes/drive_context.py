from Siphon.data.Context import Context
from Siphon.data.SourceType import SourceType
from Siphon.data.URI import URI
from typing import override


class DriveContext(Context):
    sourcetype: SourceType = SourceType.DRIVE

    @override
    @classmethod
    def from_uri(cls, uri: "DriveURI") -> "DriveContext":  # type: ignore
        """
        Create a DriveContext from a URI.
        """
        from Siphon.uri.classes.drive_uri import DriveURI

        if not isinstance(uri, DriveURI):
            raise TypeError("Expected uri to be an instance of DriveURI.")

        raise NotImplementedError("DriveContext.from_uri is not implemented yet")
