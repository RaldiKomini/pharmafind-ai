from datetime import date

import pytest

from app.clients.pubmed_client import PubMedPaperSummary
from app.pipeline.baseline_comparator import compare_reaction_counts
from app.pipeline.date_filter import parse_faers_date, split_recent_and_baseline
from app.pipeline.evidence_grader import grade_pubmed_evidence
from app.pipeline.reaction_aggregator import aggregate_reactions, count_reactions
from app.pipeline.signal_detector import SignalDetectionConfig, detect_signals


def test_parse_faers_date_handles_valid_and_invalid_values():
    assert parse_faers_date("20260501") == date(2026, 5, 1)
    assert parse_faers_date("not-a-date") is None
    assert parse_faers_date("") is None


def test_split_recent_and_baseline_uses_non_overlapping_windows():
    reports = [
        {"receivedate": "20260420", "id": "recent"},
        {"receivedate": "20260201", "id": "baseline"},
        {"receivedate": "20250101", "id": "old"},
        {"receivedate": "bad", "id": "invalid"},
    ]

    recent, baseline = split_recent_and_baseline(
        reports,
        today=date(2026, 5, 1),
        recent_days=30,
        baseline_days=120,
    )

    assert [item["id"] for item in recent] == ["recent"]
    assert [item["id"] for item in baseline] == ["baseline"]


def test_reaction_aggregation_counts_and_orders_terms():
    terms = ["nausea", "headache", "nausea", "fatigue", "nausea"]

    assert count_reactions(terms) == {"nausea": 3, "headache": 1, "fatigue": 1}
    assert aggregate_reactions(terms, top_k=1) == [("nausea", 3)]


def test_signal_detection_filters_low_support_and_ranks_scores():
    comparisons = compare_reaction_counts(
        recent_counts={"nausea": 20, "headache": 3, "rare": 8},
        baseline_counts={"nausea": 5, "headache": 3, "rare": 0},
        total_recent_reports=100,
        total_baseline_reports=100,
    )

    signals = detect_signals(
        comparisons,
        SignalDetectionConfig(
            min_recent_count=5,
            min_baseline_count=3,
            min_ratio=2.0,
            max_signals=10,
        ),
    )

    assert [item.reaction for item in signals] == ["nausea"]
    assert signals[0].ratio == pytest.approx(4.0)
    assert signals[0].signal_score > 0


def test_pubmed_evidence_grading_thresholds():
    papers = [
        PubMedPaperSummary(
            pmid=str(index),
            title=f"Paper {index}",
            source="Test",
            pub_date="2026",
        )
        for index in range(6)
    ]

    assert grade_pubmed_evidence([]).evidence_grade == "none"
    assert grade_pubmed_evidence(papers[:2]).evidence_grade == "weak"
    assert grade_pubmed_evidence(papers[:5]).evidence_grade == "moderate"
    assert grade_pubmed_evidence(papers).evidence_grade == "strong"
