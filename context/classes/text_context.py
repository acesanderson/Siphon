from Siphon.data.Context import Context
from Siphon.data.types.SourceType import SourceType
from Siphon.data.URI import URI
from pathlib import Path
from typing import override, Optional, Literal


class TextContext(Context):
    """
    Context class for handling text files.
    This is also the base class for audio, image, video, and obsidian contexts.
    """

    sourcetype: SourceType = SourceType.TEXT

    # Metadata field
    file_path: str | Path
    file_size: int
    mime_type: str
    file_extension: str
    content_created_at: Optional[int]
    content_modified_at: Optional[int]

    @override
    @classmethod
    def from_uri(cls, uri: URI, model: Literal["local", "cloud"] = "cloud") -> Context:  # type: ignore
        """
        Create a Context from a URI.
        """
        if not cls._validate_uri(uri):
            raise ValueError("Invalid URI provided.")

        # Get metadata from the URI
        metadata = cls._get_metadata(uri)

        # Get context from the file
        context = cls._get_context(uri, model=model)

        # Assemble and return the Context instance
        return cls(context=context, **metadata)

    @classmethod
    def _validate_uri(cls, uri: URI) -> bool:
        """
        Validate that we received the correct subclass of URI and that the file exists.
        Inheritable by other file-based contexts like AudioContext, ImageContext, etc.
        """
        # Assert that uri class name matches the expected format
        sourcetype_value = uri.sourcetype.value
        if uri.__class__.__name__ != f"{sourcetype_value}URI":
            raise TypeError(
                f"Expected uri to be an instance of {sourcetype_value}URI, "
                f"but got {uri.__class__.__name__}."
            )

        from pathlib import Path

        if not uri.source:
            raise ValueError("URI source cannot be empty.")
        if not isinstance(uri.source, str) or isinstance(uri.source, Path):
            raise TypeError("URI source must be a string or Path object.")

        path = Path(uri.source)
        if not path.is_file():
            raise FileNotFoundError(f"The file {path} does not exist.")

        from Siphon.data.types.Extensions import Extensions

        if path.suffix not in Extensions[sourcetype_value]:
            raise ValueError(f"Unsupported file type: {path.suffix}.")
        return True

    @classmethod
    def _get_context(cls, uri: URI, model: Literal["local", "cloud"]) -> str:
        """
        Get the text content from the file.
        The most customized method for each context type.
        Model is available for audio, image, and video contexts.
        """
        _ = model

        from pathlib import Path

        path = Path(uri.source)
        if not path.is_file():
            raise FileNotFoundError(f"The file {path} does not exist.")
        with open(path, "r") as file:
            return file.read()

    @classmethod
    def _get_metadata(cls, uri: URI) -> dict:
        """
        Get metadata for the text file.
        Inheritable by other file-based contexts like AudioContext, ImageContext, etc.
        """
        from pathlib import Path
        import mimetypes

        path = Path(uri.source)
        return {
            "file_path": str(path.resolve()),
            "file_size": path.stat().st_size,
            "mime_type": mimetypes.guess_type(path)[0] or "text/plain",
            "file_extension": path.suffix,
            "content_created_at": int(path.stat().st_ctime),
            "content_modified_at": int(path.stat().st_mtime),
        }
