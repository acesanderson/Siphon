from pydantic import BaseModel, Field


class SyntheticData(BaseModel):
    """
    AI-generated enrichments, applied as a "finishing step" to the content.
    """

    title: str = Field(
        default="", description="Title of the content, either extracted or generated"
    )
    description: str = Field(
        default="", description="Short description or summary of the content"
    )
    summary: str = Field(default="", description="Detailed summary of the content")
    topics: list[str] = Field(
        default_factory=list,
        description="List of topics or keywords associated with the content, an area liable to change with cluster analyses.",
    )
    entities: list[str] = Field(
        default_factory=list,
        description="List of entities (people, places, organizations) mentioned in the content.",
    )
