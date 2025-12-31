from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from cc.config import DedupeConfig, StrategyConfig
from cc.strategies import BaseStrategy, StrategyDecision, StrategyRegistry


@dataclass
class FrameMetrics:
    total_frames: int = 0
    kept_frames: int = 0
    start_time: float = field(default_factory=time.perf_counter)

    def record(self, kept: bool) -> None:
        self.total_frames += 1
        if kept:
            self.kept_frames += 1

    @property
    def dropped_frames(self) -> int:
        return self.total_frames - self.kept_frames

    def fps(self) -> float:
        elapsed = time.perf_counter() - self.start_time
        if elapsed <= 0:
            return 0.0
        return self.total_frames / elapsed

    def drop_rate(self) -> float:
        if self.total_frames == 0:
            return 0.0
        return self.dropped_frames / self.total_frames


class FrameDeduper:
    def __init__(self, config: DedupeConfig) -> None:
        self.config = config
        self.metrics = FrameMetrics()
        self._strategies = self._build_strategies()
        self._previous_frame: Any | None = None
        self._logger = logging.getLogger("cc.dedupe")
        if self.config.debug:
            logging.basicConfig(level=logging.INFO, format="%(message)s")

    def _build_strategies(self) -> list[tuple[BaseStrategy, StrategyConfig]]:
        strategies: list[tuple[BaseStrategy, StrategyConfig]] = []
        for name, strategy_config in self.config.strategies.items():
            strategy = StrategyRegistry.create(name)
            strategies.append((strategy, strategy_config))
        return strategies

    def process_frame(self, frame: Any) -> bool:
        decisions: list[tuple[str, StrategyDecision]] = []
        keep = True
        for strategy, strategy_config in self._strategies:
            if not strategy_config.enabled:
                decisions.append(
                    (strategy.name, StrategyDecision(True, "strategy_disabled"))
                )
                continue
            decision = strategy.decide(
                self._previous_frame,
                frame,
                self.config,
                strategy_config,
            )
            decisions.append((strategy.name, decision))
            if not decision.keep:
                keep = False
        self.metrics.record(keep)
        self._log_debug(frame, keep, decisions)
        if keep:
            self._previous_frame = frame
        return keep

    def _log_debug(
        self,
        frame: Any,
        keep: bool,
        decisions: list[tuple[str, StrategyDecision]],
    ) -> None:
        if not self.config.debug:
            return
        fps = self.metrics.fps()
        drop_rate = self.metrics.drop_rate()
        decision_lines = [
            f"- {name}: {'keep' if decision.keep else 'drop'} ({decision.reason})"
            for name, decision in decisions
        ]
        self._logger.info(
            "frame=%s keep=%s fps=%.2f drop_rate=%.2f\n%s",
            _frame_id(frame),
            keep,
            fps,
            drop_rate,
            "\n".join(decision_lines),
        )


def _frame_id(frame: Any) -> str:
    identifier = getattr(frame, "id", None)
    if identifier is not None:
        return str(identifier)
    return hex(id(frame))
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
