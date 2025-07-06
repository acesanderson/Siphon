"""
Goes through each SourceType and extension to creating a ProcessedContent doc.
"""

from Siphon.tests.fixtures.assets import sample_assets
from Siphon.main.siphon import siphon
from Siphon.cli.cli_params import CLIParams
from Siphon.data.ProcessedContent import ProcessedContent

assets_path = sample_assets.pop("assets_path")
filetypes = sample_assets.pop("filetypes")
sourcetypes = sample_assets

def test_integration_sourcetypes():
    """
    Test the integration of all source types and file extensions.
    """
    for sourcetype in sourcetypes.keys():
        cli_params = CLIParams(
            source=str(sample_assets[sourcetype])
        )
        if not cli_params:
            raise ValueError(f"CLIParams could not be created for {sourcetype} with source {sample_assets[sourcetype]}")
        assert isinstance(cli_params, CLIParams), f"CLIParams is not an instance of CLIParams for {sourcetype} with source {sample_assets[sourcetype]}"
        processed_content = siphon(cli_params)
        assert isinstance(processed_content, ProcessedContent)

def test_integration_filetypes():
    """
    Test the integration of all file types.
    """
    for filetype in filetypes.keys():
        cli_params = CLIParams(
            source=str(filetypes[filetype]),
        )
        if not cli_params:
            raise ValueError(f"CLIParams could not be created for filetype {filetype} with source {sample_assets['assets_path']}")
        assert isinstance(cli_params, CLIParams), f"CLIParams is not an instance of CLIParams for filetype {filetype} with source {sample_assets['assets_path']}"
        processed_content = siphon(cli_params)
        assert isinstance(processed_content, ProcessedContent)


