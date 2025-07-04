"""
This adapts our image analysis code to work with the ContextCall object.
"""

from Siphon.data.ContextCall import ContextCall
from Chain.message.convert_image import convert_image
from pathlib import Path
import base64


def describe_image_ContextCall(context_call: ContextCall) -> str:
    """
    Convert an image to text from a ContextCall object.
    This is a very minimal implementation -- we send only file extension and base64 data.
    """
    import ollama

    # Decode base64 data to bytes
    base64_bytes = base64.b64decode(context_call.base64_data)
    converted_image = convert_image(context_call.base64_data)

    response = ollama.generate(
        model="gemma3:27b",  # or any other vision-capable model
        prompt="Describe this photo in detail. If there is text in the image, return it verbatim.",
        images=[converted_image],
        keep_alive=0,
    )
    return response["response"]


if __name__ == "__main__":
    from Siphon.data.ContextCall import create_ContextCall_from_file

    dir_path = Path(__file__).parent
    file_path = dir_path.parent / "assets" / "dymphna.png"
    context_call = create_ContextCall_from_file(file_path)
    print(context_call)
    transcript = describe_image_ContextCall(context_call)
    print(transcript)
