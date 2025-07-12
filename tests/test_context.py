import pytest
from Siphon.data.URI import URI
from Siphon.tests.fixtures.assets import sample_assets
from Siphon.ingestion.retrieve import retrieve_llm_context

assets_path = sample_assets["assets_path"]
filetypes = sample_assets["filetypes"]
sourcetypes = {
    k: v for k, v in sample_assets.items() if k not in ("assets_path", "filetypes")
}


@pytest.mark.parametrize("sourcetype", list(sourcetypes.keys()))
def test_context_sourcetype(sourcetype):
    source = sourcetypes[sourcetype]
    uri = URI.from_source(source)
    assert uri is not None, f"URI could not be created for sourcetype '{sourcetype}'"
    llm_context = retrieve_llm_context(uri)
    assert llm_context, f"Failed to retrieve llm_context for '{sourcetype}'"
    assert len(llm_context) > 0, f"llm_context is empty for '{sourcetype}'"


@pytest.mark.parametrize("filetype", list(filetypes.keys()))
def test_context_filetype(filetype):
    source = filetypes[filetype]
    uri = URI.from_source(source)
    assert uri is not None, f"URI could not be created for filetype '{filetype}'"
    llm_context = retrieve_llm_context(uri)
    assert llm_context, f"Failed to retrieve llm_context for '{filetype}'"
    assert len(llm_context) > 0, f"llm_context is empty for '{filetype}'"
