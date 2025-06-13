"""
We also need:
- comments (optional) -- passed from Siphon cli
- description (llm-generated from context)
- summary (llm-generated from context)
- datetime (when processed)
- file_type
- file_size
"""


from pydantic import BaseModel, Field

class ProcessedFile(BaseModel):
    sha256: str = Field(..., description="SHA-256 hash of the file")
    abs_path: str = Field(..., description="Absolute path to the file")
    llm_context: str = Field(..., description="LLM context for the file")
