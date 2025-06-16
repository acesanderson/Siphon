from enum import Enum


class SourceType(str, Enum):
    ARTICLE = "article"
    YOUTUBE = "youtube"
    FILE = "file"
    EMAIL = "email"
    GITHUB = "github"
    OBSIDIAN = "obsidian"
    DRIVE = "drive"
