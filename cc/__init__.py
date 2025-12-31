"""Core interfaces for frame de-duplication."""

from cc.config import DedupeConfig, StrategyConfig, load_config
from cc.pipeline import FrameDeduper, FrameMetrics
from cc.strategies import BaseStrategy, StrategyDecision, StrategyRegistry

__all__ = [
    "BaseStrategy",
    "DedupeConfig",
    "FrameDeduper",
    "FrameMetrics",
    "StrategyConfig",
    "StrategyDecision",
    "StrategyRegistry",
    "load_config",
]
