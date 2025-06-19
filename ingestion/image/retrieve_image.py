from pathlib import Path
from Siphon.ingestion.image.describe_image_with_cloud import describe_image_with_cloud_models
from Siphon.ingestion.image.describe_image_with_ollama import describe_image_with_ollama_models

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
        # TBD: add validation for Chain-supported image analysis models
        model = Model()._validate_model(model)
        return describe_image_with_cloud_models(image_path, model=model)
    elif model == "ollama":
        return describe_image_with_ollama_models(image_path)


