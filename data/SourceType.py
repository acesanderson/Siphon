from enum import Enum


class SourceType(str, Enum):
    ARTICLE = "ARTICLE"
    YOUTUBE = "YOUTUBE"
    FILE = "FILE"
    EMAIL = "EMAIL"
    GITHUB = "GITHUB"
    OBSIDIAN = "OBSIDIAN"
    DRIVE = "DRIVE"
