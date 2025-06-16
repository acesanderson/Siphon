from Siphon.data.URI import SiphonURI
from Siphon.data.SourceType import SourceType
from Siphon.data.ProcessedContent import ProcessedContent
from Siphon.data.Metadata import OnlineMetadata
from datetime import datetime
from pathlib import Path

dir_path = Path(__file__).parent
example_html = dir_path / "example_html.html"

# Example usage
content = ProcessedContent(
    content_id="example_content_id",
    uri=SiphonURI.from_string("http://example.com/content"),
    source_type=SourceType.ARTICLE,
    content_created_at=datetime.now(),
    content_modified_at=datetime.now(),
    ingested_at=datetime.now(),
    last_updated_at=datetime.now(),
    llm_context=example_html.read_text(),
)
metadata = OnlineMetadata(
    url ="http://example.com",
    html_title="Example Metadata Title",
    content_type="webpage",
)
content.metadata = metadata


