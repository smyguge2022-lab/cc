"""Virtual camera sink abstractions."""

from .base import VideoFormat, VirtualCameraSink
from .factory import create_default_sink, default_sink_cls
from .linux import LinuxVirtualCameraSink
from .macos import MacOSVirtualCameraSink
from .windows import WindowsVirtualCameraSink

__all__ = [
    "VideoFormat",
    "VirtualCameraSink",
    "LinuxVirtualCameraSink",
    "MacOSVirtualCameraSink",
    "WindowsVirtualCameraSink",
    "create_default_sink",
    "default_sink_cls",
]
