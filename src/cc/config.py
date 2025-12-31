from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .dedup import ExactHashStrategy, TimeWindowStrategy, WeightedCompositeStrategy


@dataclass(frozen=True)
class StrategyConfig:
    name: str
    enabled: bool
    weight: float
    params: Dict[str, Any]


@dataclass(frozen=True)
class PipelineConfig:
    threshold: float
    strategies: List[StrategyConfig]


_STRATEGY_REGISTRY = {
    "exact_hash": ExactHashStrategy,
    "time_window": TimeWindowStrategy,
}


def load_config(path: str | Path) -> PipelineConfig:
    payload = yaml.safe_load(Path(path).read_text())
    dedup_config = payload.get("dedup", {})
    threshold = float(dedup_config.get("threshold", 1.0))
    strategies: List[StrategyConfig] = []
    for entry in dedup_config.get("strategies", []):
        strategies.append(
            StrategyConfig(
                name=entry["name"],
                enabled=bool(entry.get("enabled", True)),
                weight=float(entry.get("weight", 1.0)),
                params=entry.get("params", {}),
            )
        )
    return PipelineConfig(threshold=threshold, strategies=strategies)


def build_dedup_strategy(config: PipelineConfig) -> WeightedCompositeStrategy:
    strategies = []
    weights = []
    for entry in config.strategies:
        if not entry.enabled:
            continue
        strategy_cls = _STRATEGY_REGISTRY.get(entry.name)
        if strategy_cls is None:
            raise ValueError(f"Unknown strategy '{entry.name}'.")
        strategies.append(strategy_cls(**entry.params))
        weights.append(entry.weight)
    return WeightedCompositeStrategy(
        strategies=strategies,
        weights=weights,
        threshold=config.threshold,
    )
