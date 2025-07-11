"""
I've spent arguably too much time scaffolding up a complex pipeline of:
source: str -> URI -> Metadata -> Context -> SyntheticData -> ProcessedContent

Let's get to the meat of it + make it immediately useful with a midway pipeline:
source: str -> URI -> Context -> Context.context: str

So that siphon_cli can immediately output context to stdout.

Amending siphon.py to return the above minimal pipeline, this test script will orchestrate across a subset of sourcetypes we already have an implementation for.
"""

import pytest
from Siphon.data.SourceType import SourceType
from Siphon.main.siphon import siphon
from Siphon.cli.cli_params import CLIParams
from Siphon.tests.fixtures.assets import sample_assets

# Import Chain so we can set a cache.
from Chain import Model, ChainCache

Model._chain_cache = ChainCache(db_path=".test_minimal_cache.db")

# Create our list of source types
immediately_usable_types = """
Text
Doc
Audio
Image
GitHub
YouTube
Article
""".strip().split(
    "\n"
)

immediately_usable_types = [SourceType(x) for x in immediately_usable_types]
sourcetype_assets = sample_assets["sourcetypes"]

# Just text for now
immediate_usable_types = [immediately_usable_types[0]]  # Text


@pytest.mark.parametrize("source_type", immediately_usable_types)
def test_minimal_siphon(source_type):
    """
    Test the minimal siphon pipeline for a subset of source types.
    """
    # Get the sample source for the given source type
    source = sourcetype_assets[source_type]

    # Create CLI parameters
    cli_params = CLIParams(source=str(source))

    # Run siphon and get the context
    context = siphon(cli_params)

    # Assert that context is not empty
    assert context is not None
    assert isinstance(context, str)
    assert len(context) > 0
