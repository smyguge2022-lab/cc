from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Iterable, List, Protocol, Sequence


class PacketWithFingerprint(Protocol):
    timestamp: float

    def fingerprint(self) -> str: ...


DedupHistory = List[PacketWithFingerprint]


class DedupStrategy(ABC):
    """Interface for deduplication strategies."""

    @abstractmethod
    def should_drop(self, packet: PacketWithFingerprint, history: DedupHistory) -> bool:
        """Return True if packet should be dropped as duplicate."""

    def score(self, packet: PacketWithFingerprint, history: DedupHistory) -> float:
        return 1.0 if self.should_drop(packet, history) else 0.0


@dataclass(frozen=True)
class ExactHashStrategy(DedupStrategy):
    """Drop if packet fingerprint already exists in history."""

    def should_drop(self, packet: PacketWithFingerprint, history: DedupHistory) -> bool:
        fingerprint = packet.fingerprint()
        return any(previous.fingerprint() == fingerprint for previous in history)


@dataclass(frozen=True)
class TimeWindowStrategy(DedupStrategy):
    """Drop if fingerprint repeats within a time window."""

    window_seconds: float

    def should_drop(self, packet: PacketWithFingerprint, history: DedupHistory) -> bool:
        fingerprint = packet.fingerprint()
        cutoff = packet.timestamp - self.window_seconds
        return any(
            previous.fingerprint() == fingerprint and previous.timestamp >= cutoff
            for previous in history
        )


@dataclass(frozen=True)
class WeightedCompositeStrategy(DedupStrategy):
    """Combine multiple strategies with weights and a drop threshold."""

    strategies: Sequence[DedupStrategy]
    weights: Sequence[float]
    threshold: float

    def should_drop(self, packet: PacketWithFingerprint, history: DedupHistory) -> bool:
        if not self.strategies:
            return False
        score = 0.0
        for strategy, weight in zip(self.strategies, self.weights, strict=False):
            score += strategy.score(packet, history) * weight
        return score >= self.threshold


def build_weighted_composite(
    strategies: Iterable[DedupStrategy],
    weights: Iterable[float],
    threshold: float,
) -> WeightedCompositeStrategy:
    strategies_list = list(strategies)
    weights_list = list(weights)
    if len(strategies_list) != len(weights_list):
        raise ValueError("Strategies and weights must have the same length.")
    return WeightedCompositeStrategy(
        strategies=strategies_list,
        weights=weights_list,
        threshold=threshold,
    )
