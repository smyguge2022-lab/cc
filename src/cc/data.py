from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class Metadata:
    source: str
    tags: Dict[str, str] = field(default_factory=dict)
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FramePacket:
    frame_id: str
    timestamp: float
    data: bytes
    metadata: Optional[Metadata] = None
    features: Dict[str, Any] = field(default_factory=dict)

    def fingerprint(self) -> str:
        return self.frame_id


@dataclass(frozen=True)
class AudioPacket:
    audio_id: str
    timestamp: float
    data: bytes
    metadata: Optional[Metadata] = None
    features: Dict[str, Any] = field(default_factory=dict)

    def fingerprint(self) -> str:
        return self.audio_id
