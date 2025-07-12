"""
This module dynamically loads all URI handler classes for each SourceType defined in Siphon.

Each SourceType enum member (e.g. SourceType.YOUTUBE) is expected to have:
- A corresponding module located at: `Siphon.uri.{lowercase_name}_uri.py`
  (e.g. `Siphon.uri.youtube_uri` for SourceType.YOUTUBE)
- A class defined in that module named `{SourceType.value}URI`
  (e.g. `YouTubeURI` for "YouTube", `GitHubURI` for "GitHub")

This script:
1. Iterates through all values of the SourceType enum.
2. Dynamically imports each corresponding URI class.
3. Validates that the class exists and inherits from the base `URI` class.
4. Builds a list of all successfully loaded URI subclasses as `URIClasses`.

If any SourceType is missing a corresponding module or class, or if the class does not inherit from URI, an informative error is raised.

This ensures strict one-to-one enforcement between defined source types and implemented URI resolvers.
"""

import importlib
from Siphon.data.URI import URI
from Siphon.data.SourceType import SourceType


def load_uri_class(source_type: SourceType) -> type[URI]:
    """
    Dynamically import the URI class corresponding to a SourceType.
    Assumes:
      - module path: Siphon.uri.{source_type.name.lower()}_uri
      - class name: {source_type.value}URI
    """
    module_name = f"Siphon.uri.classes.{source_type.name.lower()}_uri"
    class_name = f"{source_type.value}URI"

    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as e:
        raise ImportError(
            f"Missing module for SourceType.{source_type.name}.\n"
            f"Expected file: `{module_name.replace('.', '/')}.py`"
        ) from e

    try:
        uri_class = getattr(module, class_name)
    except AttributeError as e:
        raise ImportError(
            f"Module `{module_name}` exists but does not define `{class_name}`.\n"
            f"Please ensure the class name matches and is defined."
        ) from e

    if not issubclass(uri_class, URI):
        raise TypeError(f"{class_name} exists but does not inherit from `URI`.")

    return uri_class


# Build the list of valid URI subclasses
URIClasses = [load_uri_class(st) for st in SourceType]
