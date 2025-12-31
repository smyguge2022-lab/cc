from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .decoder import FFmpegDecoder
from .packets import AVPacket, iter_av_packets


@dataclass
class DecodeStage:
    ffmpeg_path: str = "ffmpeg"
    pts_tolerance: float = 1e-3

    def run(self, input_path: str | Path) -> Iterable[AVPacket]:
        decoder = FFmpegDecoder(input_path, ffmpeg_path=self.ffmpeg_path)
        frames = decoder.iter_frames()
        audio = decoder.iter_audio()
        return iter_av_packets(frames, audio, tolerance=self.pts_tolerance)


class Pipeline:
    def __init__(self, *, ffmpeg_path: str = "ffmpeg") -> None:
        self.decode_stage = DecodeStage(ffmpeg_path=ffmpeg_path)

    def decode(self, input_path: str | Path) -> Iterable[AVPacket]:
        return self.decode_stage.run(input_path)
