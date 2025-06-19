from pathlib import Path
from Chain import ImageMessage, Chain, Model


def describe_image_with_cloud_models(file_path: str | Path, model="gpt") -> str:
    """
    Describe an image using a Chain model.
    TBD: implement Ollama.
    """
    prompt_str = "Please describe this image in detail. If it is full of text, please provide the text verbatim."
    imagemessage = ImageMessage(
        role="user", file_path=str(file_path), text_content=prompt_str
    )

    model = Model(model)
    chain = Chain(model=model)
    response = chain.run(messages=[imagemessage])
    return str(response.content)


