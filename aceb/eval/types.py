from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CoreMetricResult:
    episode_id: str
    pcm: float
    cdl: int | None
    pr: float
