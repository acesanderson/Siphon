from Siphon.data.Metadata import Metadata
from Siphon.data.URI import URI
from typing import Optional


class FileMetadata(Metadata):
    file_path: str | Path
    file_size: int
    mime_type: str
    file_extension: str
    content_created_at: Optional[int]
    content_modified_at: Optional[int]

    def model_post_init(self, __context):
        """
        Coerce from Path to str.
        """
        self.file_path = str(self.file_path)

    @classmethod
    def from_uri(cls, uri: URI):
        """Factory method to create FileMetadata from a URI object."""
        from pathlib import Path
        import mimetypes

        path = Path(uri.source)
        return cls(
            file_path=str(path.resolve()),
            file_size=path.stat().st_size,
            mime_type=mimetypes.guess_type(path)[0] or "application/octet-stream",
            file_extension=path.suffix,
            content_created_at=int(path.stat().st_ctime),
            content_modified_at=int(path.stat().st_mtime),
        )

    @classmethod
    def from_dict(cls, data: dict):
        """
        Factory method to create ArticleMetadata from a dictionary.
        """
        ...
