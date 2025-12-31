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
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Optional


@dataclass(frozen=True)
class FramePacket:
    frame: bytes
    pts: float
    size: int
    brightness_stats: dict[str, float]


@dataclass(frozen=True)
class AudioPacket:
    samples: bytes
    pts: float


@dataclass(frozen=True)
class AVPacket:
    pts: float
    frame: Optional[FramePacket] = None
    audio: Optional[AudioPacket] = None


def iter_av_packets(
    frames: Iterable[FramePacket],
    audio_packets: Iterable[AudioPacket],
    *,
    tolerance: float = 1e-3,
) -> Iterable[AVPacket]:
    """Align audio and video packets by PTS.

    If both packets are within the tolerance, emit a combined packet. Otherwise
    emit whichever packet has the earlier timestamp.
    """

    frame_iter = iter(frames)
    audio_iter = iter(audio_packets)

    next_frame: Optional[FramePacket] = next(frame_iter, None)
    next_audio: Optional[AudioPacket] = next(audio_iter, None)

    while next_frame is not None or next_audio is not None:
        if next_frame is None:
            yield AVPacket(pts=next_audio.pts, audio=next_audio)
            next_audio = next(audio_iter, None)
            continue
        if next_audio is None:
            yield AVPacket(pts=next_frame.pts, frame=next_frame)
            next_frame = next(frame_iter, None)
            continue

        pts_delta = next_frame.pts - next_audio.pts
        if abs(pts_delta) <= tolerance:
            pts = (next_frame.pts + next_audio.pts) / 2.0
            yield AVPacket(pts=pts, frame=next_frame, audio=next_audio)
            next_frame = next(frame_iter, None)
            next_audio = next(audio_iter, None)
        elif pts_delta < 0:
            yield AVPacket(pts=next_frame.pts, frame=next_frame)
            next_frame = next(frame_iter, None)
        else:
            yield AVPacket(pts=next_audio.pts, audio=next_audio)
            next_audio = next(audio_iter, None)


__all__ = [
    "FramePacket",
    "AudioPacket",
    "AVPacket",
    "iter_av_packets",
]
