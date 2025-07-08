from Siphon.data.Context import Context
from Siphon.data.SourceType import SourceType


class DocContext(Context):
    sourcetype: SourceType = SourceType.DOC
