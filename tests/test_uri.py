from Siphon.data.SourceType import SourceType
from Siphon.tests.fixtures.assets import sample_assets

source_types = [SourceType.ARTICLE, SourceType.YOUTUBE, SourceType.FILE, SourceType.EMAIL, SourceType.GITHUB, SourceType.OBSIDIAN, SourceType.DRIVE]

# URI tests
def test_ARTICLE_URI():
    sourcetype = SourceType.ARTICLE
    from Siphon.data.URI import URI
    uri = URI.from_source(sample_assets[sourcetype.value])
    if uri is None:
        raise ValueError(f"URI for {sourcetype.value} is None, check sample_assets.")
    assert uri.source_type == sourcetype
    assert uri.source == sample_assets[sourcetype.value]
    assert len(uri.uri) > 0
    assert uri.uri == "https://mwichary.medium.com/one-hundred-and-thirty-seven-seconds-2a0a3dfbc59e"
    print(uri)

def test_YOUTUBE_URI():
    sourcetype = SourceType.YOUTUBE
    from Siphon.data.URI import URI
    uri = URI.from_source(sample_assets[sourcetype.value])
    if uri is None:
        raise ValueError(f"URI for {sourcetype.value} is None, check sample_assets.")
    assert uri.source_type == sourcetype
    assert uri.source == sample_assets[sourcetype.value]
    assert len(uri.uri) > 0
    assert uri.uri == "youtube://dQw4w9WgXcQ"
    print(uri)

def test_FILE_URI():
    sourcetype = SourceType.FILE
    from Siphon.data.URI import URI
    uri = URI.from_source(sample_assets[sourcetype.value])
    if uri is None:
        raise ValueError(f"URI for {sourcetype.value} is None, check sample_assets.")
    assert uri.source_type == sourcetype
    assert str(uri.source) == str(sample_assets[sourcetype.value])
    assert len(uri.uri) > 0
    assert uri.uri == "file:///home/fishhouses/Brian_Code/Siphon/assets/Talent Management Sources.docx"
    print(uri)

def test_GITHUB_URI():
    sourcetype = SourceType.GITHUB
    from Siphon.data.URI import URI
    uri = URI.from_source(sample_assets[sourcetype.value])
    if uri is None:
        raise ValueError(f"URI for {sourcetype.value} is None, check sample_assets.")
    assert uri.source_type == sourcetype
    assert uri.source == sample_assets[sourcetype.value]
    assert len(uri.uri) > 0
    assert uri.uri == "github://acesanderson/Siphon"
    print(uri)

# Future implementations
# def test_OBSIDIAN_URI():
#     sourcetype = SourceType.OBSIDIAN
#     from Siphon.data.URI import URI
#     uri = URI.from_source(sample_assets[sourcetype.value])
#     if uri is None:
#         raise ValueError(f"URI for {sourcetype.value} is None, check sample_assets.")
#     assert uri.source_type == sourcetype
#     assert uri.source == sample_assets[sourcetype.value]
#     assert len(uri.uri) > 0
#
# def test_EMAIL_URI():
#     sourcetype = SourceType.EMAIL
#     from Siphon.data.URI import URI
#     uri = URI.from_source(sample_assets[sourcetype.value])
#     if uri is None:
#         raise ValueError(f"URI for {sourcetype.value} is None, check sample_assets.")
#     assert uri.source_type == sourcetype
#     assert uri.source == sample_assets[sourcetype.value]
#     assert len(uri.uri) > 0
#
#
# def test_DRIVE_URI():
#     sourcetype = SourceType.DRIVE
#     from Siphon.data.URI import URI
#     uri = URI.from_source(sample_assets[sourcetype.value])
#     if uri is None:
#         raise ValueError(f"URI for {sourcetype.value} is None, check sample_assets.")
#     assert uri.source_type == sourcetype
#     assert uri.source == sample_assets[sourcetype.value]
#     assert len(uri.uri) > 0

