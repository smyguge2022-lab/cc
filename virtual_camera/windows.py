"""Windows virtual camera sinks."""

from __future__ import annotations

from .base import VirtualCameraSink


class WindowsVirtualCameraSink(VirtualCameraSink):
    """Virtual camera sink for Windows.

    Consider integrating with OBS VirtualCam or DirectShow-based devices.
    """

    def open(self, width: int, height: int, fps: float) -> None:
        raise NotImplementedError(
            "Windows virtual camera sink not implemented. "
            "Consider OBS VirtualCam or DirectShow integration."
        )

    def write(self, frame: bytes) -> None:
        raise NotImplementedError("Windows virtual camera sink not implemented.")

    def close(self) -> None:
        raise NotImplementedError("Windows virtual camera sink not implemented.")
