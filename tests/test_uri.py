import pytest
from Siphon.data.SourceType import SourceType
from Siphon.tests.fixtures.assets import sample_assets
from Siphon.data.URI import URI

"""
https://mwichary.medium.com/one-hundred-and-thirty-seven-seconds-2a0a3dfbc59e
youtube://dQw4w9WgXcQ
file:///home/fishhouses/Brian_Code/Siphon/assets/Talent Management Sources.docx
github://acesanderson/Siphon
"""

sources_and_example_uris = {
    SourceType.ARTICLE: "https://mwichary.medium.com/one-hundred-and-thirty-seven-seconds-2a0a3dfbc59e",
    SourceType.YOUTUBE: "youtube://dQw4w9WgXcQ",
    SourceType.FILE: "file:///home/fishhouses/Brian_Code/Siphon/assets/Talent Management Sources.docx",
    SourceType.GITHUB: "github://acesanderson/Siphon",
    # SourceType.OBSIDIAN: "NA",
    # SourceType.DRIVE: "NA",
    # SourceType.EMAIL: "NA",
}


# URI tests
@pytest.mark.parametrize("source_and_example_uri", sources_and_example_uris.items())
def test_URI(source_and_example_uri):
    sourcetype, example_uri = source_and_example_uri
    uri = URI.from_source(sample_assets[sourcetype.value])
    if uri is None:
        raise ValueError(f"URI for {sourcetype.value} is None, check sample_assets.")
    assert uri.source_type == sourcetype
    assert str(uri.source) == str(sample_assets[sourcetype.value])
    assert len(uri.uri) > 0
    assert uri.uri == example_uri
    print(uri)
