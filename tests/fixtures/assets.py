"""
Import sample_assets from the assets directory for testing and development purposes.
"""

"""
source_types = [SourceType.ARTICLE, SourceType.YOUTUBE, SourceType.FILE, SourceType.EMAIL, SourceType.GITHUB, SourceType.OBSIDIAN, SourceType.DRIVE]
"""

from pathlib import Path
from Siphon.data.SourceType import SourceType

dir_path = Path(__file__).parent
assets_path = dir_path.parent.parent / "assets"

files = """
/home/fishhouses/Brian_Code/Siphon/assets/New-Year-New-Skills-Own-Your-Career-Goals.pptx
/home/fishhouses/Brian_Code/Siphon/assets/Talent Management Sources.docx
/home/fishhouses/Brian_Code/Siphon/assets/Zscaler Professional Certificate Pitch 5-20-2025.pdf
/home/fishhouses/Brian_Code/Siphon/assets/courselist_en_US (6).xlsx
/home/fishhouses/Brian_Code/Siphon/assets/download.html
/home/fishhouses/Brian_Code/Siphon/assets/dymphna.png
/home/fishhouses/Brian_Code/Siphon/assets/ezra-transcripts.zip
/home/fishhouses/Brian_Code/Siphon/assets/monthly-cert-insights (14).csv
/home/fishhouses/Brian_Code/Siphon/assets/morris1.jpg
/home/fishhouses/Brian_Code/Siphon/assets/output.mp3
""".strip().split("\n")

sample_pptx = assets_path / "New-Year-New-Skills-Own-Your-Career-Goals.pptx"
sample_docx = assets_path / "Talent Management Sources.docx"
sample_pdf = assets_path / "Zscaler Professional Certificate Pitch 5-20-2025.pdf"
sample_xlsx = assets_path / "courselist_en_US (6).xlsx"
sample_html = assets_path / "download.html"
sample_image = assets_path / "dymphna.png"
sample_zip = assets_path / "ezra-transcripts.zip"
sample_csv = assets_path / "monthly-cert-insights (14).csv"
sample_jpg = assets_path / "morris1.jpg"
sample_mp3 = assets_path / "output.mp3"

sample_assets = {
    # If you ever need the dir
    "assets_path": assets_path,
    # Specific file types
    "filetypes": {
        "pptx": sample_pptx,
        "docx": sample_docx,
        "pdf": sample_pdf,
        "xlsx": sample_xlsx,
        "html": sample_html,
        "png": sample_image,
        "zip": sample_zip,
        "csv": sample_csv,
        "jpg": sample_jpg,
        "mp3": sample_mp3,
    },
    # Sourcetypes
    "sourcetypes": {
        SourceType("Text"): sample_html,
        SourceType("Audio"): sample_mp3,
        SourceType("Image"): sample_image,
        SourceType("Doc"): sample_docx,
        SourceType("YouTube"): "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        SourceType("GitHub"): "https://github.com/acesanderson/Siphon",
        SourceType(
            "Article"
        ): "https://mwichary.medium.com/one-hundred-and-thirty-seven-seconds-2a0a3dfbc59e",
        # SourceType("Drive"): "https://drive.google.com/file/d/1a2b3c4d5e6f7g8h9i0j/view?usp=sharing",
        # SourceType("Email"): "NA",
        # SourceType("Obsidian"): "NA",
    },
}
