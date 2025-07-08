from Siphon.data.Context import Context
from Siphon.data.SourceType import SourceType


class EmailContext(Context):
    sourcetype: SourceType = SourceType.EMAIL
