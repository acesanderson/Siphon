from pathlib import Path
from Chain import ImageMessage, Chain, Model


def describe_image(file_path: str | Path) -> str:
    """
    Describe an image using a Chain model.
    TBD: implement Ollama.
    """
    prompt_str = "Please describe this image in detail. If it is full of text, please provide the text verbatim."
    imagemessage = ImageMessage(
        role="user", file_path=str(file_path), text_content=prompt_str
    )

    model = Model("gpt")
    chain = Chain(model=model)
    response = chain.run(messages=[imagemessage])
    return str(response.content)


if __name__ == "__main__":
    dir_path = Path(__file__).parent
    file_path = dir_path.parent.parent / "assets" / "duchamp.jpg"
    description = describe_image(file_path)
    print(description)
