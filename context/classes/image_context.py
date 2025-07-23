from Siphon.context.classes.text_context import TextContext
from Siphon.data.types.SourceType import SourceType
from Siphon.data.URI import URI
from typing import override, Literal


class ImageContext(TextContext):
    """
    Context class for handling image files.
    Inherits from TextContext to provide common functionality; from_uri, _validate_uri, and _get_metadata work under the hood.
    """

    sourcetype: SourceType = SourceType.IMAGE

    @override
    @classmethod
    def _get_context(cls, uri: URI, model: Literal["local", "cloud"] = "cloud") -> str:
        """
        Get the context from the image file.
        This method is overridden to provide specific functionality for image files.
        """
        _ = model

        from Siphon.ingestion.image.retrieve_image import retrieve_image

        image_description = retrieve_image(uri.source, model=model)
        return image_description
