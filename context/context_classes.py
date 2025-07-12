import importlib
from Siphon.data.Context import Context
from Siphon.data.SourceType import SourceType


def load_context_class(sourcetype: SourceType) -> type[Context]:
    """
    Dynamically import the Context class corresponding to a SourceType.
    Assumes:
      - module path: Siphon.context.classes.{sourcetype.name.lower()}_context
      - class name: {sourcetype.value}Context
    """
    module_name = f"Siphon.context.classes.{sourcetype.name.lower()}_context"
    class_name = f"{sourcetype.value}Context"

    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as e:
        raise ImportError(
            f"Missing module for SourceType.{sourcetype.name}.\n"
            f"Expected file: `{module_name.replace('.', '/')}.py`"
        ) from e

    try:
        context_class = getattr(module, class_name)
    except AttributeError as e:
        raise ImportError(
            f"Module `{module_name}` exists but does not define `{class_name}`.\n"
            f"Please ensure the class name matches and is defined."
        ) from e

    if not issubclass(context_class, Context):
        raise TypeError(f"{class_name} exists but does not inherit from `URI`.")

    return context_class


# Build the list of valid URI subclasses
ContextClasses = [load_context_class(st) for st in SourceType]
