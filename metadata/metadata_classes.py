import importlib
from Siphon.data.Metadata import Metadata
from Siphon.data.SourceType import SourceType


def load_metadata_class(source_type: SourceType) -> type[Metadata]:
    """
    Dynamically import the Metadata class corresponding to a SourceType.
    Assumes:
      - module path: Siphon.metadata.classes.{source_type.name.lower()}_metadata
      - class name: {source_type.value}Metadata
    """
    module_name = f"Siphon.metadata.classes.{source_type.name.lower()}_metadata"
    class_name = f"{source_type.value}Metadata"

    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as e:
        raise ImportError(
            f"Missing module for SourceType.{source_type.name}.\n"
            f"Expected file: `{module_name.replace('.', '/')}.py`"
        ) from e

    try:
        metadata_class = getattr(module, class_name)
    except AttributeError as e:
        raise ImportError(
            f"Module `{module_name}` exists but does not define `{class_name}`.\n"
            f"Please ensure the class name matches and is defined."
        ) from e

    if not issubclass(metadata_class, Metadata):
        raise TypeError(f"{class_name} exists but does not inherit from `URI`.")

    return metadata_class


# Build the list of valid URI subclasses
MetadataClasses = [load_metadata_class(st) for st in SourceType]
