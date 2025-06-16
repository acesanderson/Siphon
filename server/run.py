from Siphon.server.server_audio import transcribe_ContextCall
from Siphon.server.server_image import describe_image_ContextCall
from Siphon.server.server_enrich import create_SyntheticData
from Siphon.data.ProcessedContent import ProcessedContent
from Siphon.data.SyntheticData import SyntheticData
from Siphon.data.ContextCall import ContextCall
from Siphon.data.extensions import extensions
from fastapi import FastAPI

app = FastAPI(title="SiphonServer", version="1.0.0")


@app.post("/enrich")
async def enrich(processed_content: ProcessedContent) -> SyntheticData:
    """
    Generates title, description, summary for ProcessedContent.
    Returns SyntheticData object.
    """
    synthetic_data = create_SyntheticData(processed_content, model="cogito:14b")
    return synthetic_data


@app.post("/process")
async def process_content(content: ContextCall) -> ContextCall:
    """
    Processes audio or image content and returns the enriched ContextCall object.
    """
    if content.extension in extensions["audio"]:
        llm_context = transcribe_ContextCall(content)
    elif content.extension in extensions["image"]:
        llm_context = describe_image_ContextCall(content)
    else:
        raise ValueError("Unsupported content type")
    if not llm_context:
        raise ValueError("LLM context is empty after processing")
    return llm_context


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify that the server is running.
    """
    return {"status": "ok", "version": "1.0.0"}


def main():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)


if __name__ == "__main__":
    main()
