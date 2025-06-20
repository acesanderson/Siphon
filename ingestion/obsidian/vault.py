"""
Simple logic for identifying the Obsidian vault path from an environment variable.
Will also add host-based logic since this is only local to Petrosian host, not Caruana or AlphaBlue.
"""
from pathlib import Path
import os

vault = os.getenv("OBSIDIAN_VAULT")
vault = Path(vault)
if not vault:
    raise ValueError("OBSIDIAN_VAULT environment variable is not set.")

print(vault)
