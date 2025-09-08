import importlib
from Siphon.data.SyntheticData import SyntheticData
from Siphon.data.types.SourceType import SourceType
from Siphon.logs.logging_config import get_logger
from typing import Union

logger = get_logger(__name__)


def load_synthetic_data_class(source_type: SourceType) -> type[SyntheticData]:
    """
    Dynamically import the SyntheticData class corresponding to a SourceType.
    Assumes:
      - module path: Siphon.synthetic_data.classes.{source_type.name.lower()}_synthetic_data
      - class name: {source_type.value}SyntheticData
    """
    module_name = (
        f"Siphon.synthetic_data.classes.{source_type.name.lower()}_synthetic_data"
    )
    class_name = f"{source_type.value}SyntheticData"

    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as e:
        raise ImportError(
            f"Missing module for SourceType.{source_type.name}.\n"
            f"Expected file: `{module_name.replace('.', '/')}.py`"
        ) from e

    try:
        synthetic_data_class = getattr(module, class_name)
    except AttributeError as e:
        raise ImportError(
            f"Module `{module_name}` exists but does not define `{class_name}`.\n"
            f"Please ensure the class name matches and is defined."
        ) from e

    if not issubclass(synthetic_data_class, SyntheticData):
        raise TypeError(f"{class_name} exists but does not inherit from `URI`.")

    return synthetic_data_class


# Build the list of valid URI subclasses
SyntheticDataClasses = [load_synthetic_data_class(st) for st in SourceType]

# A union type for all SyntheticData classes
SyntheticDataUnion = Union[tuple(SyntheticDataClasses)]
