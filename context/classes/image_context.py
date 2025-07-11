from Siphon.data.Context import Context
from Siphon.data.SourceType import SourceType
from Siphon.data.URI import URI
from typing import override


class ImageContext(Context):
    sourcetype: SourceType = SourceType.IMAGE

    @override
    @classmethod
    def from_uri(cls, uri: "ImageURI") -> "ImageContext":  # type: ignore
        """
        Create an ImageContext object from a URI object.
        """
        from Siphon.uri.classes.image_uri import ImageURI

        if not isinstance(uri, ImageURI):
            raise TypeError("Expected uri to be an instance of ImageURI.")

        from Siphon.ingestion.image.retrieve_image import retrieve_image

        image_description = retrieve_image(uri.source, model="gpt-4.1-mini")
        assert (
            isinstance(image_description, str) and len(image_description) > 0
        ), "The image description should be a non-empty string."
        return cls(context=image_description)
