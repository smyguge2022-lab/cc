"""Factory helpers for selecting platform-specific virtual camera sinks."""

from __future__ import annotations

import sys
from typing import Type

from .base import VirtualCameraSink
from .linux import LinuxVirtualCameraSink
from .macos import MacOSVirtualCameraSink
from .windows import WindowsVirtualCameraSink


def default_sink_cls() -> Type[VirtualCameraSink]:
    """Return the platform-specific sink implementation."""

    if sys.platform.startswith("win"):
        return WindowsVirtualCameraSink
    if sys.platform == "darwin":
        return MacOSVirtualCameraSink
    return LinuxVirtualCameraSink


def create_default_sink() -> VirtualCameraSink:
    """Instantiate the default sink for the current platform."""

    return default_sink_cls()()
