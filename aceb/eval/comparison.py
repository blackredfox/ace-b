from __future__ import annotations

import hashlib
from dataclasses import dataclass

from aceb.agents.adaptive_shift_agent import AdaptiveShiftAgent
from aceb.agents.random_agent import RandomAgent
from aceb.agents.static_shift_agent import StaticShiftAgent
from aceb.config import BenchmarkConfig
from aceb.eval.core_metrics import evaluate_core_metrics
from aceb.generator.builder import build_episode_spec
from aceb.runner.episode_runner import run_episode
from aceb.env.environment import RCSEnvironment


@dataclass
class AgentEpisodeComparison:
    agent_name: str
    episode_id: str
    pcm: float
    cdl: int | None
    pr: float
    accuracy: float


@dataclass
class ComparisonResult:
    episodes: list[str]
    results: list[AgentEpisodeComparison]


def compare_baseline_agents_on_episodes(
    config: BenchmarkConfig,
    episode_ids: list[str],
) -> ComparisonResult:
    results: list[AgentEpisodeComparison] = []

    for episode_id in episode_ids:
        episode = build_episode_spec(config, episode_id)

        for agent_name, agent in _build_agents_for_episode(episode.alphabet, episode.seed):
            run_result = run_episode(RCSEnvironment(episode), agent)
            metrics = evaluate_core_metrics(episode, run_result.trajectory)
            results.append(
                AgentEpisodeComparison(
                    agent_name=agent_name,
                    episode_id=episode_id,
                    pcm=metrics.pcm,
                    cdl=metrics.cdl,
                    pr=metrics.pr,
                    accuracy=run_result.accuracy,
                )
            )

    return ComparisonResult(episodes=episode_ids.copy(), results=results)


def summarize_by_agent(comparison: ComparisonResult) -> dict[str, dict[str, float | None]]:
    grouped: dict[str, list[AgentEpisodeComparison]] = {}
    for result in comparison.results:
        grouped.setdefault(result.agent_name, []).append(result)

    summary: dict[str, dict[str, float | None]] = {}
    for agent_name, agent_results in grouped.items():
        cdl_values = [result.cdl for result in agent_results if result.cdl is not None]
        summary[agent_name] = {
            "pcm": sum(result.pcm for result in agent_results) / len(agent_results),
            "cdl": (sum(cdl_values) / len(cdl_values)) if cdl_values else None,
            "pr": sum(result.pr for result in agent_results) / len(agent_results),
            "accuracy": sum(result.accuracy for result in agent_results) / len(agent_results),
        }

    return summary


def _build_agents_for_episode(alphabet: list[str], episode_seed: int) -> list[tuple[str, object]]:
    return [
        ("RandomAgent", RandomAgent(alphabet=alphabet, seed=_derive_agent_seed(episode_seed, "random"))),
        ("StaticShiftAgent", StaticShiftAgent(alphabet=alphabet)),
        ("AdaptiveShiftAgent", AdaptiveShiftAgent(alphabet=alphabet)),
    ]


def _derive_agent_seed(episode_seed: int, agent_name: str) -> int:
    seed_material = f"{episode_seed}:{agent_name}".encode("utf-8")
    seed_digest = hashlib.sha256(seed_material).digest()
    return int.from_bytes(seed_digest[:8], byteorder="big", signed=False)
