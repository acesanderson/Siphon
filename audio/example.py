from pathlib import Path

dir_path = Path(__file__).parent
assets_dir = dir_path.parent / "assets"
example_file = str(assets_dir / "output.mp3")
