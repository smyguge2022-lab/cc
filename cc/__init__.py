"""Core feature extraction and packet structures."""

from .features import AudioFeature, BrightnessFeature, SizeFeature
from .packets import AVPacket, FramePacket
from .extractors import (
    attach_audio_feature,
    attach_brightness_feature,
    attach_size_feature,
)

__all__ = [
    "AudioFeature",
    "BrightnessFeature",
    "SizeFeature",
    "FramePacket",
    "AVPacket",
    "attach_brightness_feature",
    "attach_audio_feature",
    "attach_size_feature",
]
