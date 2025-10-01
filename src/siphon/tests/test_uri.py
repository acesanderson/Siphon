import pytest
from siphon.tests.fixtures.assets import sample_assets
from siphon.data.type_definitions.uriSchemes import URISchemes
from siphon.data.uri import URI

sourcetypes = sample_assets["sourcetypes"]


# URI tests
@pytest.mark.parametrize("source_and_example_uri", sourcetypes.items())
def test_URI(source_and_example_uri):
    sourcetype, example_uri = source_and_example_uri
    uri = URI.from_source(sourcetypes[sourcetype])
    if uri is None:
        raise ValueError(f"URI for {sourcetype.value} is None, check sample_assets.")
    assert uri.sourcetype == sourcetype
    assert str(uri.source) == str(sourcetypes[sourcetype])
    assert len(uri.uri) > 0
    assert URISchemes[sourcetype.value] in uri.uri, (
        f"URI scheme mismatch for {sourcetype.value}"
    )
    print(uri)
