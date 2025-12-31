"""Core pipeline components for cc."""

from .config import PipelineConfig, StrategyConfig, load_config
from .data import AudioPacket, FramePacket, Metadata
from .dedup import (
    DedupHistory,
    DedupStrategy,
    ExactHashStrategy,
    TimeWindowStrategy,
    WeightedCompositeStrategy,
)
from .pipeline import Pipeline
from .stages import PipelineStage

__all__ = [
    "AudioPacket",
    "DedupHistory",
    "DedupStrategy",
    "ExactHashStrategy",
    "FramePacket",
    "Metadata",
    "Pipeline",
    "PipelineConfig",
    "PipelineStage",
    "StrategyConfig",
    "TimeWindowStrategy",
    "WeightedCompositeStrategy",
    "load_config",
]
