"""
# Example 1: Database → Query → In-Memory
all_content = CorpusFactory.from_library()
research_query = all_content.query()\
   .filter_by_source_type(SourceType.YOUTUBE)\
   .filter_by_tags(["AI", "research"])\
   .limit(50)
research_corpus = research_query.to_corpus()

# Example 2: Direct corpus operations
youtube_corpus = CorpusFactory.from_library()\
   .filter_by_source_type(SourceType.YOUTUBE)

# Example 3: Complex query chain
strategic_content = SiphonQuery(CorpusFactory.from_library())\
   .filter_by_date_range(last_30_days)\
   .semantic_search("strategic planning")\
   .order_by_date(ascending=False)\
   .limit(20)\
   .to_sourdough(focus_areas=["strategy", "planning"])

# Example 4: In-memory corpus from files
local_corpus = CorpusFactory.from_directory("./docs")\
   .query()\
   .filter_by_content("important")\
   .to_corpus()
"""






# Collections Module Design Specification

## Overview

The `collections/` module provides comprehensive interfaces for managing, querying, and analyzing collections of `ProcessedContent` objects. This module bridges the gap between individual content processing (handled by core Siphon) and advanced content analysis workflows.

## Directory Structure

```
collections/
├── __init__.py           # Main exports and convenience imports
├── README.md            # This specification
├── corpus/              # Collection management and construction
│   ├── processed_corpus.py      # In-memory collections with rich operations
│   ├── processed_library.py     # Database-backed collection interface
│   ├── sourdough.py             # Auto-curating strategic knowledge base
│   └── specialized/             # Domain-specific corpus types
│       ├── research_corpus.py   # Multi-document synthesis collections
│       ├── temporal_corpus.py   # Time-aware collections
│       └── domain_corpus.py     # Subject-matter specialized collections
├── query/               # Query interfaces and search implementations
│   ├── siphon_query.py          # Main query interface (corpus-agnostic)
│   ├── builders/                # Query construction utilities
│   │   ├── query_builder.py     # Fluent query construction
│   │   ├── filter_builder.py    # Complex filtering logic
│   │   └── aggregation_builder.py # Analytics and grouping
│   ├── engines/                 # Different search implementations
│   │   ├── fulltext_search.py   # PostgreSQL full-text search
│   │   ├── semantic_search.py   # ChromaDB vector similarity
│   │   ├── graph_search.py      # Neo4j relationship queries
│   │   └── hybrid_search.py     # Combined search strategies
│   ├── filters/                 # Reusable filtering components
│   │   ├── metadata_filters.py  # Source type, date, size filters
│   │   ├── content_filters.py   # Text-based filtering
│   │   └── semantic_filters.py  # AI-powered content classification
│   └── snapshot.py              # Library overview and statistics
└── analytics/           # Advanced analysis and insights
    ├── content_analytics.py     # Content analysis and metrics
    ├── relationship_discovery.py # Find connections between content
    ├── trend_analysis.py        # Temporal pattern detection
    └── export/                  # Export formats for external tools
        ├── markdown_export.py
        ├── json_export.py
        └── research_export.py
```

## Core Design Principles

### 1. **Corpus-Agnostic Querying**
All query operations work on any `ProcessedCorpus`, whether it's:
- In-memory collections (`ProcessedCorpus.from_directory()`)
- Database-backed collections (`ProcessedCorpus.from_library()`)
- Specialized collections (`Sourdough`, `ResearchCorpus`)

### 2. **Composable Query Building**
```python
# Fluent interface for complex queries
results = (SiphonQuery(corpus)
    .filter_by_source_type(SourceType.YOUTUBE)
    .filter_by_date_range(last_month, today)
    .search("machine learning")
    .semantic_search("AI strategy", k=10)
    .limit(20)
    .execute())
```

### 3. **Pluggable Search Engines**
Different search strategies can be combined:
- **Full-text**: PostgreSQL native search
- **Semantic**: ChromaDB vector similarity
- **Graph**: Neo4j relationship traversal
- **Hybrid**: Combine multiple approaches with ranking

