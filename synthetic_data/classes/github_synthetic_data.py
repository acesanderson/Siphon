from Siphon.data.SourceType import SourceType
from Siphon.synthetic_data.classes.text_synthetic_data import TextSyntheticData


class GitHubSyntheticData(TextSyntheticData):
    """
    AI-generated enrichments, applied as a "finishing step" to the content.
    """

    sourcetype: SourceType = SourceType.GITHUB
