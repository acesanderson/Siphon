"""
Simple dummy ProcessedContent for testing display.

Usage:
    from Siphon.tests.fixtures.dummy_processed_content import dummy_content
    dummy_content.pretty_print()  # assuming you've added the mixin to ProcessedContent
"""

from Siphon.data.ProcessedContent import ProcessedContent
from Siphon.data.URI import URI
from Siphon.data.Context import Context
from Siphon.data.SyntheticData import SyntheticData
from Siphon.data.types.SourceType import SourceType


# Simple YouTube context with metadata
class DummyYouTubeContext(Context):
    sourcetype: SourceType = SourceType.YOUTUBE
    context: str = "This is a great tutorial on machine learning basics. We cover linear regression, decision trees, and neural networks with practical Python examples. Perfect for beginners!"

    # YouTube metadata
    url: str = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    domain: str = "youtube.com"
    video_id: str = "dQw4w9WgXcQ"
    channel: str = "AI Learning Hub"
    duration: int = 1547  # 25 min 47 sec
    view_count: int = 45782


# Create dummy ProcessedContent
dummy_content = ProcessedContent(
    uri=URI(
        source="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        sourcetype=SourceType.YOUTUBE,
        uri="youtube://dQw4w9WgXcQ",
    ),
    llm_context=DummyYouTubeContext(),
    synthetic_data=SyntheticData(
        sourcetype=SourceType.YOUTUBE,
        title="Machine Learning Basics Tutorial",
        description="Comprehensive guide covering ML fundamentals with Python examples",
        summary="A 25-minute tutorial covering linear regression, decision trees, and neural networks. Great for beginners looking to get started with machine learning.",
        topics=["machine learning", "python", "tutorial", "AI"],
        entities=["Python", "scikit-learn", "TensorFlow"],
    ),
)