### 4. **Lazy Evaluation**
Queries are constructed as query objects and executed only when needed, allowing for:
- Query optimization
- Caching strategies
- Progress tracking for long operations

## Implementation Strategy

### Query Interface Evolution
```python
class SiphonQuery:
    """Main query interface - starts simple, grows sophisticated."""
    
    # Phase 1: Basic functionality
    def last(self, n: int = 1) -> ProcessedCorpus
    def search(self, query: str) -> ProcessedCorpus
    def filter_by_source_type(self, source_type: SourceType) -> ProcessedCorpus
    
    # Phase 2: Advanced filtering
    def filter_by_date_range(self, start: datetime, end: datetime) -> ProcessedCorpus
    def filter_by_size(self, min_chars: int, max_chars: int) -> ProcessedCorpus
    def filter_by_metadata(self, **criteria) -> ProcessedCorpus
    
    # Phase 3: Semantic capabilities
    def semantic_search(self, query: str, k: int = 10) -> ProcessedCorpus
    def find_similar(self, content: ProcessedContent, k: int = 10) -> ProcessedCorpus
    def cluster_by_topic(self, n_clusters: int = 5) -> dict[str, ProcessedCorpus]
    
    # Phase 4: Advanced analytics
    def trend_analysis(self, time_window: timedelta) -> TrendReport
    def relationship_discovery(self) -> RelationshipGraph
    def content_analytics(self) -> AnalyticsReport
```

### Search Engine Architecture
```python
class SearchEngine(ABC):
    """Base class for different search implementations."""
    
    @abstractmethod
    def search(self, corpus: ProcessedCorpus, query: SearchQuery) -> SearchResults
    
    @abstractmethod
    def supports_query_type(self, query_type: QueryType) -> bool

# Implementations handle specific search types
class FullTextSearchEngine(SearchEngine): ...
class SemanticSearchEngine(SearchEngine): ...
class GraphSearchEngine(SearchEngine): ...

# Hybrid engine routes queries to appropriate engines
class HybridSearchEngine(SearchEngine):
    def search(self, corpus, query):
        # Route to best engine(s) for query type
        # Combine and rank results
```

### Progressive Enhancement

**Phase 1: Foundation** (Current Priority)
- Migrate existing query functionality
- Implement basic SiphonQuery interface
- Set up directory structure

**Phase 2: Advanced Filtering**
- Complex metadata filtering
- Date range and temporal queries
- Content-based filtering (length, complexity)

**Phase 3: Semantic Search**
- ChromaDB integration for vector similarity
- Semantic clustering and topic discovery
- Content relationship detection

**Phase 4: Graph Analysis**
- Neo4j integration for entity relationships
- Content citation and reference networks
- Knowledge graph construction

**Phase 5: Analytics & Insights**
- Trend analysis and pattern detection
- Content gap analysis
- Strategic intelligence automation

## Integration Points

### With Core Siphon
- Collections consume `ProcessedContent` objects
- Query results return `ProcessedCorpus` for further processing
- Maintains compatibility with existing caching and storage

### With External Systems
- **ChromaDB**: Vector embeddings for semantic search
- **Neo4j**: Graph relationships and entity networks  
- **PostgreSQL**: Full-text search and metadata queries
- **Export Formats**: Markdown, JSON, research reports

### With User Workflows
- **CLI Tools**: Rich terminal interfaces for query exploration
- **Research Scripts**: Multi-document synthesis and analysis
- **Strategic Intelligence**: Auto-updating knowledge bases (Sourdough)
- **API Endpoints**: Programmatic access for external tools

## Success Metrics

1. **Query Performance**: Sub-second response for typical queries
2. **Scalability**: Handle 10K+ ProcessedContent objects efficiently  
3. **Flexibility**: Support 80% of user query needs without custom code
4. **Usability**: Intuitive interfaces that match user mental models
5. **Extensibility**: Easy to add new search engines and corpus types

This architecture supports both simple use cases (finding recent content) and sophisticated workflows (multi-modal semantic analysis) while maintaining the clean abstractions that make Siphon extensible and maintainable.
