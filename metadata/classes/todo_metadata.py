# from Siphon.data.Metadata import Metadata
# from Siphon.data.URI import URI
# from pydantic import Field
#
#
# class ToDoMetadata(Metadata):
#     """
#     Obsidian ToDos, as scraped when prcoessing obsidian files.
#     Needs some special thinking about how to handle, resolve duplicates, etc.
#     Also needs implementation of URI, ingestion, etc.
#     Design backwards from my ADHD brain and how you would handle a mass of todos, some of which will never be completed.
#     """
#
#     source_file: URI = Field(..., description="URI for file to do is associated with.")
#     date_created: int = Field(
#         ...,
#         description="Unix epoch time for when todo was first detected by scripts / last modified data for file on first scrape.",
#     )
#     date_completed: int = Field(
#         ...,
#         description="Unix epoch time for first time todo was noticed to be completed.",
#     )
#
#     @classmethod
#     def from_uri(cls, uri: URI):
#         _ = uri
#         raise NotImplementedError("ToDos not implemented yet.")
#
#     @classmethod
#     def from_dict(cls, data: dict):
#         """
#         Factory method to create ArticleMetadata from a dictionary.
#         """
#         ...
