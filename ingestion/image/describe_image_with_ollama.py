from Chain.message.convert_image import convert_image_file
from pathlib import Path

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


