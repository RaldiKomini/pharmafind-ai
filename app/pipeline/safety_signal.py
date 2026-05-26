from dataclasses import dataclass

from app.pipeline.baseline_comparator import ReactionComparison
from app.pipeline.evidence_grader import EvidenceSummary


@dataclass(frozen=True)
class SafetySignal:
    reaction: str
    recent_count: int
    baseline_count: int
    recent_rate: float
    baseline_rate: float
    ratio: float
    signal_score: float
    evidence: EvidenceSummary


def build_safety_signal(
    comparison: ReactionComparison,
    evidence: EvidenceSummary,
) -> SafetySignal:
    return SafetySignal(
        reaction=comparison.reaction,
        recent_count=comparison.recent_count,
        baseline_count=comparison.baseline_count,
        recent_rate=comparison.recent_rate,
        baseline_rate=comparison.baseline_rate,
        ratio=comparison.ratio,
        signal_score=comparison.signal_score,
        evidence=evidence,
    )