"""Feature computation helpers."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Iterable, Mapping, Sequence
import cmath


@dataclass(frozen=True)
class BrightnessFeature:
    average_brightness: float
    histogram: list[int]


@dataclass(frozen=True)
class AudioFeature:
    rms: float
    energy: float
    band_energy: Mapping[str, float]


@dataclass(frozen=True)
class SizeFeature:
    original_resolution: tuple[int, int]
    current_resolution: tuple[int, int]
    scale_ratio: tuple[float, float]
    changed: bool


def _pixel_luminance(pixel: object) -> float:
    if isinstance(pixel, (tuple, list)):
        if not pixel:
            return 0.0
        if len(pixel) >= 3:
            r, g, b = pixel[:3]
            return 0.2126 * float(r) + 0.7152 * float(g) + 0.0722 * float(b)
        return float(pixel[0])
    return float(pixel)


def compute_brightness_feature(frame: Sequence[Sequence[object]]) -> BrightnessFeature:
    """Compute average brightness and histogram for a frame.

    Frame pixels may be grayscale values or RGB/RGBA tuples.
    """

    histogram = [0] * 256
    total = 0.0
    count = 0
    for row in frame:
        for pixel in row:
            value = _pixel_luminance(pixel)
            value = max(0.0, min(255.0, value))
            histogram[int(value)] += 1
            total += value
            count += 1
    average = total / count if count else 0.0
    return BrightnessFeature(average_brightness=average, histogram=histogram)


def _compute_rms(samples: Sequence[float]) -> float:
    if not samples:
        return 0.0
    mean_square = sum(sample * sample for sample in samples) / len(samples)
    return sqrt(mean_square)


def _compute_energy(samples: Sequence[float]) -> float:
    return sum(sample * sample for sample in samples)


def _compute_band_energy(
    samples: Sequence[float], sample_rate: int, bands: Iterable[tuple[float, float]]
) -> dict[str, float]:
    if not samples or sample_rate <= 0:
        return {f"{low}-{high}": 0.0 for low, high in bands}

    band_energy: dict[str, float] = {f"{low}-{high}": 0.0 for low, high in bands}
    n = len(samples)
    for k in range(n):
        frequency = k * sample_rate / n
        for low, high in bands:
            if low <= frequency < high:
                exponent = -2j * cmath.pi * k / n
                value = sum(
                    sample * cmath.exp(exponent * index)
                    for index, sample in enumerate(samples)
                )
                magnitude = abs(value) / n
                band_energy[f"{low}-{high}"] += magnitude * magnitude
                break
    return band_energy


def compute_audio_feature(
    samples: Sequence[float],
    sample_rate: int,
    bands: Iterable[tuple[float, float]] = ((0.0, 200.0), (200.0, 2000.0), (2000.0, 8000.0)),
) -> AudioFeature:
    """Compute RMS, energy, and band energy from audio samples."""

    rms = _compute_rms(samples)
    energy = _compute_energy(samples)
    band_energy = _compute_band_energy(samples, sample_rate, bands)
    return AudioFeature(rms=rms, energy=energy, band_energy=band_energy)


def compute_size_feature(
    original_resolution: tuple[int, int], current_resolution: tuple[int, int]
) -> SizeFeature:
    """Compute scale ratio and change flag between resolutions."""

    original_width, original_height = original_resolution
    current_width, current_height = current_resolution
    scale_ratio = (
        current_width / original_width if original_width else 0.0,
        current_height / original_height if original_height else 0.0,
    )
    changed = original_resolution != current_resolution
    return SizeFeature(
        original_resolution=original_resolution,
        current_resolution=current_resolution,
        scale_ratio=scale_ratio,
        changed=changed,
    )
