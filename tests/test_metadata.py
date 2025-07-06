from Siphon.data.SourceType import SourceType
from Siphon.data.URI import URI
from Siphon.data.Metadata import Metadata, FileMetadata, ArticleMetadata, YouTubeMetadata, EmailMetadata, GitHubMetadata, ObsidianMetadata
from Siphon.tests.fixtures.assets import sample_assets

source_types = [SourceType.ARTICLE, SourceType.YOUTUBE, SourceType.FILE, SourceType.EMAIL, SourceType.GITHUB, SourceType.OBSIDIAN, SourceType.DRIVE]

# URI tests
def test_FILE_METADATA():
    sourcetype = SourceType.FILE
    source = sample_assets[sourcetype.value]
    uri = URI.from_source(source)
    if not uri:
        raise ValueError(f"URI for {sourcetype.value} is None, check sample_assets.")
    metadata = Metadata.from_uri(uri)
    if uri is None:
        raise ValueError(f"URI for {sourcetype.value} is None, check sample_assets.")
    assert metadata is not None
    assert isinstance(metadata, FileMetadata)

def test_ARTICLE_METADATA():
    sourcetype = SourceType.ARTICLE
    source = sample_assets[sourcetype.value]
    uri = URI.from_source(source)
    if not uri:
        raise ValueError(f"URI for {sourcetype.value} is None, check sample_assets.")
    metadata = Metadata.from_uri(uri)
    if uri is None:
        raise ValueError(f"URI for {sourcetype.value} is None, check sample_assets.")
    assert metadata is not None
    assert isinstance(metadata, ArticleMetadata)


# def test_YOUTUBE_METADATA():
#     sourcetype = SourceType.YOUTUBE
#
# def test_GITHUB_METADATA():
#     sourcetype = SourceType.GITHUB
#
# Future implementations
# def test_OBSIDIAN_URI():
#     sourcetype = SourceType.OBSIDIAN

# def test_EMAIL_URI():
#     sourcetype = SourceType.EMAIL

#
# def test_DRIVE_URI():
#     sourcetype = SourceType.DRIVE

