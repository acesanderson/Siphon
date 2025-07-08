"""
All file sourcetypes have the same metadata fields.
"""

from Siphon.metadata.classes.text_metadata import TextMetadata
from Siphon.data.SourceType import SourceType


class VideoMetadata(TextMetadata):
    sourcetype: SourceType = SourceType.VIDEO
