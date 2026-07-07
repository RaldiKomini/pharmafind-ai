import math

import pytest

from app.clients.pubmed_client import PubMedPaperSummary
from app.pipeline.disproportionality import (
    ContingencyTable,
    calculate_disproportionality,
)
from app.pipeline.evidence_grader import (
    EvidenceClaim,
    EvidenceSynthesis,
    validate_evidence_synthesis,
)
from app.pipeline.signal_detector import (
    SignalCandidate,
    SignalDetectionConfig,
    detect_signals,
    evaluate_candidate,
)


def test_prr_ror_and_confidence_intervals_match_known_table():
    table = ContingencyTable(
        drug_with_event=260,
        drug_without_event=20585,
        other_drugs_with_event=3126,
        other_drugs_without_event=1593460,
    )
    metrics = calculate_disproportionality(table)

    assert metrics.prr == pytest.approx(6.3705186516)
    assert metrics.prr_ci_low == pytest.approx(5.6176596420)
    assert metrics.prr_ci_high == pytest.approx(7.2242731807)
    assert metrics.ror == pytest.approx(6.4383512894)
    assert metrics.ror_ci_low == pytest.approx(5.6690513720)
    assert metrics.ror_ci_high == pytest.approx(7.3120465145)
    assert metrics.continuity_corrected is False


def test_zero_cell_uses_finite_continuity_corrected_estimates():
    metrics = calculate_disproportionality(ContingencyTable(5, 95, 0, 1000))

    assert metrics.continuity_corrected is True
    assert all(
        math.isfinite(value) and value > 0
        for value in (
            metrics.prr,
            metrics.prr_ci_low,
            metrics.prr_ci_high,
            metrics.ror,
            metrics.ror_ci_low,
            metrics.ror_ci_high,
        )
    )


@pytest.mark.parametrize(
    "cells",
    [(-1, 1, 1, 1), (0, 0, 1, 1), (1, 1, 0, 0)],
)
def test_invalid_contingency_tables_are_rejected(cells):
    with pytest.raises(ValueError):
        ContingencyTable(*cells)


def _candidate(reaction: str, cases: int, table: ContingencyTable) -> SignalCandidate:
    return SignalCandidate(
        reaction=reaction,
        case_count=cases,
        contingency_table=table,
        metrics=calculate_disproportionality(table),
    )


def test_signal_thresholds_are_explained_and_ranked_by_ror_lower_bound():
    strong = _candidate("strong", 8, ContingencyTable(8, 92, 10, 9890))
    moderate = _candidate("moderate", 20, ContingencyTable(20, 80, 200, 9700))
    too_few = _candidate("too few", 4, ContingencyTable(4, 96, 2, 9898))
    config = SignalDetectionConfig(
        min_case_count=5,
        min_prr=2.0,
        min_ror_ci_lower=1.0,
        max_signals=10,
    )

    signals = detect_signals([moderate, too_few, strong], config)

    assert [signal.reaction for signal in signals] == ["strong", "moderate"]
    failed = evaluate_candidate(too_few, config)
    assert failed.passes_threshold is False
    assert "below minimum" in failed.threshold_reasons[0]


def test_grounded_evidence_accepts_only_retrieved_pmids():
    papers = [
        PubMedPaperSummary(pmid="123", title="One", abstract="Evidence"),
        PubMedPaperSummary(pmid="456", title="Two", abstract="Evidence"),
    ]
    synthesis = EvidenceSynthesis(
        summary="The abstracts report mixed evidence.",
        overall_stance="mixed",
        claims=[EvidenceClaim(text="One study reports an association.", stance="supports", pmids=["123"])],
        limitations=["Abstract-only review."],
    )
    assert validate_evidence_synthesis(synthesis, papers) is synthesis

    invented = EvidenceSynthesis(
        summary="Invalid",
        overall_stance="supports",
        claims=[EvidenceClaim(text="Invented citation", stance="supports", pmids=["999"])],
        limitations=[],
    )
    with pytest.raises(ValueError, match="outside the retrieved set"):
        validate_evidence_synthesis(invented, papers)
