"""
This module defines various file extensions categorized into different types.
This routes incoming requests to the appropriate handler based on the file extension.
"""

extensions = {
    "raw": [".csv", ".json", ".xml", ".txt", ".md", ".yaml", ".yml", ".toml", ".ini"],
    "code": [
        ".py",
        ".js",
        ".html",
        ".css",
        ".java",
        ".cpp",
        ".c",
        ".go",
        ".rs",
        ".rb",
        ".php",
    ],
    "markitdown": [
        ".docx",
        ".pptx",
        ".xlsx",
        ".xls",
        ".pdf",
        ".msg",
        ".html",
        ".rtf",
    ],
    "audio": [
        ".wav",
        ".mp3",
        ".m4a",
        ".ogg",
        ".flac",
    ],
    "video": [
        ".mp4",
        ".avi",
        ".mov",
        ".webm",
        ".mkv",
    ],
    "image": [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".tiff",
        ".svg",
        ".webp",
        ".ico",
    ],
    "archive": [".zip", ".tar", ".gz", ".rar", ".7z"],
    "specialized": [".epub", ".mobi"],
}
