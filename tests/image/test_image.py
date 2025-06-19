from Siphon.tests.fixtures.example_files import example_image_file
from Siphon.ingestion.image.retrieve_image import retrieve_image

llm_context = retrieve_image(example_image_file)
print(llm_context)

llm_context = retrieve_image(example_image_file, "gpt")
print(llm_context)
