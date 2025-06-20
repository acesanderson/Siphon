from pathlib import Path
from Chain import ImageMessage, Chain, Model

# Import our centralized logger - no configuration needed here!
from Siphon.logging.logging_config import get_logger

# Get logger for this module - will inherit config from retrieve_audio.py
logger = get_logger(__name__)


def describe_image_with_cloud_models(file_path: str | Path, model="gpt") -> str:
    """
    Describe an image using a Chain model.
    TBD: implement Ollama.
    """
    prompt_str = "Please describe this image in detail. If it is full of text, please provide the text verbatim."
    imagemessage = ImageMessage(
        role="user", file_path=str(file_path), text_content=prompt_str
    )

    logger.info(f"Creating Chain model with name: {model}")
    model = Model(model)
    chain = Chain(model=model)
    logger.info(f"Running Chain with model: {model.model} and image: {file_path}")
    response = chain.run(messages=[imagemessage])
    return str(response.content)


