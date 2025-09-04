# ProcessedCollections Design Specification

**Version 1.0** | *January 2025*

## Purpose

ProcessedCollections bridges the gap between individual content processing and workflow-level operations. While Siphon excels at processing single items (one YouTube video, one document, one GitHub repo), real knowledge work requires **collection-level abstractions** for research, curation, and strategic intelligence.

## Architecture Overview

```
Individual → Collection → Library
    ↓          ↓          ↓
ProcessedContent → ProcessedCorpus → ProcessedLibrary
                      ↓
                  Sourdough (specialized)
```

### Core Principle: **Separation of Concerns**
- **ProcessedCorpus**: Ephemeral, in-memory collection manipulation
- **ProcessedLibrary**: Persistent, database-backed search that returns Corpus objects  
- **Sourdough**: Specialized, auto-maintaining corpus with strategic intelligence

## Class Specifications

### ProcessedCorpus
**Lightweight wrapper around collections of ProcessedContent objects**

#### Design Philosophy
- **Ephemeral**: Exists in memory for the duration of a workflow
- **Manipulable**: Rich interface for filtering, searching, organizing
- **Constructible**: Multiple ways to build collections based on real use cases

#### Key Features
```python
# Construction patterns
ProcessedCorpus.from_directory("./meeting_notes/")
ProcessedCorpus.from_url_list(research_urls)
ProcessedCorpus.from_tag("#strategy")

# Collection management  
corpus.add(content)
corpus.remove(content)

# View operations
corpus.snapshot()  # titles + descriptions for quick scanning
corpus.text()      # full context for LLM consumption

# Query operations
corpus.search("AI strategy")
corpus.similarity_search("competitive positioning", k=5)
corpus.filter_by_source_type(SourceType.YOUTUBE)
```

#### Implementation Notes
- Uses **composition** - internally maintains `list[ProcessedContent]`
- Query methods return **new ProcessedCorpus objects** (immutable operations)
- In-memory similarity search via ephemeral ChromaDB collection
- Optimized for collections of 10-1000 items

---

### ProcessedLibrary  
**Database-backed interface for library-wide operations**

#### Design Philosophy
- **Persistent**: Queries the full Siphon database
- **Scalable**: Handles thousands of ProcessedContent objects
- **Returns Corpora**: Search results come back as ProcessedCorpus for manipulation

#### Key Features
```python
library = ProcessedLibrary()

# Search operations (return ProcessedCorpus)
corpus = library.search("machine learning")
corpus = library.get_corpus_by_source_type(SourceType.YOUTUBE)
corpus = library.get_recent_content(days=7)

# Corpus persistence
corpus_id = library.save_corpus(my_corpus, "Q4_Strategy_Research")
saved_corpus = library.load_corpus("Q4_Strategy_Research")

# Library management
library.get_library_stats()
library.health_check()
```

#### Implementation Notes
- **No inheritance** from ProcessedCorpus - different concerns
- Delegates to existing `database/postgres/` functions
- Future: Integration with persistent ChromaDB for semantic search
- Caches frequently-accessed corpora for performance

---

### Sourdough
**Auto-updating, self-maintaining strategic knowledge base**

#### Design Philosophy
- **Strategic Focus**: Maintains high-value strategic content within constraints
- **Self-Curating**: Automatically prunes outdated content, prioritizes by value
- **Living Document**: Produces always-fresh strategic snapshots

#### Key Features
```python
sourdough = Sourdough(max_tokens=4000, focus_areas=["AI", "product", "strategy"])

# Content management (auto-prunes)
sourdough.feed(new_all_hands_transcript)
sourdough.feed([quarterly_review, competitor_analysis])

# Strategic intelligence
snapshot = sourdough.get_current_snapshot()  # Markdown strategic summary
sourdough.save_snapshot()  # Version and persist

# Health monitoring
health = sourdough.get_health_status()
drift_analysis = sourdough.detect_drift()
```

#### Composition Over Inheritance
Sourdough **HAS-A** ProcessedCorpus rather than inheriting from it:

```python
class Sourdough:
    def __init__(self):
        self._corpus = ProcessedCorpus()  # Composition
        self._snapshot_history = []
        self._max_tokens = 4000
```

**Why composition?**
- Different lifecycle (persistent vs ephemeral)
- Specialized operations (auto-pruning, drift detection)  
- Strategic scoring and theme extraction
- Version management and snapshot persistence

## Use Case Workflows

