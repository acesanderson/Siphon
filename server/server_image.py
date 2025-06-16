"""
This adapts our image analysis code to work with the ContextCall object.
"""

from Chain.message.convert_image import convert_image
from Siphon.server.context_call import ContextCall
from Siphon.ingestion.image.image import describe_image
from pathlib import Path
import base64, tempfile


def describe_image_ContextCall(context_call: ContextCall) -> str:
    """
    Convert an image to text from a ContextCall object.
    This is a very minimal implementation -- we send only file extension and base64 data.
    """
    # Decode base64 data to bytes
    base64_bytes = base64.b64decode(context_call.base64_data)


if __name__ == "__main__":
    from Siphon.server.context_call import create_ContextCall_from_file

    dir_path = Path(__file__).parent
    file_path = dir_path.parent / "assets" / "dymphna.png"
    context_call = create_ContextCall_from_file(file_path)
    print(context_call)
    transcript = describe_image_ContextCall(context_call)
    print(transcript)
