from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, List, Optional

from .dedup import DedupHistory, DedupStrategy
from .stages import PipelineStage


@dataclass
class Pipeline:
    decoder: PipelineStage
    feature_extractor: PipelineStage
    dedup_strategy: DedupStrategy
    output: Optional[PipelineStage] = None
    history: DedupHistory = field(default_factory=list)

    def process(self, packet: Any) -> Optional[Any]:
        context: dict[str, Any] = {}
        decoded = self.decoder.process(packet, context)
        features = self.feature_extractor.process(decoded, context)
        if self.dedup_strategy.should_drop(features, self.history):
            return None
        self.history.append(features)
        if self.output is not None:
            return self.output.process(features, context)
        return features

    def run(self, packets: Iterable[Any]) -> List[Any]:
        results: List[Any] = []
        for packet in packets:
            output = self.process(packet)
            if output is not None:
                results.append(output)
        return results
