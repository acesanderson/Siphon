"""
ProcessedCollections - Collection abstractions for Siphon

This module provides collection-level operations for ProcessedContent objects:
- ProcessedCorpus: Ephemeral, in-memory collections with rich query interface
- ProcessedLibrary: Persistent, database-backed search returning ProcessedCorpus objects
- Sourdough: Specialized, auto-maintaining ProcessedCorpus with domain-specific rules
"""

from .processed_corpus import ProcessedCorpus
from .processed_library import ProcessedLibrary
from .sourdough import Sourdough

__all__ = ["ProcessedCorpus", "ProcessedLibrary", "Sourdough"]
