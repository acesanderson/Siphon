from Siphon.data.Context import Context
from Siphon.data.SourceType import SourceType


class GitHubContext(Context):
    sourcetype: SourceType = SourceType.GITHUB
