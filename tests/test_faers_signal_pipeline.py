from datetime import date

from app.clients.faers_client import FaersTermCount
from app.pipeline.faers_signal_pipeline import (
    FaersSignalReviewConfig,
    run_faers_signal_review,
)


class FakeFaersClient:
    def __init__(self):
        self.missing_event_queries: list[str] = []

    def fetch_latest_received_date(self):
        return date(2026, 4, 28)

    def count_reports(self, search: str):
        if "patient.reaction" in search:
            self.missing_event_queries.append(search)
            return 10
        if "patient.drug" in search:
            return 100
        return 10000

    def count_terms(self, search: str, field: str, limit: int):
        if "patient.drug" in search:
            return [
                FaersTermCount("EVENT A", 10),
                FaersTermCount("EVENT B", 4),
                FaersTermCount("EVENT C", 6),
            ]
        return [FaersTermCount("EVENT A", 100)]


def test_faers_pipeline_uses_complete_counts_and_fetches_missing_background_term():
    client = FakeFaersClient()
    result = run_faers_signal_review(
        FaersSignalReviewConfig(
            drug_name="Example",
            analysis_days=365,
            min_case_count=5,
            min_prr=2,
            min_ror_ci_lower=1,
            max_signals=10,
        ),
        client=client,
    )

    assert result.analysis_start == date(2025, 4, 29)
    assert result.analysis_end == date(2026, 4, 28)
    assert result.total_report_count == 10000
    assert result.drug_report_count == 100
    assert {signal.reaction for signal in result.signals} == {"event a", "event c"}
    event_a = next(signal for signal in result.signals if signal.reaction == "event a")
    assert event_a.contingency_table.drug_with_event == 10
    assert event_a.contingency_table.drug_without_event == 90
    assert event_a.contingency_table.other_drugs_with_event == 90
    assert event_a.contingency_table.other_drugs_without_event == 9810
    assert len(client.missing_event_queries) == 1
    assert "EVENT C" in client.missing_event_queries[0]
