from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, Iterable, Optional, Sequence, Tuple


@dataclass(frozen=True)
class FrameFeatures:
    brightness: Optional[float] = None
    audio_energy: Optional[float] = None
    audio_spectrum: Optional[Sequence[float]] = None
    resolution: Optional[Tuple[int, int]] = None


@dataclass(frozen=True)
class DedupConfig:
    brightness_threshold: float = 0.05
    audio_energy_threshold: float = 0.1
    audio_spectrum_threshold: float = 0.1
    resolution_threshold: float = 0.01
    fusion_mode: str = "AND"  # AND, OR, WEIGHTED
    weighted_threshold: float = 1.0
    weights: Dict[str, float] = field(
        default_factory=lambda: {
            "brightness": 1.0,
            "audio": 1.0,
            "resolution": 1.0,
        }
    )
    history_size: int = 5


@dataclass(frozen=True)
class ComparisonResult:
    brightness_duplicate: Optional[bool]
    audio_duplicate: Optional[bool]
    resolution_duplicate: Optional[bool]
    weighted_score: Optional[float]


def _normalized_diff(diff: float, threshold: float) -> float:
    if threshold <= 0:
        return 0.0 if diff == 0 else float("inf")
    return diff / threshold


def _spectrum_diff(
    current: Sequence[float],
    previous: Sequence[float],
) -> float:
    if not current or not previous:
        return 0.0
    length = min(len(current), len(previous))
    if length == 0:
        return 0.0
    total = sum(abs(current[i] - previous[i]) for i in range(length))
    return total / length


def _resolution_relative_diff(
    current: Tuple[int, int],
    previous: Tuple[int, int],
) -> float:
    cur_w, cur_h = current
    prev_w, prev_h = previous
    if cur_w <= 0 or cur_h <= 0 or prev_w <= 0 or prev_h <= 0:
        return float("inf")
    width_diff = abs(cur_w - prev_w) / max(cur_w, prev_w)
    height_diff = abs(cur_h - prev_h) / max(cur_h, prev_h)
    return max(width_diff, height_diff)


class Deduplicator:
    def __init__(self, config: DedupConfig) -> None:
        self._config = config
        self._history: Deque[FrameFeatures] = deque(maxlen=config.history_size)

    @property
    def history(self) -> Iterable[FrameFeatures]:
        return tuple(self._history)

    def compare(
        self,
        current: FrameFeatures,
        previous: FrameFeatures,
    ) -> ComparisonResult:
        brightness_duplicate = None
        if current.brightness is not None and previous.brightness is not None:
            diff = abs(current.brightness - previous.brightness)
            brightness_duplicate = diff < self._config.brightness_threshold

        audio_duplicate = None
        energy_diff = None
        spectrum_diff = None
        if current.audio_energy is not None and previous.audio_energy is not None:
            energy_diff = abs(current.audio_energy - previous.audio_energy)
        if current.audio_spectrum is not None and previous.audio_spectrum is not None:
            spectrum_diff = _spectrum_diff(current.audio_spectrum, previous.audio_spectrum)
        if energy_diff is not None or spectrum_diff is not None:
            energy_ok = (
                energy_diff is not None
                and energy_diff < self._config.audio_energy_threshold
            )
            spectrum_ok = (
                spectrum_diff is not None
                and spectrum_diff < self._config.audio_spectrum_threshold
            )
            audio_duplicate = energy_ok or spectrum_ok

        resolution_duplicate = None
        if current.resolution is not None and previous.resolution is not None:
            res_diff = _resolution_relative_diff(current.resolution, previous.resolution)
            resolution_duplicate = res_diff < self._config.resolution_threshold

        weighted_score = None
        if self._config.fusion_mode.upper() == "WEIGHTED":
            weighted_score = 0.0
            total_weight = 0.0
            if brightness_duplicate is not None and current.brightness is not None:
                diff = abs(current.brightness - previous.brightness)
                normalized = _normalized_diff(diff, self._config.brightness_threshold)
                weight = self._config.weights.get("brightness", 1.0)
                weighted_score += normalized * weight
                total_weight += weight
            if audio_duplicate is not None:
                best_normalized = None
                if energy_diff is not None:
                    best_normalized = _normalized_diff(
                        energy_diff, self._config.audio_energy_threshold
                    )
                if spectrum_diff is not None:
                    spectrum_normalized = _normalized_diff(
                        spectrum_diff, self._config.audio_spectrum_threshold
                    )
                    if best_normalized is None:
                        best_normalized = spectrum_normalized
                    else:
                        best_normalized = min(best_normalized, spectrum_normalized)
                if best_normalized is not None:
                    weight = self._config.weights.get("audio", 1.0)
                    weighted_score += best_normalized * weight
                    total_weight += weight
            if resolution_duplicate is not None and current.resolution is not None:
                res_diff = _resolution_relative_diff(
                    current.resolution, previous.resolution
                )
                normalized = _normalized_diff(res_diff, self._config.resolution_threshold)
                weight = self._config.weights.get("resolution", 1.0)
                weighted_score += normalized * weight
                total_weight += weight
            if total_weight:
                weighted_score /= total_weight

        return ComparisonResult(
            brightness_duplicate=brightness_duplicate,
            audio_duplicate=audio_duplicate,
            resolution_duplicate=resolution_duplicate,
            weighted_score=weighted_score,
        )

    def is_duplicate(self, current: FrameFeatures) -> bool:
        if not self._history:
            return False
        mode = self._config.fusion_mode.upper()
        for previous in self._history:
            result = self.compare(current, previous)
            if mode == "WEIGHTED":
                if result.weighted_score is None:
                    continue
                if result.weighted_score < self._config.weighted_threshold:
                    return True
                continue

            checks = [
                result.brightness_duplicate,
                result.audio_duplicate,
                result.resolution_duplicate,
            ]
            available = [check for check in checks if check is not None]
            if not available:
                continue
            if mode == "AND" and all(available):
                return True
            if mode == "OR" and any(available):
                return True
        return False

    def add(self, current: FrameFeatures) -> bool:
        duplicate = self.is_duplicate(current)
        self._history.append(current)
        return duplicate
