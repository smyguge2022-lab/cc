from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class PipelineStage(ABC):
    """Abstract pipeline stage."""

    @abstractmethod
    def process(self, packet: Any, context: dict[str, Any]) -> Any:
        """Process the packet and return the transformed packet."""
