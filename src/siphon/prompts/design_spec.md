# Enhanced Prompts Design Specification

## Overview
Implement source-specific enhanced prompts for title, description, and summary generation that capture multiple perspectives within a single generation step. Each source type gets customized prompts optimized for your personal knowledge management and RAG searchability.

## File Structure
```
prompts/
├── enrich_title.jinja2           # Base title template
├── enrich_description.jinja2     # Base description template  
├── enrich_summary.jinja2         # Base summary template
└── source_specific/
    ├── youtube_title.jinja2
    ├── youtube_description.jinja2
    ├── youtube_summary.jinja2
    ├── powerpoint_title.jinja2
    ├── powerpoint_description.jinja2
    ├── powerpoint_summary.jinja2
    ├── github_title.jinja2
    ├── github_description.jinja2
    ├── github_summary.jinja2
    └── [other source types...]
```

## Core Design Principles

### 1. **Multi-Component Structure**
Each enhanced prompt requests multiple perspectives in a single generation:
- **Chronological + Insights** (YouTube)
- **Themes + Decisions + Evidence** (PowerPoint) 
- **Purpose + Functionality** (GitHub)

### 2. **RAG Optimization**
All prompts emphasize:
- **Keyword density** for searchability
- **Semantic consistency** across title/description/summary
- **Entity preservation** (names, technical terms, concepts)

### 3. **Personal Knowledge Management Focus**
Prompts assume the user will search with queries like:
- "I remember a doc about strategy for X"
- "What was that video where someone explained Y?"
- "Find the presentation with data on Z"

## Implementation Changes Required

### 1. **Update Generation Functions**
Modify `enrich/generate_*.py` files to support source-specific templates:

```python
# enrich/generate_title.py
def generate_title(processed_content: ProcessedContent, model: str = "llama3.3:latest") -> str:
    uri = processed_content.uri
    source_type = uri.sourcetype.value.lower()
    
    # Try source-specific template first
    source_specific_file = prompts_dir / "source_specific" / f"{source_type}_title.jinja2"
    if source_specific_file.exists():
        prompt_file = source_specific_file
    else:
        # Fallback to base template
        prompt_file = prompts_dir / "enrich_title.jinja2"
    
    # Rest of function unchanged...
```

### 2. **Template Variable Enhancement**
Pass additional context to templates:

```python
input_variables = {
    "uri": uri,
    "llm_context": llm_context,
    "source_type": uri.sourcetype.value,
    "metadata": getattr(processed_content, 'metadata', {}),
}
```

## Source-Specific Prompt Specifications

### YouTube Templates

#### `youtube_title.jinja2`
```jinja2
Generate a concise title (5-12 words) that captures:
- Primary topic/subject matter
- Key perspective or unique angle
- Speaker/creator if notable

Content: {{ llm_context }}

Requirements:
- Focus on searchable keywords
- Include unique angle if present
- Avoid generic terms like "video" or "discusses"

Title:
```

#### `youtube_description.jinja2`  
```jinja2
Create a 2-3 sentence description that includes:
1. What specific problem or question this addresses
2. The unique perspective or approach taken
3. Target audience or use case

Content: {{ llm_context }}

Focus on what someone would need to know to decide if this content is relevant to their current work or interests.

Description:
```

#### `youtube_summary.jinja2`
```jinja2
Create a summary with the following three components:

**CHRONOLOGICAL FLOW**: How the content unfolds and builds over time
**KEY INSIGHTS**: Main arguments, novel ideas, practical advice, and unique perspectives  
**STRUCTURE**: If there are distinct sections or topics, outline each briefly

Content: {{ llm_context }}

Target length: {{ target_length }} words ({{ length_percentage }}% of original)

Requirements:
- Preserve all important technical terms and proper nouns
- Focus on actionable insights and unique perspectives
- Maintain chronological logic while highlighting key concepts
- Include specific examples or data points mentioned

Summary:
```

### PowerPoint Templates

