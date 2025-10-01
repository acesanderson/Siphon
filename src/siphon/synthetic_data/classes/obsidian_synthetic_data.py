from siphon.data.type_definitions.source_type import SourceType
from siphon.synthetic_data.classes.text_synthetic_data import TextSyntheticData


class ObsidianSyntheticData(TextSyntheticData):
    """
    AI-generated enrichments, applied as a "finishing step" to the content.
    """

    sourcetype: SourceType = SourceType.OBSIDIAN
