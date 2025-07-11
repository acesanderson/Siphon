from Siphon.data.Context import Context
from Siphon.data.SourceType import SourceType
from Siphon.data.URI import URI


class ImageContext(Context):
    sourcetype: SourceType = SourceType.IMAGE

    @classmethod
    def from_uri(cls, uri: "URI") -> "ImageContext":  # type: ignore
        """
        Create an ImageContext object from a URI object.
        """
        from Siphon.ingestion.image.retrieve_image import retrieve_image

        image_description = retrieve_image(uri.source, model="gpt-3o")
        return cls(context=image_description)
