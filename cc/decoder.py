from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator

from .packets import AudioPacket, FramePacket


@dataclass(frozen=True)
class VideoStreamInfo:
    width: int
    height: int
    pix_fmt: str


@dataclass(frozen=True)
class AudioStreamInfo:
    channels: int
    sample_rate: int
    sample_fmt: str


class FFmpegDecoder:
    """Decode audio/video using the ffmpeg CLI and pipes."""

    def __init__(self, input_path: str | Path, *, ffmpeg_path: str = "ffmpeg") -> None:
        self.input_path = str(input_path)
        self.ffmpeg_path = ffmpeg_path

    def iter_frames(self) -> Iterable[FramePacket]:
        video_info = self._get_video_info()
        frame_pts = list(self._iter_frame_pts())
        frame_size = video_info.width * video_info.height * 3

        cmd = [
            self.ffmpeg_path,
            "-i",
            self.input_path,
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-",
        ]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if process.stdout is None:
            raise RuntimeError("Failed to open ffmpeg stdout pipe")

        for pts in frame_pts:
            frame_bytes = process.stdout.read(frame_size)
            if len(frame_bytes) < frame_size:
                break
            yield FramePacket(
                frame=frame_bytes,
                pts=pts,
                size=frame_size,
                brightness_stats=_brightness_stats(frame_bytes),
            )

        process.stdout.close()
        process.wait()

    def iter_audio(self) -> Iterable[AudioPacket]:
        audio_info = self._get_audio_info()
        audio_frames = list(self._iter_audio_frames())
        bytes_per_sample = 2
        frame_sample_bytes = audio_info.channels * bytes_per_sample

        cmd = [
            self.ffmpeg_path,
            "-i",
            self.input_path,
            "-f",
            "s16le",
            "-acodec",
            "pcm_s16le",
            "-ac",
            str(audio_info.channels),
            "-ar",
            str(audio_info.sample_rate),
            "-",
        ]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if process.stdout is None:
            raise RuntimeError("Failed to open ffmpeg stdout pipe")

        for pts, sample_count in audio_frames:
            chunk_size = sample_count * frame_sample_bytes
            samples = process.stdout.read(chunk_size)
            if len(samples) < chunk_size:
                break
            yield AudioPacket(samples=samples, pts=pts)

        process.stdout.close()
        process.wait()

    def _get_video_info(self) -> VideoStreamInfo:
        payload = self._run_ffprobe_json(
            ["-select_streams", "v:0", "-show_streams"]
        )
        stream = payload["streams"][0]
        return VideoStreamInfo(
            width=int(stream["width"]),
            height=int(stream["height"]),
            pix_fmt=stream.get("pix_fmt", "rgb24"),
        )

    def _get_audio_info(self) -> AudioStreamInfo:
        payload = self._run_ffprobe_json(
            ["-select_streams", "a:0", "-show_streams"]
        )
        stream = payload["streams"][0]
        return AudioStreamInfo(
            channels=int(stream["channels"]),
            sample_rate=int(stream["sample_rate"]),
            sample_fmt=stream.get("sample_fmt", "s16"),
        )

    def _iter_frame_pts(self) -> Iterator[float]:
        payload = self._run_ffprobe_json(
            ["-select_streams", "v:0", "-show_frames"]
        )
        for frame in payload.get("frames", []):
            if frame.get("media_type") != "video":
                continue
            pts = frame.get("pts_time") or frame.get("best_effort_timestamp_time")
            if pts is None:
                continue
            yield float(pts)

    def _iter_audio_frames(self) -> Iterator[tuple[float, int]]:
        payload = self._run_ffprobe_json(
            ["-select_streams", "a:0", "-show_frames"]
        )
        for frame in payload.get("frames", []):
            if frame.get("media_type") != "audio":
                continue
            pts = frame.get("pts_time") or frame.get("best_effort_timestamp_time")
            sample_count = frame.get("pkt_samples") or frame.get("nb_samples")
            if pts is None or sample_count is None:
                continue
            yield float(pts), int(sample_count)

    def _run_ffprobe_json(self, args: list[str]) -> dict:
        cmd = [
            self.ffmpeg_path.replace("ffmpeg", "ffprobe"),
            "-v",
            "error",
            "-of",
            "json",
            *args,
            self.input_path,
        ]
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)


def _brightness_stats(frame_bytes: bytes) -> dict[str, float]:
    if not frame_bytes:
        return {"mean": 0.0, "min": 0.0, "max": 0.0}
    values = frame_bytes
    total = 0
    min_value = 255
    max_value = 0
    for value in values:
        total += value
        if value < min_value:
            min_value = value
        if value > max_value:
            max_value = value
    mean = total / len(values)
    return {"mean": float(mean), "min": float(min_value), "max": float(max_value)}
