"""
Test script to send an image to Ollama vision models and summarize the results.
SUMMARY: gemma3:27b is hands down the best model for image description, across mutiple images and according to both o4-mini and gemini2.5.
"""

from Chain.message.convert_image import convert_image_file
import ollama
from pathlib import Path

vision_models = """
gemma3:27b
llava:13b
llama4:16x17b
minicpm-v:8b
granite3.2-vision:2b
""".strip().split('\n')

# Cut this model -- too heavy -- 

dir_path = Path(__file__).parent
assets_dir = dir_path.parent.parent / "assets"
# example_image = assets_dir / "rag.png"
example_image = assets_dir / "lil.png"

# Load the image from the assets directory and encode it in base64
image_data = convert_image_file(example_image)

def describe_image(image_data: str, vision_model: str) -> str:
    # Send the image to a vision-capable model (e.g., 'llava')
    response = ollama.generate(
        model=vision_model,
        prompt='Describe this photo in detail. If there is text in the image, return it verbatim.',
        images=[image_data],
        keep_alive=0
    )
    return response["response"]

results = {}
for vision_model in vision_models:
    try:
        print(vision_model)
        response = describe_image(image_data, vision_model)
        results[vision_model] = response
    except Exception as e:
        print(f"Error with model {vision_model}: {e}")

from Chain import Model, ImageMessage
import json

model = Model("gemini2.5")
# model = Model("o4-mini")
text_content = f"Look at the following results from an ML pipeline where I've asked several different models to describe an image.\n<results>{json.dumps(results)}</results>\n\nNow, please summarize the results and tell me which model you think did the best job describing the image."
imagemessage = ImageMessage(role = "user", text_content = text_content, file_path = str(example_image))
response = model.query(input=[imagemessage])
print(response)

