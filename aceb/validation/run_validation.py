from __future__ import annotations

from aceb.config import BenchmarkConfig
from aceb.eval.comparison import ComparisonResult, compare_baseline_agents_on_episodes, summarize_by_agent
from aceb.validation.validation_set import get_validation_episode_ids


def run_validation(config: BenchmarkConfig) -> ComparisonResult:
    return compare_baseline_agents_on_episodes(config, get_validation_episode_ids())


def run_validation_with_summary(config: BenchmarkConfig) -> dict[str, object]:
    comparison = run_validation(config)
    summary = summarize_by_agent(comparison)
    return {
        "comparison": comparison,
        "summary": summary,
    }


def validate_behavioral_separation(summary: dict[str, dict[str, float | None]]) -> dict[str, bool]:
    random_summary = summary["RandomAgent"]
    static_summary = summary["StaticShiftAgent"]
    adaptive_summary = summary["AdaptiveShiftAgent"]

    static_cdl = static_summary["cdl"]
    adaptive_cdl = adaptive_summary["cdl"]

    return {
        "random_vs_static_pcm": random_summary["pcm"] < static_summary["pcm"],
        "adaptive_vs_static_cdl": (
            adaptive_cdl is not None and (static_cdl is None or adaptive_cdl <= static_cdl)
        ),
        "adaptive_vs_static_pr": adaptive_summary["pr"] <= static_summary["pr"],
    }
