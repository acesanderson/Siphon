from Siphon.enrich.enrich import enrich_content
from Siphon.data.ProcessedContent import ProcessedContent
from Siphon.data.SyntheticData import SyntheticData

def create_SyntheticData(processed_content: ProcessedContent, model: str = "cogito:14b") -> SyntheticData:
    """
    Create a SyntheticData object from a ProcessedContent object.
    """
    synthetic_data = enrich_content(processed_content, model=model)
    return synthetic_data
