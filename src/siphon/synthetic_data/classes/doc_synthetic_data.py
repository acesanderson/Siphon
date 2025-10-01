from siphon.data.context import Context
from siphon.synthetic_data.classes.text_synthetic_data import TextSyntheticData
from siphon.data.type_definitions.source_type import SourceType
from siphon.data.synthetic_data import SyntheticData
from typing import override


class DocSyntheticData(TextSyntheticData):
    """
    AI-generated enrichments, applied as a "finishing step" to the content.
    Inherits from TextSyntheticData to leverage text-based synthetic data generation.
    """

    sourcetype: SourceType = SourceType.DOC
