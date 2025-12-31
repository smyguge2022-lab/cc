"""Base abstractions for virtual camera sinks."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class VideoFormat:
    """Describes the expected output format for a virtual camera."""

    width: int
    height: int
    fps: float


class VirtualCameraSink(ABC):
    """Abstract sink for publishing frames to a virtual camera device."""

    @abstractmethod
    def open(self, width: int, height: int, fps: float) -> None:
        """Open the sink with the requested format."""

    @abstractmethod
    def write(self, frame: bytes) -> None:
        """Write a single frame to the sink."""

    @abstractmethod
    def close(self) -> None:
        """Close the sink and release any resources."""


class SupportsVirtualCameraSink(Protocol):
    """Protocol for factories that can build virtual camera sinks."""

    def create(self) -> VirtualCameraSink:
        """Create a new virtual camera sink instance."""
        ...
