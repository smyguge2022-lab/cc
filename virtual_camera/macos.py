"""macOS virtual camera sinks."""

from __future__ import annotations

from .base import VirtualCameraSink


class MacOSVirtualCameraSink(VirtualCameraSink):
    """Virtual camera sink for macOS.

    Consider AVFoundation with a CoreMediaIO extension.
    """

    def open(self, width: int, height: int, fps: float) -> None:
        raise NotImplementedError(
            "macOS virtual camera sink not implemented. "
            "Consider AVFoundation + CoreMediaIO extension."
        )

    def write(self, frame: bytes) -> None:
        raise NotImplementedError("macOS virtual camera sink not implemented.")

    def close(self) -> None:
        raise NotImplementedError("macOS virtual camera sink not implemented.")
