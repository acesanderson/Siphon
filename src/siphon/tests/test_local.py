from siphon.cli.cli_params import CLIParams
from siphon.tests.fixtures.assets import sample_assets
from siphon.main.siphon import siphon


# def test_synthetic_data_local():
# """Test that SyntheticData can be generated in local mode."""
sample_asset = sample_assets["filetypes"]["pdf"]
params = CLIParams(
    source=str(sample_asset),
    cache_options="r",
    local=True,  # Local mode
)

processed_content = siphon(params)

print(processed_content)
