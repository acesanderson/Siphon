==Note: look at the design docs within Vortex as point of comparison; these are interconnected systems.==

# Siphon ToDo Integration Design Document

## Overview

Siphon's ToDo functionality serves as an **observational todo intelligence system** rather than another task management app. It automatically discovers, tracks, and analyzes todo patterns across your entire knowledge base to provide ADHD-friendly insights and seamless integration with active task management tools like Vortex.

## Core Philosophy: The Todo Telescope

**Problem**: ADHD brains scatter todos across dozens of files, lose track of completion patterns, and struggle with traditional rigid todo systems.

**Solution**: Siphon becomes your "todo archaeologist" - automatically discovering todos from all content sources and providing data-driven insights about your actual completion patterns without judgment.

## Key Design Principles

### 🧠 ADHD-Optimized Approach
- **Automatic discovery** - No manual todo entry required
- **Pattern recognition** - Learn from actual behavior, not aspirational systems
- **Graceful decay** - Accept that some todos will never be completed
- **Context preservation** - Maintain rich context about where/when todos originated

### 🔄 Observational vs. Actionable Split
- **Siphon (Observational)**: Discovers, tracks, analyzes todo patterns
- **Vortex (Actionable)**: Active task management with rich interfaces
- **Integration**: Siphon feeds discovered todos → Vortex for triage/action

## Technical Implementation

### ToDoMetadata Class

```python
class ToDoMetadata(Metadata):
    # Core identification
    source_file: URI = Field(..., description="URI for file todo is associated with")
    todo_text: str = Field(..., description="The actual todo text")
    context_snippet: str = Field(..., description="Surrounding text for context")
    
    # Temporal tracking
    date_discovered: int = Field(..., description="Unix epoch when todo was first detected")
    date_completed: Optional[int] = Field(None, description="Unix epoch when todo was marked complete")
    times_rediscovered: int = Field(0, description="How often the same todo reappears")
    
    # ADHD-friendly analytics
    energy_level_required: Optional[str] = Field(None, description="'low', 'medium', 'high'")
    context_type: str = Field(..., description="'meeting', 'code', 'personal', 'admin'")
    completion_likelihood: Optional[float] = Field(None, description="AI-predicted completion probability")
    
    # Integration hooks
    vortex_task_id: Optional[UUID] = Field(None, description="Link to active Vortex task")
    related_todos: list[str] = Field(default_factory=list, description="Similar/duplicate todos")
```

### Discovery Engine

#### Todo Pattern Recognition
- **Markdown todos**: `- [ ] Task` / `- [x] Completed`
- **Code comments**: `TODO:`, `FIXME:`, `HACK:`
- **Natural language**: "need to", "should", "remember to"
- **Meeting transcripts**: Action items and follow-ups
- **Email forwards**: Requests and commitments

#### Context Classification
- **Meeting todos**: From transcripts, calendar events
- **Code todos**: From development files, comments
- **Personal todos**: From daily notes, journals
- **Admin todos**: From emails, official documents

### Analytics & Insights

#### Completion Pattern Analysis
- **Velocity by context**: Which types of todos actually get done?
- **Energy matching**: What gets completed when tired vs energized?
- **Context switching costs**: Todos requiring specific mental states
- **Decay patterns**: Natural resolution vs requiring action

#### ADHD-Friendly Metrics
- **Rediscovery frequency**: Todos that keep getting rewritten (high importance?)
- **Context clustering**: Related todos across different files
- **Completion streaks**: Productive periods and patterns
- **Abandonment detection**: Projects/contexts that consistently don't get completed

## Integration Architecture

### Siphon → Vortex Flow
1. **Discovery**: Siphon scans all content sources for todos
2. **Analysis**: AI categorizes, estimates effort, predicts completion
3. **Surfacing**: High-value todos suggested for Vortex import
4. **Tracking**: Bidirectional sync for completion status
5. **Learning**: Feedback loop improves AI predictions

### Data Storage Strategy
- **PostgreSQL**: Structured todo metadata, analytics, relationships
- **ChromaDB**: Semantic search for similar/duplicate todos
- **Source files**: Maintain todos in original context (Obsidian, code, etc.)

## Processing Pipeline

### Content Ingestion
```python
def extract_todos_from_content(processed_content: ProcessedContent) -> list[ToDoMetadata]:
    """Extract todos during standard Siphon ingestion"""
    # Pattern matching for different todo formats
    # Context extraction (surrounding text)
    # Deduplication against existing todos
    # AI classification and analysis
```

### Completion Detection
```python
def detect_todo_completion(old_content: str, new_content: str) -> list[UUID]:
    """Detect when todos transition from [ ] to [x]"""
    # Diff analysis for checkbox changes
    # Natural language completion detection
    # Integration with Vortex completion events
```

### Smart Prioritization
```python
def suggest_todos_for_action(context: str = None, energy: str = None) -> list[ToDoMetadata]:
    """Surface todos likely to be completed given current context"""
    # Filter by energy level and context type
    # Prioritize by completion likelihood
    # Consider current project focus
```

## Use Cases

### Automatic Discovery
- User writes "TODO: Call dentist" in daily note
- Siphon discovers during vault scan
- Creates ToDoMetadata with context and classification
- Suggests import to Vortex if high priority

### Pattern Recognition
- User consistently postpones "organize files" type todos
- Siphon identifies pattern and suggests different approach
- AI recommends breaking into smaller, more actionable items

### Context-Aware Suggestions
- User opens code editor
- Siphon surfaces code-related todos from comments and notes
- Prioritizes by file relevance and estimated effort

### Completion Analytics
- Weekly summary of completed todos by category
- Identification of productive contexts and times
- Suggestions for optimizing todo completion patterns

## Future Enhancements

### Advanced AI Features
- **Natural language parsing**: Convert informal notes to structured todos
- **Effort estimation**: AI predicts time required based on content
- **Dependency detection**: Identify todo relationships across files
- **Motivational coaching**: Gentle nudges for long-overdue items

### Integration Expansions
- **Calendar integration**: Time-blocked todos
- **Email processing**: Action items from forwarded emails
- **Meeting notes**: Automatic action item extraction
- **Code analysis**: Technical debt todos from static analysis

## Success Metrics

### ADHD-Friendly Goals
- **Reduced cognitive load**: Fewer manually managed todo lists
- **Improved completion rates**: Better matching of todos to context/energy
- **Pattern awareness**: Data-driven understanding of productivity patterns
- **Stress reduction**: Acceptance of natural todo decay without guilt

### Technical Metrics
- **Discovery accuracy**: Precision/recall of todo detection
- **Completion prediction**: Accuracy of AI likelihood estimates
- **Duplicate detection**: Effectiveness of similar todo identification
- **Integration efficiency**: Seamless Siphon ↔ Vortex synchronization

## Implementation Priority

1. **Phase 1**: Basic todo discovery and ToDoMetadata structure
2. **Phase 2**: Completion detection and simple analytics
3. **Phase 3**: AI classification and smart prioritization
4. **Phase 4**: Vortex integration and bidirectional sync
5. **Phase 5**: Advanced analytics and coaching features

---

*"The goal isn't to complete every todo - it's to understand your patterns and work with your brain, not against it."*