#### `powerpoint_title.jinja2`
```jinja2
Generate a title (5-12 words) that captures:
- Business objective or strategic purpose
- Key decision area or project focus
- Context (meeting type, stakeholder group) if clear

Content: {{ llm_context }}

Focus on what this presentation was trying to accomplish or decide.

Title:
```

#### `powerpoint_description.jinja2`
```jinja2
Create a 2-3 sentence description covering:
1. Strategic context or business problem addressed
2. Key stakeholders or decision-makers involved
3. Primary outcome or recommendation

Content: {{ llm_context }}

Emphasize business impact and decision-making context.

Description:
```

#### `powerpoint_summary.jinja2`
```jinja2
Analyze this presentation and create a summary with three components:

**STRATEGIC THEMES**: Major conceptual groupings and overarching business themes
**DECISION POINTS**: Concrete actions, commitments, recommendations, or strategic choices
**KEY EVIDENCE**: Important data points, metrics, findings, or supporting information

Content: {{ llm_context }}

Target length: {{ target_length }} words ({{ length_percentage }}% of original)

Requirements:
- Group related concepts thematically rather than slide-by-slide
- Highlight actionable decisions and commitments
- Preserve specific metrics, dates, and quantitative data
- Focus on business outcomes and strategic implications

Summary:
```

### GitHub Templates

#### `github_title.jinja2`
```jinja2
Generate a title (5-12 words) that captures:
- Project name and primary technology/framework
- Core functionality or purpose
- Target use case or domain

Content: {{ llm_context }}

Focus on technical purpose and implementation approach.

Title:
```

#### `github_description.jinja2`
```jinja2
Create a 2-3 sentence description covering:
1. What problem this project solves
2. Target users or use cases
3. Maturity level and key differentiators

Content: {{ llm_context }}

Emphasize practical applications and technical approach.

Description:
```

#### `github_summary.jinja2`
```jinja2
Create a summary focusing on technical functionality:

**ARCHITECTURE**: Key components, design patterns, and technical approach
**IMPLEMENTATION**: Notable code organization, dependencies, and technical decisions
**USAGE**: How to use, integrate, or extend this project

Content: {{ llm_context }}

Target length: {{ target_length }} words ({{ length_percentage }}% of original)

Requirements:
- Focus on technical implementation over project goals
- Preserve programming languages, frameworks, and technical terms
- Include key dependencies and architectural decisions
- Highlight notable features or technical innovations

Summary:
```

## Base Template Fallbacks

### `enrich_title.jinja2` (Generic)
```jinja2
Generate a clear, concise title (5-12 words) that captures the main topic and key perspective of this content.

Content: {{ llm_context }}
Source: {{ uri }}

Focus on searchable keywords and unique angles. Avoid generic terms.

Title:
```

### `enrich_description.jinja2` (Generic)
```jinja2
Create a 2-3 sentence description that summarizes:
1. The main topic or problem addressed
2. The approach or perspective taken  
3. Key insights or outcomes

Content: {{ llm_context }}

Description:
```

### `enrich_summary.jinja2` (Generic)
```jinja2
Create a comprehensive summary that captures:
- Main arguments and key insights
- Important supporting details and examples
- Practical implications or applications

Content: {{ llm_context }}

Target length: {{ target_length }} words ({{ length_percentage }}% of original)

Requirements:
- Preserve important technical terms and proper nouns
- Focus on unique insights and practical value
- Maintain logical flow and structure

Summary:
```

## Implementation Steps

1. **Create prompt files** in the specified directory structure
2. **Update generation functions** to support source-specific template selection
3. **Enhance template variables** to include source type and metadata
4. **Test with existing content** to validate prompt effectiveness
5. **Iterate on prompts** based on output quality and searchability

## Quality Validation

Test each source type with:
- **Keyword preservation**: Technical terms and proper nouns maintained
- **Searchability**: Would you find this content with relevant queries?
- **Uniqueness**: Does each component add distinct value?
- **Consistency**: Do title/description/summary work together coherently?

This approach gives you immediate source-specific customization while maintaining the single-stage processing you prefer
