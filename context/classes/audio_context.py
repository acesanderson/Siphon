from Siphon.data.Context import Context
from Siphon.data.SourceType import SourceType


class AudioContext(Context):
    sourcetype: SourceType = SourceType.AUDIO
