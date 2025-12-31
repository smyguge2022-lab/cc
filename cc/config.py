from __future__ import annotations

import importlib
import importlib.util
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class StrategyConfig:
    enabled: bool = True
    threshold: float | None = None
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DedupeConfig:
    threshold: float = 0.1
    output_fps: int = 30
    debug: bool = False
    strategies: dict[str, StrategyConfig] = field(default_factory=dict)

    @staticmethod
    def from_dict(payload: dict[str, Any]) -> "DedupeConfig":
        strategies_payload = payload.get("strategies", {}) or {}
        strategies: dict[str, StrategyConfig] = {}
        for name, cfg in strategies_payload.items():
            cfg_data = cfg or {}
            strategies[name] = StrategyConfig(
                enabled=bool(cfg_data.get("enabled", True)),
                threshold=cfg_data.get("threshold"),
                params={
                    key: value
                    for key, value in cfg_data.items()
                    if key not in {"enabled", "threshold"}
                },
            )
        return DedupeConfig(
            threshold=float(payload.get("threshold", 0.1)),
            output_fps=int(payload.get("output_fps", 30)),
            debug=bool(payload.get("debug", False)),
            strategies=strategies,
        )


def load_config(path: str | Path) -> DedupeConfig:
    path = Path(path)
    if path.suffix.lower() in {".yaml", ".yml"}:
        return _load_yaml(path)
    if path.suffix.lower() == ".json":
        return _load_json(path)
    raise ValueError(f"Unsupported config format: {path.suffix}")


def _load_json(path: Path) -> DedupeConfig:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return DedupeConfig.from_dict(payload)


def _load_yaml(path: Path) -> DedupeConfig:
    spec = importlib.util.find_spec("yaml")
    if spec is None:
        raise RuntimeError("PyYAML is required to load YAML configs.")
    yaml = importlib.import_module("yaml")
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return DedupeConfig.from_dict(payload or {})
