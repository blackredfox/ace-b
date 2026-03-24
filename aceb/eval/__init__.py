"""Core evaluation utilities for the ACE-B benchmark."""

from .comparison import AgentEpisodeComparison, ComparisonResult, compare_baseline_agents_on_episodes, summarize_by_agent
from .core_metrics import compute_cdl, compute_pcm, compute_pr, evaluate_core_metrics
from .evidence_summary import EvidenceClaim, EvidenceSummary, build_evidence_summary, render_evidence_summary_markdown
from .types import CoreMetricResult

__all__ = [
    "AgentEpisodeComparison",
    "ComparisonResult",
    "CoreMetricResult",
    "EvidenceClaim",
    "EvidenceSummary",
    "build_evidence_summary",
    "compare_baseline_agents_on_episodes",
    "compute_pcm",
    "compute_cdl",
    "compute_pr",
    "evaluate_core_metrics",
    "render_evidence_summary_markdown",
    "summarize_by_agent",
]

