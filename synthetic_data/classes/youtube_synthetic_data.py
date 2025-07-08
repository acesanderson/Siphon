from Siphon.data.Context import Context
from Siphon.data.SourceType import SourceType
from Siphon.data.SyntheticData import SyntheticData
from typing import override


class YouTubeSyntheticData(SyntheticData):
    """
    AI-generated enrichments, applied as a "finishing step" to the content.
    """

    sourcetype: SourceType = SourceType.YOUTUBE

    @override
    @classmethod
    def from_context(cls, context: Context) -> "YouTubeSyntheticData": ...
