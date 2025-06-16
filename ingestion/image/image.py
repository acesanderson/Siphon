from pathlib import Path
from Chain import ImageMessage, Chain, Model
from Chain.message.convert_image import convert_image_file


def describe_image_with_ollama_models(file_path: str | Path, model="gemma3:27b") -> str:
    import ollama

    image_data = convert_image_file(file_path)
    # Send the image to a vision-capable model (e.g., 'llava')
    response = ollama.generate(
        model=model,
        prompt="Describe this photo in detail. If there is text in the image, return it verbatim.",
        images=[image_data],
        keep_alive=0,
    )
    return response["response"]


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


if __name__ == "__main__":
    dir_path = Path(__file__).parent
    file_path = dir_path.parent.parent / "assets" / "duchamp.jpg"
    description = describe_image(file_path)
    print(description)