### Research Intelligence
```python
# Gather sources
research_corpus = ProcessedCorpus.from_url_list(competitor_urls)
meeting_corpus = ProcessedCorpus.from_directory("./q4_meetings/")

# Combine and analyze
combined = ProcessedCorpus.from_processed_content_list(
    research_corpus.corpus + meeting_corpus.corpus
)

# Generate synthesis
ai_strategy_content = combined.search("AI strategy")
synthesis_text = ai_strategy_content.text()  # Ready for LLM
```

### Strategic Monitoring
```python
# Initialize strategic knowledge base
sourdough = Sourdough(focus_areas=["product", "competition", "roadmap"])

# Regular feeding (automated)
sourdough.feed(weekly_all_hands)
sourdough.feed(executive_email_updates)

# Always-current strategic context
current_strategy = sourdough.get_current_snapshot()
llm_context = sourdough.export_for_llm()
```

### Library-Wide Intelligence
```python
library = ProcessedLibrary()

# Cross-time analysis
q3_content = library.search("Q3 objectives")
q4_content = library.search("Q4 planning") 

# Historical research
youtube_learnings = library.get_corpus_by_source_type(SourceType.YOUTUBE)
strategy_evolution = youtube_learnings.filter_by_date_range(start_date, end_date)
```

## Technical Implementation

### Data Flow
```
Sources → Siphon → ProcessedContent → Collections → Intelligence
   ↓         ↓           ↓              ↓            ↓
URLs,    Individual   Structured    Organized   Strategic
Files    Processing   Content       Collections  Insights
```

### Storage Strategy
- **ProcessedCorpus**: In-memory only, ephemeral
- **ProcessedLibrary**: Queries existing PostgreSQL cache + ChromaDB
- **Sourdough**: 
  - Current state: `current_strategy.md` file
  - History: Versioned snapshot files + metadata in database
  - Pruned content: Temporary "hooch" storage (30-day retention)

### Performance Considerations
- **Corpus size limits**: Optimize for 10-1000 items per corpus
- **Lazy loading**: Library queries don't load full content until needed
- **Caching**: Frequently-accessed corpora cached in memory
- **Async operations**: Large corpus construction uses async processing

## Integration Points

### CLI Integration
```bash
# Create corpus from directory
siphon corpus create --from-dir ./research_docs/ --name "Q4_Research"

# Strategic snapshot
siphon sourdough snapshot --export-llm

# Library search
siphon library search "competitive analysis" --limit 20
```

### API Integration
```python
# FastAPI endpoints
POST /corpus/create
GET /corpus/{corpus_id}/search
POST /sourdough/feed
GET /sourdough/snapshot
GET /library/search
```

### Chain Integration
```python
# Use corpus text directly in Chain prompts
from Chain import Chain, Model, Prompt

research_corpus = ProcessedCorpus.from_directory("./analysis/")
context = research_corpus.text()

chain = Chain(
    model=Model("claude"),
    prompt=Prompt("Analyze this research: {{context}}")
)
response = chain.run(input_variables={"context": context})
```

## Future Enhancements

### Phase 2: Advanced Intelligence
- **NER across corpus**: Entity extraction and relationship mapping
- **Graph traversal**: Find connections between content items
- **Topic modeling**: Automatic theme detection and clustering
- **Semantic clusters**: Auto-organize content by conceptual similarity

### Phase 3: Workflow Integration
- **Smart notifications**: "New content relevant to your research corpus"
- **Auto-corpus generation**: "Create corpus for upcoming presentation"  
- **Collaborative corpora**: Share and merge corpus collections
- **Template corpora**: Pre-built collections for common workflows

### Phase 4: Advanced Sourdough
- **Multi-focus Sourdoughs**: Separate strategic feeds for different domains
- **Predictive pruning**: ML-based content value prediction
- **Cross-Sourdough insights**: "Strategy X conflicts with Strategy Y"
- **Integration triggers**: Auto-feed from calendar events, email distros

## Success Metrics

### Adoption Indicators
- **Corpus creation frequency**: How often users build collections
- **Query patterns**: Most common search and filter operations  
- **Sourdough health**: Consistency of strategic content updates
- **Workflow integration**: Usage in research and decision-making processes

### Quality Measures
- **Relevance**: Do corpus search results match user intent?
- **Completeness**: Are important sources included in collections?
- **Freshness**: Is strategic content kept current via Sourdough?
- **Actionability**: Do corpus insights drive real decisions?

---

**ProcessedCollections transforms Siphon from individual content processing into workflow-level knowledge operations - your personal intelligence analysis team.**
