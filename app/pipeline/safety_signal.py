from dataclasses import dataclass

from app.pipeline.disproportionality import ContingencyTable
from app.pipeline.evidence_grader import EvidenceSummary
from app.pipeline.signal_detector import DetectedSignal


@dataclass(frozen=True)
class SafetySignal:
    """One PRR/ROR reporting signal plus retrieved PubMed evidence."""

    reaction: str
    case_count: int
    contingency_table: ContingencyTable
    prr: float
    prr_ci_low: float
    prr_ci_high: float
    ror: float
    ror_ci_low: float
    ror_ci_high: float
    continuity_corrected: bool
    passes_threshold: bool
    threshold_reasons: list[str]
    evidence: EvidenceSummary


def build_safety_signal(
    signal: DetectedSignal,
    evidence: EvidenceSummary,
) -> SafetySignal:
    """Combine deterministic FAERS metrics with bounded literature evidence."""
    metrics = signal.metrics
    return SafetySignal(
        reaction=signal.reaction,
        case_count=signal.case_count,
        contingency_table=signal.contingency_table,
        prr=metrics.prr,
        prr_ci_low=metrics.prr_ci_low,
        prr_ci_high=metrics.prr_ci_high,
        ror=metrics.ror,
        ror_ci_low=metrics.ror_ci_low,
        ror_ci_high=metrics.ror_ci_high,
        continuity_corrected=metrics.continuity_corrected,
        passes_threshold=signal.passes_threshold,
        threshold_reasons=signal.threshold_reasons,
        evidence=evidence,
    )
