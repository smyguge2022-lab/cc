"""Feature extraction that attaches data to packets."""

from __future__ import annotations

from .features import (
    BrightnessFeature,
    AudioFeature,
    SizeFeature,
    compute_audio_feature,
    compute_brightness_feature,
    compute_size_feature,
)
from .packets import AVPacket, FramePacket


def attach_brightness_feature(packet: FramePacket) -> BrightnessFeature:
    """Compute and attach brightness feature to a frame packet."""

    feature = compute_brightness_feature(packet.frame)
    packet.add_feature("BrightnessFeature", feature)
    return feature


def attach_audio_feature(packet: AVPacket) -> AudioFeature:
    """Compute and attach audio feature to an AV packet."""

    feature = compute_audio_feature(packet.audio_samples, packet.sample_rate)
    packet.add_feature("AudioFeature", feature)
    return feature


def attach_size_feature(
    packet: FramePacket | AVPacket, original_resolution: tuple[int, int]
) -> SizeFeature:
    """Compute and attach size feature to a packet."""

    current_resolution = (packet.width, packet.height)
    feature = compute_size_feature(original_resolution, current_resolution)
    packet.add_feature("SizeFeature", feature)
    return feature
