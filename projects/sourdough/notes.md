notes: sourdoughs should be generated / maintained for tags (think #profcerts, #boss, #google, etc.)


# Sourdough Design Document  
**Auto-Updating Company Strategic Knowledge Base**  
**Version 0.1** | *June 18, 2025*

## 1. Purpose

**Sourdough** is a self-maintaining, auto-curated knowledge base that continuously ingests, summarizes, and prunes company strategy content (e.g., all-hands transcripts, OKRs, product roadmaps) into a concise, up-to-date “strategy snapshot.” It is designed to stay within LLM context limits and to serve as a reliable, always-fresh source of strategic context for Siphon.

## 2. Key Features

- **Auto-Ingestion:** Regularly pulls in new documents from connected sources (Google Docs, transcripts, etc.).
- **Auto-Summarization:** Condenses content to fit within a defined token limit (e.g., 4K tokens).
- **Auto-Prune:** Removes outdated or redundant information to maintain freshness and relevance.
- **Snapshot Management:** Maintains a single “current_strategy.md” file and versions snapshots for auditability.
- **Prioritization:** Favors CEO/executive statements, recent data, and quantified metrics.

## 3. Architecture
```
[Connected Sources] → [Sourdough Ingestion] → [Summarization Engine] → [Pruning Engine] → [Snapshot Manager]
                                                         ↑
                                               [Snapshot History/Archive]
```
## 4. Components
- **Ingestion Module**
  - Connects to Siphon’s data sources.
  - Accepts new documents, transcripts, and other strategic content.
- **Summarization Engine**
  - Uses LLMs to generate concise summaries and synthetic titles/descriptions.
  - Recursively summarizes large documents to fit within snapshot size limits.
- **Pruning Engine**
  - Removes outdated content based on age, relevance, and similarity.
  - Retains “evergreen” content as designated.
- **Snapshot Manager**
  - Maintains the current strategy snapshot.
  - Versions snapshots for rollback and audit.
- **Snapshot History/Archive**
  - Stores previous versions and pruned content for reference.
## 5. Workflow
1. **Ingestion:** New documents are pulled from Siphon’s connected sources.
2. **Summarization:** Documents are summarized and scored for relevance.
3. **Pruning:** Outdated or low-priority content is pruned from the snapshot.
4. **Snapshot Update:** The current snapshot is updated and versioned.
5. **Feedback Loop:** Optionally, users can provide feedback on snapshot quality.
## 6. Snapshot Structure Example
```markdown
# Company Strategy Snapshot — June 2025

## Priorities (CEO Last Updated: June 15)
- "Focus on AI workflow tools, not chatbots." — CEO All-Hands
- Q3 Revenue Target: $220M (+15% YoY)

## Active Projects
- **Project Baker**: Beta launch delayed to August (Eng lead update)
- **Project Rise**: 85% customer retention (vs. 70% in April)

## Retired/Archived
- ~~Local data centers (migration to AWS completed)~~
```
## 7. Monitoring & Alerts
- **Drift Detection:** Alerts if a significant portion of the snapshot is outdated.
- **Feedback:** Users can rate the snapshot’s relevance and quality.

## 8. Glossary

- **Feeding:** Adding new documents to the pipeline.
- **Hooch:** Temporary storage for pruned content (retained for 30 days).
- **Starter:** The core snapshot file used for LLM context.

**Sourdough, like its namesake, thrives on regular care and quality ingredients.**
