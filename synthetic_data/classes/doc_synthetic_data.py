from Siphon.data.Context import Context
from Siphon.synthetic_data.classes.text_synthetic_data import TextSyntheticData
from Siphon.data.types.SourceType import SourceType
from Siphon.data.SyntheticData import SyntheticData
from typing import override


class DocSyntheticData(TextSyntheticData):
    """
    AI-generated enrichments, applied as a "finishing step" to the content.
    Inherits from TextSyntheticData to leverage text-based synthetic data generation.
    """

    sourcetype: SourceType = SourceType.DOC
