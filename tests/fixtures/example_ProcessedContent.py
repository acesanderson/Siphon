from Siphon.data.URI import SiphonURI
from Siphon.data.SourceType import SourceType
from Siphon.data.ProcessedContent import ProcessedContent
from Siphon.data.Metadata import OnlineMetadata
from pathlib import Path
import time

dir_path = Path(__file__).parent
example_html = dir_path / "example_html.html"

# Example usage
content = ProcessedContent(
    content_id="example_content_id",
    uri=SiphonURI.from_string("http://example.com/content"),
    source_type=SourceType.ARTICLE,
    content_created_at=int(time.time()) - 7200,
    content_modified_at=int(time.time()) - 3600,
    ingested_at=int(time.time()),
    last_updated_at=int(time.time()) - 1800,
    llm_context=example_html.read_text(),
)
metadata = OnlineMetadata(
    url="http://example.com",
    html_title="Example Metadata Title",
    content_type="webpage",
)
content.metadata = metadata
