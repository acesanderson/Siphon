"""
Goes through each SourceType and extension to creating a ProcessedContent doc.
"""

import pytest
from siphon.cli.cli_params import CLIParams
from siphon.data.processed_content import ProcessedContent
from siphon.main.siphon import siphon
from siphon.tests.fixtures.assets import sample_assets

assets_path = sample_assets.pop("assets_path")
filetypes = sample_assets.pop("filetypes")
sourcetypes = sample_assets


@pytest.mark.parametrize("sourcetype", list(sourcetypes.keys()))
def test_integration_sourcetypes():
    """
    Test the integration of all source types and file extensions.
    """
    cli_params = CLIParams(source=str(sample_assets[sourcetype]))
    if not cli_params:
        raise ValueError(
            f"CLIParams could not be created for {sourcetype} with source {sample_assets[sourcetype]}"
        )
    assert isinstance(cli_params, CLIParams), (
        f"CLIParams is not an instance of CLIParams for {sourcetype} with source {sample_assets[sourcetype]}"
    )
    processed_content = siphon(cli_params)
    assert isinstance(processed_content, ProcessedContent)


@pytest.mark.parametrize("filetype", list(filetypes.keys()))
def test_integration_filetypes():
    """
    Test the integration of all file types.
    """
    cli_params = CLIParams(
        source=str(filetypes[filetype]),
    )
    if not cli_params:
        raise ValueError(
            f"CLIParams could not be created for filetype {filetype} with source {sample_assets['assets_path']}"
        )
    assert isinstance(cli_params, CLIParams), (
        f"CLIParams is not an instance of CLIParams for filetype {filetype} with source {sample_assets['assets_path']}"
    )
    processed_content = siphon(cli_params)
    assert isinstance(processed_content, ProcessedContent)
