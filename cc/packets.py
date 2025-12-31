"""Packet structures that carry feature metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Sequence


@dataclass
class FramePacket:
    frame: Sequence[Sequence[Any]]
    width: int
    height: int
    features: Dict[str, Any] = field(default_factory=dict)

    def add_feature(self, name: str, feature: Any) -> None:
        self.features[name] = feature


@dataclass
class AVPacket:
    audio_samples: Sequence[float]
    sample_rate: int
    frame: Sequence[Sequence[Any]]
    width: int
    height: int
    features: Dict[str, Any] = field(default_factory=dict)

    def add_feature(self, name: str, feature: Any) -> None:
        self.features[name] = feature
