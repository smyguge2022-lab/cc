"""Linux virtual camera sinks."""

from __future__ import annotations

from .base import VirtualCameraSink


class LinuxVirtualCameraSink(VirtualCameraSink):
    """Virtual camera sink for Linux.

    Consider using v4l2loopback to create a device node and write frames.
    """

    def open(self, width: int, height: int, fps: float) -> None:
        raise NotImplementedError(
            "Linux virtual camera sink not implemented. "
            "Consider v4l2loopback integration."
        )

    def write(self, frame: bytes) -> None:
        raise NotImplementedError("Linux virtual camera sink not implemented.")

    def close(self) -> None:
        raise NotImplementedError("Linux virtual camera sink not implemented.")
