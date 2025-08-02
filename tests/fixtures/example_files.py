from pathlib import Path

dir_path = Path(__file__).parent
assets_path = dir_path.parent.parent / "assets"

example_audio_file = assets_path / "output.mp3"
example_image_file = assets_path / "dymphna.png"
example_docx_file = assets_path / "Talent Management Sources.docx"
example_ocr_file = assets_path / "ocr.png"

assert example_audio_file.exists(), "Example audio file does not exist."
assert example_image_file.exists(), "Example image file does not exist."
assert example_docx_file.exists(), "Example docx file does not exist."
