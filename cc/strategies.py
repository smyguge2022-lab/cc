from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Callable

from cc.config import DedupeConfig, StrategyConfig


@dataclass(frozen=True)
class StrategyDecision:
    keep: bool
    reason: str
    metrics: dict[str, Any] | None = None


class BaseStrategy:
    name: str = "base"

    def decide(
        self,
        previous_frame: Any | None,
        current_frame: Any,
        config: DedupeConfig,
        strategy_config: StrategyConfig,
    ) -> StrategyDecision:
        raise NotImplementedError


class StrategyRegistry:
    _registry: dict[str, Callable[[], BaseStrategy]] = {}

    @classmethod
    def register(cls, name: str, factory: Callable[[], BaseStrategy]) -> None:
        cls._registry[name] = factory

    @classmethod
    def create(cls, name: str) -> BaseStrategy:
        if name not in cls._registry:
            raise KeyError(f"Strategy '{name}' is not registered.")
        return cls._registry[name]()

    @classmethod
    def available(cls) -> list[str]:
        return sorted(cls._registry.keys())


class HashDiffStrategy(BaseStrategy):
    name = "hash_diff"

    def decide(
        self,
        previous_frame: Any | None,
        current_frame: Any,
        config: DedupeConfig,
        strategy_config: StrategyConfig,
    ) -> StrategyDecision:
        if previous_frame is None:
            return StrategyDecision(keep=True, reason="no_previous_frame")
        previous_bytes = _frame_bytes(previous_frame)
        current_bytes = _frame_bytes(current_frame)
        diff_ratio = _byte_diff_ratio(previous_bytes, current_bytes)
        threshold = strategy_config.threshold
        if threshold is None:
            threshold = config.threshold
        keep = diff_ratio > threshold
        reason = "diff_above_threshold" if keep else "diff_below_threshold"
        metrics = {
            "diff_ratio": diff_ratio,
            "threshold": threshold,
            "hash_prev": _sha_digest(previous_bytes),
            "hash_curr": _sha_digest(current_bytes),
        }
        return StrategyDecision(keep=keep, reason=reason, metrics=metrics)


StrategyRegistry.register(HashDiffStrategy.name, HashDiffStrategy)


def _frame_bytes(frame: Any) -> bytes:
    if isinstance(frame, (bytes, bytearray, memoryview)):
        return bytes(frame)
    data = getattr(frame, "data", None)
    if isinstance(data, (bytes, bytearray, memoryview)):
        return bytes(data)
    raise TypeError("Frame must be bytes-like or expose a 'data' attribute.")


def _byte_diff_ratio(previous: bytes, current: bytes) -> float:
    if not previous and not current:
        return 0.0
    max_len = max(len(previous), len(current))
    if max_len == 0:
        return 0.0
    diff = 0
    for idx in range(max_len):
        prev_byte = previous[idx] if idx < len(previous) else None
        curr_byte = current[idx] if idx < len(current) else None
        if prev_byte != curr_byte:
            diff += 1
    return diff / max_len


def _sha_digest(payload: bytes) -> str:
    return sha256(payload).hexdigest()
