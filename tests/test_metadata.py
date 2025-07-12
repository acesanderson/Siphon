import pytest
from Siphon.data.Metadata import (
    Metadata,
    FileMetadata,
    ArticleMetadata,
    YouTubeMetadata,
    GitHubMetadata,
    ObsidianMetadata,
    DriveMetadata,
    EmailMetadata,
)
from Siphon.data.SourceType import SourceType
from Siphon.data.URI import URI
from Siphon.tests.fixtures.assets import sample_assets

sources = {
    SourceType.FILE: FileMetadata,
    SourceType.ARTICLE: ArticleMetadata,
    SourceType.YOUTUBE: YouTubeMetadata,
    SourceType.GITHUB: GitHubMetadata,
    SourceType.OBSIDIAN: ObsidianMetadata,
    SourceType.DRIVE: DriveMetadata,
    SourceType.EMAIL: EmailMetadata,
}


# URI tests
@pytest.mark.parametrize("source", sources.items())
def test_metadata(source):
    sourcetype = source[0]
    metadata_class = source[1]
    source = sample_assets[sourcetype.value]
    uri = URI.from_source(source)
    if not uri:
        raise ValueError(f"URI for {sourcetype.value} is None, check sample_assets.")
    metadata = Metadata.from_uri(uri)
    if uri is None:
        raise ValueError(f"URI for {sourcetype.value} is None, check sample_assets.")
    assert metadata is not None
    assert isinstance(metadata, metadata_class)
