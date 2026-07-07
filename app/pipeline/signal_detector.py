from dataclasses import dataclass

from app.pipeline.disproportionality import (
    ContingencyTable,
    DisproportionalityMetrics,
)


@dataclass(frozen=True)
class SignalDetectionConfig:
    """Transparent minimum-support and disproportionality thresholds."""

    min_case_count: int = 5
    min_prr: float = 2.0
    min_ror_ci_lower: float = 1.0
    max_signals: int = 10


@dataclass(frozen=True)
class SignalCandidate:
    """One report-level drug/event disproportionality result."""

    reaction: str
    case_count: int
    contingency_table: ContingencyTable
    metrics: DisproportionalityMetrics


@dataclass(frozen=True)
class DetectedSignal:
    """A candidate that passed every configured signal threshold."""

    reaction: str
    case_count: int
    contingency_table: ContingencyTable
    metrics: DisproportionalityMetrics
    passes_threshold: bool
    threshold_reasons: list[str]


def evaluate_candidate(
    candidate: SignalCandidate,
    config: SignalDetectionConfig,
) -> DetectedSignal:
    """Evaluate and explain every threshold for one candidate."""
    reasons = [
        (
            f"Case count {candidate.case_count} meets minimum {config.min_case_count}."
            if candidate.case_count >= config.min_case_count
            else f"Case count {candidate.case_count} is below minimum {config.min_case_count}."
        ),
        (
            f"PRR {candidate.metrics.prr:.2f} meets minimum {config.min_prr:.2f}."
            if candidate.metrics.prr >= config.min_prr
            else f"PRR {candidate.metrics.prr:.2f} is below minimum {config.min_prr:.2f}."
        ),
        (
            "ROR lower 95% confidence bound "
            f"{candidate.metrics.ror_ci_low:.2f} exceeds {config.min_ror_ci_lower:.2f}."
            if candidate.metrics.ror_ci_low > config.min_ror_ci_lower
            else "ROR lower 95% confidence bound "
            f"{candidate.metrics.ror_ci_low:.2f} does not exceed {config.min_ror_ci_lower:.2f}."
        ),
    ]
    passes = (
        candidate.case_count >= config.min_case_count
        and candidate.metrics.prr >= config.min_prr
        and candidate.metrics.ror_ci_low > config.min_ror_ci_lower
    )
    return DetectedSignal(
        reaction=candidate.reaction,
        case_count=candidate.case_count,
        contingency_table=candidate.contingency_table,
        metrics=candidate.metrics,
        passes_threshold=passes,
        threshold_reasons=reasons,
    )


def detect_signals(
    candidates: list[SignalCandidate],
    config: SignalDetectionConfig | None = None,
) -> list[DetectedSignal]:
    """Filter candidates and rank passing signals by conservative ROR evidence."""
    config = config or SignalDetectionConfig()
    evaluated = [evaluate_candidate(candidate, config) for candidate in candidates]
    passing = [item for item in evaluated if item.passes_threshold]
    passing.sort(
        key=lambda item: (item.metrics.ror_ci_low, item.case_count),
        reverse=True,
    )
    return passing[: config.max_signals]
