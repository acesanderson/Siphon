from Siphon.data.Context import Context
from Siphon.data.SourceType import SourceType


class ArticleContext(Context):
    sourcetype: SourceType = SourceType.ARTICLE
