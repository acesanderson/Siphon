from pydantic import BaseModel, Field


class ProcessedFile(BaseModel):
    sha256: str = Field(..., description="SHA-256 hash of the file")
    abs_path: str = Field(..., description="Absolute path to the file")
    llm_context: str = Field(..., description="LLM context for the file")
