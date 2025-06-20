from pathlib import Path
from Siphon.ingestion.image.describe_image_with_cloud import describe_image_with_cloud_models
from Siphon.ingestion.image.describe_image_with_ollama import describe_image_with_ollama_models

# Import our centralized logging configuration
from Siphon.logging.logging_config import configure_logging
import logging


# Configure logging once at the entry point
logger = configure_logging(
    level=logging.INFO,
    console=True
)

def retrieve_image(image_path: str | Path, model: str = "ollama") -> str:
    """
    Retrieves an image description using the specified model.

    Args:
        image_path (str | Path): The path to the image file.
        model (str): The model to use for image description. Options are "ollama" or any Chain-supported model.

    Returns:
        str: The description of the image.
    """
    if model != "ollama":
        from Chain import Model
        if Model.is_supported(model):
            logger.info(f"Starting image description process with model: {model}")
            return describe_image_with_cloud_models(image_path, model=model)
        else:
            logger.error(f"Model '{model}' is not recognized by Chain.")
            raise ValueError(f"Model not recognized by Chain: {model}")
    elif model == "ollama":
        logger.info("Starting image description process with Ollama models.")
        return describe_image_with_ollama_models(image_path)


