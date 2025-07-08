from Siphon.data.Context import Context
from Siphon.data.SourceType import SourceType


class DriveContext(Context):
    sourcetype: SourceType = SourceType.DRIVE
