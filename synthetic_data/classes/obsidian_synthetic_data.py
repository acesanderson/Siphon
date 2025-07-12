from Siphon.data.Context import Context
from Siphon.data.SourceType import SourceType
from Siphon.data.SyntheticData import SyntheticData
from typing import override


class ObsidianSyntheticData(SyntheticData):
    """
    AI-generated enrichments, applied as a "finishing step" to the content.
    """

    sourcetype: SourceType = SourceType.OBSIDIAN

    @override
    @classmethod
    def from_context(cls, context: Context) -> "ObsidianSyntheticData": ...
