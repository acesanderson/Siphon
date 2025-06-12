"""
Some disconnected functions for displaying images on command line IF you have chafa installed.
"""


def convert_file_to_base64(file_path):
    """Convert an image file to a base64-encoded string."""
    try:
        with open(file_path, "rb") as image_file:
            base64_string = base64.b64encode(image_file.read()).decode("utf-8")
        return base64_string
    except Exception as e:
        print(f"Error: {e}")
        return None


def display_to_terminal(base64_string):
    """
    Display a base64-encoded image using chafa.
    Your mileage may vary depending on the terminal and chafa version.
    """
    import subprocess
    import base64

    try:
        image_data = base64.b64decode(base64_string)
        process = subprocess.Popen(["chafa", "-"], stdin=subprocess.PIPE)
        process.communicate(input=image_data)
    except Exception as e:
        print(f"Error: {e}")


# Example usage
if __name__ == "__main__":
    # Convert the image file to a base64 string
    base64_string = convert_file_to_base64("dymphna.png")
    display_to_terminal(base64_string)
