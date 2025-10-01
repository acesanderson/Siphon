"""
Sourdough - Auto-updating, auto-curated strategic knowledge base

Specialized ProcessedCorpus that maintains itself within token limits,
auto-prunes outdated content, and provides strategic intelligence capabilities.
Uses composition rather than inheritance for flexibility.
"""

import time
from typing import Optional, Any
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field

from siphon.data.processed_content import ProcessedContent
from siphon.data.type_definitions.source_type import SourceType
from .processed_corpus import ProcessedCorpus


class SourdoughSnapshot(BaseModel):
    """Represents a versioned snapshot of the Sourdough state."""

    timestamp: int = Field(..., description="Unix timestamp of snapshot creation")
    version: str = Field(..., description="Semantic version of this snapshot")
    content_count: int = Field(
        ..., description="Number of content items in this snapshot"
    )
    token_count: int = Field(..., description="Estimated token count of snapshot")
    summary: str = Field(..., description="Executive summary of strategic content")


class Sourdough:
    """
    Auto-updating strategic knowledge base that maintains itself within constraints.

    Like sourdough starter, this requires regular feeding and maintenance to stay healthy.
    Automatically prunes outdated content and maintains strategic focus.
    """

    def __init__(
        self,
        max_tokens: int = 4000,
        focus_areas: Optional[list[str]] = None,
        auto_prune: bool = True,
    ):
        """
        Initialize Sourdough strategic knowledge base.

        Args:
            max_tokens: Maximum tokens to maintain in current snapshot
            focus_areas: Strategic focus areas to prioritize (e.g., ["AI", "strategy", "product"])
            auto_prune: Whether to automatically prune content on updates
        """
        # Core corpus management (composition, not inheritance)
        self._corpus = ProcessedCorpus.from_processed_content_list([])

        # Sourdough-specific configuration
        self.max_tokens = max_tokens
        self.focus_areas = focus_areas or []
        self.auto_prune = auto_prune

        # State management
        self._snapshot_history: list[SourdoughSnapshot] = []
        self._last_update: int = int(time.time())
        self._drift_threshold = 0.3  # 30% content change triggers drift alert

        # Persistence (matches your design spec)
        self._snapshot_file = Path("current_strategy.md")

    # ============================================================================
    # Core Sourdough Operations (Auto-curation)
    # ============================================================================

    def feed(self, content: ProcessedContent | list[ProcessedContent]) -> None:
        """
        Add new content to the Sourdough (feeding the starter).

        Args:
            content: Single ProcessedContent or list of content to add
        """
        if isinstance(content, ProcessedContent):
            content = [content]

        for item in content:
            self._corpus.add(item)

        if self.auto_prune:
            self._auto_prune()

        self._last_update = int(time.time())
        print(f"Fed Sourdough with {len(content)} new items")

    def _auto_prune(self) -> None:
        """
        Automatically prune content to stay within token limits.
        Prioritizes recent, high-value strategic content.
        """
        current_tokens = self._estimate_token_count()

        if current_tokens <= self.max_tokens:
            return

        print(f"Auto-pruning: {current_tokens} tokens > {self.max_tokens} limit")

        # Score content by strategic value
        scored_content = []
        for content in self._corpus:
            score = self._calculate_strategic_score(content)
            scored_content.append((score, content))

        # Sort by score (highest first) and keep top content
        scored_content.sort(reverse=True, key=lambda x: x[0])

        # Keep content until we hit token limit
        pruned_corpus = []
        running_tokens = 0

        for score, content in scored_content:
            _ = score  # Unused, but kept for clarity
            content_tokens = len(content.context.split()) * 1.3  # Rough token estimate

            if running_tokens + content_tokens <= self.max_tokens:
                pruned_corpus.append(content)
                running_tokens += content_tokens
            else:
                # Store pruned content in "hooch" (temporary storage)
                self._add_to_hooch(content)

        # Update corpus with pruned content
        self._corpus = ProcessedCorpus.from_processed_content_list(pruned_corpus)

        final_tokens = self._estimate_token_count()
        print(f"Pruning complete: {final_tokens} tokens remaining")

    def _calculate_strategic_score(self, content: ProcessedContent) -> float:
        """
        Calculate strategic value score for content prioritization.

        Returns:
            Score from 0.0 to 1.0 (higher = more strategic value)
        """
        score = 0.0

        # Recency bonus (content from last 30 days gets higher score)
        # TODO: Add timestamp to ProcessedContent for proper recency calculation
        score += 0.3  # Default recency score

        # Focus area relevance
        content_text = (
            content.title + " " + content.description + " " + content.context[:500]
        ).lower()

        focus_matches = sum(
            1 for area in self.focus_areas if area.lower() in content_text
        )
        if self.focus_areas:
            score += (focus_matches / len(self.focus_areas)) * 0.4

        # Source type weighting (prioritize certain types)
        source_weights = {
            SourceType.YOUTUBE: 0.1,  # Often tactical
            SourceType.GITHUB: 0.05,  # Technical, less strategic
            SourceType.ARTICLE: 0.15,
            SourceType.DOC: 0.2,  # Often strategic documents
            SourceType.AUDIO: 0.2,  # Meeting recordings, high value
        }
        score += source_weights.get(content.uri.sourcetype, 0.1)

        # Authority indicators (CEO, executive content)
        authority_keywords = ["ceo", "executive", "strategy", "roadmap", "okr"]
        authority_matches = sum(
            1 for keyword in authority_keywords if keyword in content_text
        )
        score += min(authority_matches * 0.05, 0.1)

        return min(score, 1.0)  # Cap at 1.0

    def _add_to_hooch(self, content: ProcessedContent) -> None:
        """
        Add pruned content to temporary storage ('hooch').
        Content is retained for 30 days before permanent deletion.
        """
        # TODO: Implement hooch storage (temporary retention of pruned content)
        # This could be a separate database table or file system storage
        print(f"Added to hooch: {content.title or content.uri.uri}")

    # ============================================================================
    # Snapshot Management (Core Sourdough Feature)
    # ============================================================================

    def get_current_snapshot(self) -> str:
        """
        Get the current strategic snapshot in markdown format.
        This is the main product of Sourdough - always fresh strategic intel.
        """
        if self._corpus.is_empty():
            return "# Strategic Snapshot\n\n*No strategic content available.*"

        snapshot_lines = [
            f"# Strategic Snapshot — {datetime.now().strftime('%B %Y')}",
            "",
            f"*Last updated: {datetime.fromtimestamp(self._last_update).strftime('%Y-%m-%d %H:%M')}*",
            f"*Content items: {len(self._corpus)} | Estimated tokens: {self._estimate_token_count()}*",
            "",
        ]

        # Group content by strategic themes
        themes = self._extract_strategic_themes()

        for theme, contents in themes.items():
            snapshot_lines.extend([f"## {theme}", ""])

            for content in contents:
                # Extract key insights from each piece of content
                insights = self._extract_key_insights(content)
                snapshot_lines.extend(
                    [
                        f"### {content.title or 'Strategic Update'}",
                        f"*Source: {content.uri.sourcetype.value}*",
                        "",
                        insights,
                        "",
                    ]
                )

        # Add strategic action items
        action_items = self._generate_action_items()
        if action_items:
            snapshot_lines.extend(["## Strategic Actions", "", action_items, ""])

        return "\n".join(snapshot_lines)

    def save_snapshot(self) -> str:
        """
        Save current snapshot to file and create version history.

        Returns:
            Version identifier of saved snapshot
        """
        snapshot_content = self.get_current_snapshot()

        # Save to current snapshot file
        self._snapshot_file.write_text(snapshot_content)

        # Create versioned snapshot for history
        version = f"v{len(self._snapshot_history) + 1}.{int(time.time())}"

        snapshot_record = SourdoughSnapshot(
            timestamp=int(time.time()),
            version=version,
            content_count=len(self._corpus),
            token_count=self._estimate_token_count(),
            summary=self._generate_executive_summary(),
        )

        self._snapshot_history.append(snapshot_record)

        # Save versioned snapshot file
        versioned_file = Path(f"strategy_snapshot_{version}.md")
        versioned_file.write_text(snapshot_content)

        print(f"Saved snapshot {version} with {len(self._corpus)} items")
        return version

    def load_snapshot(self, version: str) -> bool:
        """
        Load a specific snapshot version.

        Args:
            version: Version identifier to load

        Returns:
            True if snapshot was loaded successfully
        """
        # TODO: Implement snapshot loading from versioned files
        # This would restore the corpus state from a specific point in time
        raise NotImplementedError("Snapshot loading not yet implemented")

    # ============================================================================
    # Strategic Intelligence Operations
    # ============================================================================

    def _extract_strategic_themes(self) -> dict[str, list[ProcessedContent]]:
        """
        Group content by strategic themes for better organization.

        Returns:
            Dictionary mapping theme names to content lists
        """
        themes = {
            "Priorities & Objectives": [],
            "Active Projects": [],
            "Market Intelligence": [],
            "Organizational Updates": [],
            "Technical Strategy": [],
            "Other Strategic Content": [],
        }

        for content in self._corpus:
            content_text = (
                content.title + " " + content.description + " " + content.context[:500]
            ).lower()

            # Simple keyword-based theme classification
            if any(
                keyword in content_text
                for keyword in ["okr", "priority", "goal", "objective", "target"]
            ):
                themes["Priorities & Objectives"].append(content)
            elif any(
                keyword in content_text
                for keyword in ["project", "initiative", "launch", "beta"]
            ):
                themes["Active Projects"].append(content)
            elif any(
                keyword in content_text
                for keyword in ["market", "competitor", "industry", "customer"]
            ):
                themes["Market Intelligence"].append(content)
            elif any(
                keyword in content_text
                for keyword in ["hiring", "team", "organization", "culture"]
            ):
                themes["Organizational Updates"].append(content)
            elif any(
                keyword in content_text
                for keyword in [
                    "technical",
                    "architecture",
                    "platform",
                    "infrastructure",
                ]
            ):
                themes["Technical Strategy"].append(content)
            else:
                themes["Other Strategic Content"].append(content)

        # Remove empty themes
        return {theme: contents for theme, contents in themes.items() if contents}

    def _extract_key_insights(self, content: ProcessedContent) -> str:
        """
        Extract key strategic insights from a piece of content.

        Args:
            content: ProcessedContent to extract insights from

        Returns:
            Formatted insights text
        """
        # Use the summary if available, otherwise create excerpt
        if content.summary:
            return content.summary[:300] + ("..." if len(content.summary) > 300 else "")
        elif content.description:
            return content.description
        else:
            # Extract first meaningful paragraph from context
            paragraphs = content.context.split("\n\n")
            for para in paragraphs:
                if len(para.strip()) > 50:  # Skip short lines
                    excerpt = para.strip()[:300]
                    return excerpt + ("..." if len(para) > 300 else "")

            return "No summary available."

    def _generate_action_items(self) -> str:
        """
        Generate strategic action items based on current content.

        Returns:
            Formatted action items text
        """
        # TODO: Implement AI-powered action item generation
        # This could use LLM to analyze content and suggest strategic actions
        return "- Review strategic priorities based on recent updates\n- Monitor progress on active projects\n- Assess market intelligence for opportunities"

    def _generate_executive_summary(self) -> str:
        """
        Generate high-level executive summary of strategic state.

        Returns:
            Executive summary text
        """
        if self._corpus.is_empty():
            return "No strategic content available for summary."

        theme_count = len(self._extract_strategic_themes())
        content_count = len(self._corpus)

        return (
            f"Strategic snapshot containing {content_count} key items across "
            f"{theme_count} strategic themes. Focus areas: {', '.join(self.focus_areas) if self.focus_areas else 'general strategy'}."
        )

    # ============================================================================
    # Monitoring & Health Operations
    # ============================================================================

    def detect_drift(self) -> dict[str, Any]:
        """
        Detect if strategic content has significantly changed (drift detection).

        Returns:
            Drift analysis with recommendations
        """
        if len(self._snapshot_history) < 2:
            return {
                "drift_detected": False,
                "reason": "Insufficient history for comparison",
            }

        current_snapshot = self._snapshot_history[-1]
        previous_snapshot = self._snapshot_history[-2]

        # Calculate content change percentage
        content_change = abs(
            current_snapshot.content_count - previous_snapshot.content_count
        )
        change_percentage = content_change / max(previous_snapshot.content_count, 1)

        drift_detected = change_percentage > self._drift_threshold

        return {
            "drift_detected": drift_detected,
            "change_percentage": change_percentage,
            "threshold": self._drift_threshold,
            "recommendation": "Consider reviewing strategic focus areas"
            if drift_detected
            else "Strategic content is stable",
            "content_change": content_change,
            "timespan_hours": (current_snapshot.timestamp - previous_snapshot.timestamp)
            / 3600,
        }

    def get_health_status(self) -> dict[str, Any]:
        """
        Get comprehensive health status of the Sourdough.

        Returns:
            Health status and metrics
        """
        current_tokens = self._estimate_token_count()
        token_utilization = current_tokens / self.max_tokens

        # Assess content freshness (how recent is the newest content)
        hours_since_update = (time.time() - self._last_update) / 3600

        # Health scoring
        health_score = 1.0
        health_issues = []

        if token_utilization > 0.9:
            health_score -= 0.3
            health_issues.append("Near token limit")

        if hours_since_update > 168:  # 1 week
            health_score -= 0.2
            health_issues.append("Content may be stale")

        if self._corpus.is_empty():
            health_score = 0.0
            health_issues.append("No strategic content")

        return {
            "health_score": health_score,
            "status": "healthy"
            if health_score > 0.7
            else "needs_attention"
            if health_score > 0.3
            else "unhealthy",
            "token_utilization": token_utilization,
            "content_count": len(self._corpus),
            "hours_since_update": hours_since_update,
            "focus_areas": self.focus_areas,
            "issues": health_issues,
            "last_snapshot": self._snapshot_history[-1].version
            if self._snapshot_history
            else "none",
        }

    # ============================================================================
    # Utility Methods & Delegation to ProcessedCorpus
    # ============================================================================

    def _estimate_token_count(self) -> int:
        """
        Estimate total token count of current corpus.

        Returns:
            Estimated token count
        """
        if self._corpus.is_empty():
            return 0

        # Rough estimation: 1 token ≈ 0.75 words
        total_words = sum(len(content.context.split()) for content in self._corpus)
        return int(total_words * 1.3)

    # Delegate common operations to the internal corpus
    def search(self, query: str) -> ProcessedCorpus:
        """Search within strategic content."""
        return self._corpus.search(query)

    def filter_by_source_type(self, source_type: SourceType) -> ProcessedCorpus:
        """Filter strategic content by source type."""
        return self._corpus.filter_by_source_type(source_type)

    def get_source_type_counts(self) -> dict[SourceType, int]:
        """Get breakdown of content by source type."""
        return self._corpus.get_source_type_counts()

    def __len__(self) -> int:
        """Return number of items in strategic corpus."""
        return len(self._corpus)

    def __repr__(self) -> str:
        """String representation of Sourdough."""
        health = self.get_health_status()
        return (
            f"Sourdough(content={len(self._corpus)}, "
            f"tokens={self._estimate_token_count()}/{self.max_tokens}, "
            f"health={health['status']})"
        )

    # ============================================================================
    # Configuration & Management
    # ============================================================================

    def update_focus_areas(self, focus_areas: list[str]) -> None:
        """Update strategic focus areas and re-score content."""
        self.focus_areas = focus_areas
        if self.auto_prune:
            self._auto_prune()  # Re-evaluate with new focus areas

    def set_token_limit(self, max_tokens: int) -> None:
        """Update token limit and prune if necessary."""
        self.max_tokens = max_tokens
        if self.auto_prune:
            self._auto_prune()

    def export_for_llm(self) -> str:
        """
        Export current strategic content in format optimized for LLM consumption.

        Returns:
            Formatted strategic context for LLM prompts
        """
        snapshot = self.get_current_snapshot()

        # Add metadata for LLM context
        context_header = [
            "# Strategic Context",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"Content items: {len(self._corpus)}",
            f"Focus areas: {', '.join(self.focus_areas) if self.focus_areas else 'General strategy'}",
            "",
            "---",
            "",
        ]

        return "\n".join(context_header) + snapshot
