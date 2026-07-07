from dataclasses import dataclass
from datetime import date, timedelta

from app.clients.faers_client import (
    OPENFDA_MAX_COUNT_TERMS,
    FaersClient,
    build_date_search,
    build_drug_search,
    build_reaction_search,
)
from app.pipeline.disproportionality import (
    ContingencyTable,
    calculate_disproportionality,
)
from app.pipeline.signal_detector import (
    DetectedSignal,
    SignalCandidate,
    SignalDetectionConfig,
    detect_signals,
)


REACTION_COUNT_FIELD = "patient.reaction.reactionmeddrapt.exact"


@dataclass(frozen=True)
class FaersSignalReviewConfig:
    """Configuration for one complete-window openFDA count analysis."""

    drug_name: str
    analysis_days: int = 365
    min_case_count: int = 5
    min_prr: float = 2.0
    min_ror_ci_lower: float = 1.0
    max_signals: int = 10


@dataclass(frozen=True)
class FaersSignalReviewResult:
    """FAERS-only result before PubMed evidence is attached."""

    drug_name: str
    analysis_start: date
    analysis_end: date
    total_report_count: int
    drug_report_count: int
    signals: list[DetectedSignal]


def _join_search(*parts: str) -> str:
    return " AND ".join(part for part in parts if part)


def _build_candidate(
    reaction: str,
    drug_event_count: int,
    drug_report_count: int,
    event_report_count: int,
    total_report_count: int,
) -> SignalCandidate:
    a = drug_event_count
    b = drug_report_count - a
    c = event_report_count - a
    d = total_report_count - drug_report_count - event_report_count + a
    table = ContingencyTable(
        drug_with_event=a,
        drug_without_event=b,
        other_drugs_with_event=c,
        other_drugs_without_event=d,
    )
    return SignalCandidate(
        reaction=reaction.strip().lower(),
        case_count=a,
        contingency_table=table,
        metrics=calculate_disproportionality(table),
    )


def run_faers_signal_review(
    config: FaersSignalReviewConfig,
    client: FaersClient | None = None,
    analysis_end: date | None = None,
) -> FaersSignalReviewResult:
    """Calculate complete-window PRR/ROR signals from openFDA count queries."""
    if config.analysis_days < 1:
        raise ValueError("analysis_days must be at least 1")

    client = client or FaersClient()
    analysis_end = analysis_end or client.fetch_latest_received_date()
    analysis_start = analysis_end - timedelta(days=config.analysis_days - 1)
    date_search = build_date_search(analysis_start, analysis_end)
    drug_search = build_drug_search(config.drug_name)
    date_and_drug_search = _join_search(date_search, drug_search)

    total_report_count = client.count_reports(date_search)
    drug_report_count = client.count_reports(date_and_drug_search)
    if total_report_count == 0:
        raise ValueError("No FAERS reports were available in the selected analysis window")
    if drug_report_count == 0:
        return FaersSignalReviewResult(
            drug_name=config.drug_name,
            analysis_start=analysis_start,
            analysis_end=analysis_end,
            total_report_count=total_report_count,
            drug_report_count=0,
            signals=[],
        )

    drug_event_counts = client.count_terms(
        search=date_and_drug_search,
        field=REACTION_COUNT_FIELD,
        limit=OPENFDA_MAX_COUNT_TERMS,
    )
    eligible_counts = [
        item for item in drug_event_counts if item.count >= config.min_case_count
    ]

    global_counts = client.count_terms(
        search=date_search,
        field=REACTION_COUNT_FIELD,
        limit=OPENFDA_MAX_COUNT_TERMS,
    )
    global_count_by_term = {item.term.upper(): item.count for item in global_counts}

    candidates: list[SignalCandidate] = []
    for item in eligible_counts:
        reaction = item.term.upper()
        event_report_count = global_count_by_term.get(reaction)
        if event_report_count is None:
            event_report_count = client.count_reports(
                _join_search(date_search, build_reaction_search(reaction))
            )

        # Aggregation and exact-search counts should obey set inclusion. Skip a
        # malformed upstream result rather than emitting an invalid 2x2 table.
        if event_report_count < item.count:
            continue
        try:
            candidates.append(
                _build_candidate(
                    reaction=reaction,
                    drug_event_count=item.count,
                    drug_report_count=drug_report_count,
                    event_report_count=event_report_count,
                    total_report_count=total_report_count,
                )
            )
        except ValueError:
            continue

    signals = detect_signals(
        candidates,
        SignalDetectionConfig(
            min_case_count=config.min_case_count,
            min_prr=config.min_prr,
            min_ror_ci_lower=config.min_ror_ci_lower,
            max_signals=config.max_signals,
        ),
    )
    return FaersSignalReviewResult(
        drug_name=config.drug_name,
        analysis_start=analysis_start,
        analysis_end=analysis_end,
        total_report_count=total_report_count,
        drug_report_count=drug_report_count,
        signals=signals,
    )
